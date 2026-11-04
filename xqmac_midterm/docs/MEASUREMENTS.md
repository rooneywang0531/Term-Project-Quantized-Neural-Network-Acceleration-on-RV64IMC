# Measurement definitions and evidence

## Scope

`dynamic_instructions` is the sum of histogram weights of instructions inside the selected operator symbols. It includes prologue/return, address arithmetic, all runtime input/weight packing, zero-point correction, loops, scalar tails, spills and requantization. It excludes startup, dispatch, fixture copies and golden comparisons. A full-model report sums all 37 operators; this is not a count of every retired instruction from ELF entry to termination.

The histogram is collected using Spike `-g`. Static disassembly supplies encoding and function-boundary information. A static instruction appearing once is counted as many times as its PC executes. Custom instructions are decoded from their bit encodings, not guessed from objdump text. Measured helper calls outside selected regions are rejected to prevent under-counting.

| Required measurement | Definition / artifact |
|---|---|
| Dynamic instruction count | `metrics.json: dynamic_instructions` |
| All-PC total including verification | `histogram_total_instructions`; excluded overhead separately in `outside_operator_instructions` |
| Instruction mix | `instruction_mix`: load, store, integer_alu, multiply, branch_jump, custom_mac, custom_requant |
| Dynamic memory instructions | load + store; `dynamic_memory_instructions` |
| MAC per retired instruction | Both `dense_mac_per_instruction` and `executed_mac_per_instruction` |
| Major-operator contribution | `operators.csv`, per-op counts and instruction share |
| Code size | Sum of selected operator symbol bytes + ELF sections in `sections.txt`; these are different quantities |
| Custom utilization | Dynamic custom instructions / measured instructions; also report custom MAC coverage |

Branch/jump/return are grouped as `branch_jump`. Double-precision/integer register instructions must be decoded by actual ISA type; integer `mul` used in scalar requantization is not a model MAC. The disassembly guard rejects floating-point instructions in measured operators.

## Dense versus executed MACs

Dense model MACs count all nominal convolution products, including positions with implicit SAME-padding zeros. Executed MACs count products actually performed after the C kernels skip those out-of-range taps. Explicit PAD tensors remain real operator inputs, so their products are included. Counts are identical across configurations:

| Scope | Dense MACs | Executed model MACs |
|---|---:|---:|
| FC microbenchmark | 512,000 | 512,000 |
| First residual block | 231,211,008 | 225,738,752 |
| Full model | 1,814,073,344 | 1,691,652,096 |

`qmac4` performs four logical model MACs. Full-model custom MAC counts are exactly 28,098,560 SS and 393,409,536 US: 1,686,032,384 MACs, covering 99.6678% of executed model MACs. The remaining 5,619,712 are scalar RGB-tail MACs. Final X1 additionally executes exactly 4,741,632 DR and 1,000 SR instructions. SS/US lanes, zero points, rounding, clamping and tails preserve the reference result.

## What changed in RGB v2

The initial RGB input has only three channels. A direct output-channel-tiled implementation repeatedly reconstructed packed bytes, creating excessive stack store instructions. v2 packs each kernel's 7 rows into groups of four plus a scalar tail, and constructs each spatial input patch once for reuse across output-channel tiles. All preparation is runtime code inside op02, not excluded preprocessing. The declared scratch data totals 9,811 bytes; actual compiler frame size is recorded by `.su` and depends on the compiler.

Report final X1 with v2. Keep the v1→v2 ablation as a software implementation improvement; it adds no ISA operation. B1→X1 also includes packed-load/loop changes needed to use the ISA, and should not be described as an isolated hardware MAC latency benefit. MAC-only→MAC+RQ uses the same v2 source with one feature define and isolates the incremental instruction-count effect at operator scope, including compiler allocation changes.

## Earlier workstation results (GCC 16.1.0)

These are previously supplied workstation measurements, retained separately from newly reproduced GCC-12 results. Earlier FC numbers were collected in the full-model operator context; the new FC microbenchmark has an independent harness and can differ.

| Full model, random | B0 | B1 | X1_MAC v2 | X1_RQ v2 |
|---|---:|---:|---:|---:|
| Operator instructions | 14,341,261,830 | 6,752,583,412 | 1,784,388,394 | 1,717,141,906 |
| Operator code bytes | 12,182 | 24,410 | 20,874 | 14,808 |

Final X1 full-model real-zero and maximum counts were 1,715,832,104 and 1,715,907,049, respectively, with exact outputs. Input-dependent scalar rounding/activation paths can change instruction totals even when custom MAC counts are fixed.

The workstation B1/final-X1 full-operator instruction ratio is 3.932×; B0/final-X1 is 8.352×. These are not end-to-end time speedups. The separate pinned-toolchain FC microbenchmark in README establishes the allowed ≥2× major FC instruction-reduction target without requiring cycle measurements.

## Three baseline bottlenecks supported by counts

1. **Scalar integer MAC implementation cost.** Full baseline executes roughly 1.69 billion scalar multiply instructions alongside loads/addressing/accumulation. Packed instructions collapse four useful MACs into one; qmac coverage and unchanged model MAC counts verify the amount of useful work.
2. **Address arithmetic and loop/control overhead.** Baseline full mix is 51.45% integer ALU and 12.55% branch/jump. B1 input reuse and unrolling substantially reduce these categories, establishing that part of the baseline overhead is removable in software. Aggregate ALU counts alone cannot attribute every instruction to requantization versus addresses; use per-op disassembly for that distinction.
3. **Scalar operand load/store instruction overhead.** Baseline full mix is 23.93% loads plus 0.25% stores. Packed operand loads and reuse reduce dynamic memory instruction count. v1's RGB stack stores were a separate implementation bottleneck corrected by v2.

Requantization is an additional measured opportunity, especially for residual ADD, where three requantizations are needed per output. MAC+RQ preserves double rounding for Conv/ADD and the original single rounding for FC. None of these counts establish cache misses, load-use stalls, memory bandwidth saturation, RF latency or clock frequency; those are unmeasured hardware properties.

## Correctness versus accuracy

All three fixtures are synthetic and deterministic, with every intermediate INT8 output checked against LiteRT BUILTIN_REF. This establishes exact numerical agreement for the tested inputs, not a measured ImageNet accuracy result or exhaustive model correctness proof. Instruction semantic tests separately exercise edge cases and seeded randomized vectors.
