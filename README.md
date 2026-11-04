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

## Supported environment

Recommended native host: **Linux x86_64, Debian 12 or Ubuntu 24.04 / WSL2 Ubuntu 24.04**. The pinned binary compiler needs glibc >= 2.36. Windows/macOS can use Linux containers below. Apple Silicon requires `--platform linux/amd64` emulation and may be slower.

Internet is needed once to install/build tools. Model, constants and reference fixtures are included, so benchmark execution needs neither internet nor Python ML packages. Allow several GB for Spike build files; the first build and full scalar simulations can take many minutes. Each simulation has a default 7,200-second timeout, adjustable with `TIMEOUT_SEC`.

### Native setup

Run from this repository's top-level directory:

```bash
sudo apt-get update
sudo apt-get install -y build-essential git python3 ca-certificates \
  device-tree-compiler libboost-regex-dev libboost-system-dev \
  libgmp10 libisl23 libmpc3 libmpfr6 libzstd1 zlib1g
python3 scripts/install_toolchain.py
bash scripts/bootstrap_spike.sh
source env.sh
```

The installer extracts checksum-pinned Debian GCC 12.2.0/binutils 2.40 into `.tools/cross/`; it does not install a target libc and none is needed. Spike source is fetched at the exact commit in `tools.lock.json` and built locally. The extension is built against that same checkout's headers. `env.sh` must be sourced in each new Bash shell.

### Existing university workstation tools

The existing EL8 workstation can use its already working GCC 16 / Spike instead of installing the Debian binaries. From a fresh copy of this submission, in Bash:

```bash
source "$HOME/riscv_project/env.sh"
export SPIKE_SRC="$HOME/riscv_project/src/riscv-isa-sim"
export SPIKE_BUILD="$SPIKE_SRC/build"
export SPIKE_BIN="$HOME/riscv_project/tools/bin/spike"
source ./env.sh
bash scripts/reproduce.sh quick
bash scripts/reproduce.sh full
```

This compatibility route rebuilds and retests the plugin using the workstation's own headers and records its compiler/binary hashes. It is not the pinned GCC-12 reference environment, so compare configurations within that run. Do not install the Debian pinned cross binaries on EL8. Use a fresh submission checkout without `.tools/cross/` to prevent that compiler taking priority over the existing workstation compiler.

### Container setup (alternative)

```bash
docker build --platform linux/amd64 -t xqmac-midterm .
docker run --rm --platform linux/amd64 -v "$PWD":/work \
  xqmac-midterm bash scripts/reproduce.sh quick
docker run --rm --platform linux/amd64 -v "$PWD":/work \
  xqmac-midterm bash scripts/reproduce.sh full
```

The image contains tools built from the same lock file. The mounted checkout supplies sources/model data and receives results. The supplied Dockerfile has not been built in the preparation environment; the native Linux route and repository relocation are the tested paths. Tool versions are pinned, but the Debian base image and host development packages are not a complete OS snapshot.

## Reproduce

```bash
source env.sh
bash scripts/reproduce.sh quick
bash scripts/reproduce.sh full
# Or run both with one unit-test build:
bash scripts/reproduce.sh all
```

`quick` runs the profiler checks, all instruction semantic tests, the **512→1000 FC microbenchmark in all four configurations**, and **the complete first residual block with final X1** (two 3×3 Conv operators + residual ADD). It covers the required microbenchmark, two major operators and one complete CNN block.

`full` runs the instruction tests, all **37 operators** for random input in all four configurations, their comparison, and final X1 full inference for the real-zero and maximum fixtures. Every C operator output is compared exactly with the saved LiteRT `BUILTIN_REF` result, including all 1000 final logits. No layer is fed golden outputs during full inference.

For a single run after the instruction tests:

```bash
python3 scripts/run_unit.py
python3 scripts/benchmark.py --scope block --config X1_RQ --case 0
python3 scripts/benchmark.py --scope full --config X1_RQ --case 1
# Other options: --scope fc|block|full; --config B0|B1|X1_MAC|X1_RQ; --case 0|1|2
```

To compare all four block configurations, run `benchmark.py --scope block` once for each configuration, then `python3 scripts/compare.py block`. Comparison scripts reject mismatched compiler versions/flags, data, harnesses or Spike binaries.

### Output locations

| Output | Path |
|---|---|
| Semantic test results / source and binary hashes | `results/unit/unit_metrics.json`, `unit_pass.json` |
| Dynamic instructions, mix, memory, MAC rates, utilization | `results/<scope>_<config>_<case>/metrics.json` |
| Per-operator contribution | Same directory: `operators.csv` |
| ELF section sizes | Same directory: `sections.txt` |
| Compiler command and provenance | Same directory: `build_command.json`, `run.json` |
| Four-way comparison | `results/comparison_<scope>_<case>.md` |
| ELF / disassembly / PC histogram / stack-usage report | `build/<scope>_<config>_<case>/` |

