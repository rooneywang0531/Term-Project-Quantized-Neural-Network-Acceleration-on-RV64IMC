# Term Project: Quantized ResNet-18 Acceleration on RV64IMC

Bare-metal C inference on RV64IMC, evaluated with Spike. Final **X1 is packed MAC + requantization**. No RTL, CV-Wally, PPA or cycle-speedup claim is part of this submission.

## Submission contents

| Required item | Files |
|---|---|
| Bare-metal C workload | `workload/`: `model.c, model_block.c, model_fc.c` 分別為 full model, first residual block, FC layer of ResNet-18。`kernels_b0.c, kernels_b1.c, kernels_x1.c` 分別選擇要進行 b0, b1, x1 哪個版本的運算。`start.S` 負責 bare-metal 啟動、呼叫 main()、通知 Spike 結束，`link.ld` 負責安排程式、資料、activation 和 stack 的記憶體位置，`host_main.c` 負責在一般電腦讀取 fixture、呼叫模型並印出結果 |
| Quantized model / Python scripts | `model/`: `model/resnet18_int8_channelwise.tflite` 為原始量化模型， `model/export_model.py` 解析模型，匯出權重、bias、整數量化參數與靜態計算圖，並使用 LiteRT BUILTIN_REF 產生三組測試輸入及各層參考輸出，匯出結果已附於 `model/assets/`，供 C 程式編譯與逐層比對使用 |
| Spike/custom ISA implementation | `docs/ISA.md` 定義四條自訂指令的編碼、運算語意與例外行為。 `isa/`: `isa/spike_extension.cc` 將指令註冊至 Spike，並使用 xqmac_semantics.h、`rq_semantics.h` 實作其運算。C kernels 透過 isa_ops.h 與 instruction wrappers 發出自訂指令。`build_extension.py` 使用相符的 Spike headers 建立 plugin，由驗證與 benchmark 腳本自動載入 |
| Short instruction verification | `tests/mac/` 驗證 packed MAC，`tests/instructions/` 驗證 double/single-rounding requantization，包含定向與隨機向量、邊界值、暫存器重疊、x0 和非法指令測試。執行 `python3 scripts/run_unit.py` 可自動建立 plugin 並完成全部驗證，結果輸出至 `results/unit/` |
| Reproducible benchmarks | `scripts/reproduce.sh` 提供完整重現入口，自動執行驗證與 benchmark。`benchmark.py` 編譯指定版本並在 Spike 執行，透過 PC histogram profiler 統計各 operator 的動態指令數、指令組成、程式大小與自訂指令使用率。`compare.py` 檢查測試條件一致後，產生 B0、B1、X1_MAC、X1_RQ 比較表。測量結果輸出至 `results/`，編譯產物與 histogram 保存於 `build/` |


## Configurations

| Name | ISA | Implementation |
|---|---|---|
| B0 | Original RV64IMC | Scalar baseline |
| B1 | Original RV64IMC | Software-optimized, including tiling, input reuse and unrolling |
| X1_MAC | RV64IMC + Xqmac | four-lane INT8 MAC; scalar rounding |
| X1_MAC_RQ | RV64IMC + Xqmac + requantization | Same v2 kernel + `qrequant.dr` and FC `qrequant.sr`; **final X1** |

All configurations use identical original model constants and fixtures. No offline packed-weight replacement is supplied. Runtime X1 packing, correction and scalar tails are counted inside the operator.

## Reproduce process

我是用清大電機的工作站架設環境並執行程式，如果要得到程式執行的結果，助教可以直接進入我的工作站，帳號：m115061579、密碼1988viva，進入後直接在/home/m115/m115061579/這個資料夾上傳github上面的xqmac_midterm.zip，接著依序按照以下指令輸入：

```bash
ssh -X ws26
bash
cd "$HOME/midterm_reproduce"

python3 -m zipfile -e "$HOME/xqmac_midterm.zip" .
cd xqmac_midterm

source "$HOME/riscv_project/env.sh"

export SPIKE_SRC="$HOME/riscv_project/src/riscv-isa-sim"
export SPIKE_BUILD="$SPIKE_SRC/build"
export SPIKE_BIN="$HOME/riscv_project/tools/bin/spike"

source ./env.sh

bash scripts/reproduce.sh quick
bash scripts/reproduce.sh full
```
`quick` runs the profiler checks, all instruction semantic tests, the **512→1000 FC microbenchmark in all four configurations**, and **the complete first residual block with final X1** (two 3×3 Conv operators + residual ADD). It covers the required microbenchmark, two major operators and one complete CNN block.

`full` runs the instruction tests, all **37 operators** for random input in all four configurations, their comparison, and final X1 full inference for the real-zero and maximum fixtures. Every C operator output is compared exactly with the saved LiteRT `BUILTIN_REF` result, including all 1000 final logits. No layer is fed golden outputs during full inference.

接著就可以看到 B0, B1, X1_MAC, X1_MAC_RQ 的每層輸出結果是否正確，以及它們之間的 instruction 統計資料等，用下面的指令可以查看統計比較表
```bash
cat results/comparison_full_random.md
```

### Output locations

| Output | Path |
|---|---|
| Instruction verification results | `results/unit/unit_metrics.json` |
| Four-configuration comparison | `results/comparison_fc_random.md`, `results/comparison_full_random.md` |
| Detailed metrics and per-operator results | `results/<scope>_<config>_<case>/metrics.json`, `operators.csv` |

These files are generated when the scripts run. All tests should report PASS, and the script should exit with status 0. Silence during Spike simulation is normal. Exit status 124 indicates a timeout.

## Expected measurements

These are **dynamic operator instructions**, not cycles or whole-ELF instruction counts.
Include FC layer and full model as below

| FC microbenchmark, random case | B0 | B1 | X1_MAC | Final X1_RQ |
|---|---:|---:|---:|---:|
| Instructions | 4,119,026 | 2,003,543 | 434,284 | 432,278 |
| Operator code bytes | 188 | 632 | 430 | 386 |
| Load + store instructions | 1,028,006 | 644,524 | 164,012 | 164,008 |

The FC microbenchmark performs 512,000 MACs, and all 1,000 outputs match the LiteRT reference. Dynamic instructions decrease from 2,003,543 (B1) to 432,278 (final X1), giving a 4.635× instruction-count ratio and satisfying the project’s ≥2× major FC/GEMM instruction-reduction target. Final FC X1 executes exactly 128,000 qmac4.us and 1,000 qrequant.sr instructions. This is an instruction-count improvement, not a cycle speedup.

| Full model, random | B0 | B1 | X1_MAC | Final X1_RQ |
|---|---:|---:|---:|---:|
| Operator instructions | 14,341,261,830 | 6,752,583,412 | 1,784,388,394 | 1,717,141,906 |
| Operator code bytes | 12,182 | 24,410 | 20,874 | 14,808 |
| Load + store instructions | 3,467,316,966 | 2,161,059,297 | 567,480,222 | 566,481,064 |

All outputs of all 37 operators, including the 1,000 final logits, match the LiteRT reference exactly. Operator instructions decrease from 6,752,583,412 (B1) to 1,717,141,906 (final X1), giving a 3.932× instruction-count ratio, or a 74.57% reduction. This is an instruction-count improvement, not a cycle speedup. Comparisons must use the same compiler and build settings; instruction totals and code size may differ across toolchains.

其餘資訊在報告簡報裡說明