Silence while Spike runs is normal. `PASS` requires a successful target exit plus a complete, valid histogram and exact custom-instruction counts. A nonzero exit stops the script; **124 means timeout**, not a correct result. A target mismatch exits with operator index + 1; inspect `first_bad_*` in the harness when debugging.

## Expected measurements

The numbers below use the pinned GCC 12.2.0 compiler. These are **dynamic operator instructions**, not cycles or whole-ELF instruction counts.

| FC microbenchmark, random case | B0 | B1 | X1_MAC | Final X1_RQ |
|---|---:|---:|---:|---:|
| Instructions | 4,118,027 | 2,169,047 | 532,049 | 529,049 |
| Operator code bytes | 190 | 712 | 492 | 452 |
| Load + store instructions | 1,028,006 | 807,027 | 164,524 | 164,024 |

The FC has **512,000 MACs** and 1000 checked outputs. B1 / final X1 = **4.100× fewer dynamic instructions**, satisfying the project's ≥2× major FC/GEMM instruction-count target. Final FC X1 executes exactly **128,000 `qmac4.us` + 1,000 `qrequant.sr`**. This is an instruction-count result, not a cycle speedup.

Final X1 first residual block (random): **210,133,167 instructions**, all 602,112 output values match; exactly **56,434,688 `qmac4.us` + 1,003,520 `qrequant.dr`**.

| Full model, random, GCC 12.2.0 | B0 | B1 | X1_MAC v2 | Final X1_RQ v2 |
|---|---:|---:|---:|---:|
| Operator instructions | 14,295,056,770 | 7,087,829,490 | 1,732,987,620 | 1,664,344,410 |
| Operator code bytes | 12,632 | 26,170 | 21,806 | 15,154 |
| Load + store instructions | 3,457,692,900 | 2,499,250,557 | 568,449,945 | 566,635,647 |

All 37 operator outputs match exactly. B1 / final X1 operator instruction ratio is **4.259×**. Full-model tables and compiler-specific references are in `results/reference/` and `docs/MEASUREMENTS.md`. Earlier workstation results used GCC 16.1.0 and therefore differ. Never mix a GCC-16 baseline with GCC-12 X1 to compute an improvement. Model output equality and exact custom counts are mandatory; scalar instruction totals are compiler/version dependent.

## Model export and reference generation (optional audit)

The normal TA benchmark does **not** re-export the model. Checked-in generated files have SHA-256 guards. To audit how the Python LiteRT reference becomes C constants/graph wrappers:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r model/requirements-export.lock.txt
bash scripts/reexport.sh
```

Use a Python version supported by the pinned LiteRT/NumPy wheels (Python 3.12 was used for the original export and the successful re-export audit). `requirements-export.txt` records the original four direct dependencies; `.lock.txt` also pins the transitives used in this audit. Export writes into `build/reexport/` and compares every exporter output hash; committed benchmark assets remain unchanged. The original static INT8 `.tflite` is included and checked against its pinned SHA-256.

On Debian/Ubuntu, the optional export path may also need the `python3-venv` package.

Python loads the model with LiteRT `BUILTIN_REF`, exports weights/biases/integer quantization parameters and static operator calls, and records all intermediate reference tensors for three synthetic inputs. C independently implements the integer operators. The RISC-V compiler converts C + startup assembly into a bare-metal ELF; Spike executes the ELF. These fixtures test numerical equivalence, not ImageNet classification accuracy. See [model provenance](model/NOTICE.md).

## Measurement boundaries and troubleshooting

Measured scope is the sum of the selected operator function symbols, including prologue/return, runtime packing, packed loads/XOR, loops, spills and requantization. Startup, dispatch, fixture copy and golden comparisons are excluded. FC/block isolated inputs are saved reference boundary activations; full-model consumer inputs always come from actual C producer outputs.

For completeness, metrics also provide `histogram_total_instructions` (all Spike PCs, including startup and golden checks) and `outside_operator_instructions`. Use the scoped `dynamic_instructions` for model comparisons; the all-PC total includes evaluation overhead.

The profiler rejects floating-point instructions in measured operators, unknown opcodes, incomplete histograms, out-of-scope helpers and custom encoding/count errors. Memory instruction counts do not establish byte traffic, cache misses, stalls or hardware latency.

If a native sanitizer probe cannot link (e.g. missing `libubsan`), unit tests explicitly fall back to the mandatory native numerical cross-check and print that UBSan was unavailable. Actual numerical test failures never fall back. A missing `libmpc.so.3` means the host compiler dependencies above are incomplete; do not invent library symlinks. If Spike or plugin sources change, rerun `scripts/run_unit.py` before benchmarking. A failed hash/alignment check must be resolved, not bypassed.

This is a single standalone checkout: it does not require any prior `riscv_project/tests/...` folders or prebuilt `.so` files. Build artifacts, downloaded tools and local results are ignored by Git; reference measurements and original model assets are included.
