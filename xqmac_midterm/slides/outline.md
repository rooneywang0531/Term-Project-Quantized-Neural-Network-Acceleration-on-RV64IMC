# 5–6 minute midterm presentation outline

This is an outline, not the final slides. Prepare a 6-slide PDF/PPTX and use results from one compiler consistently. Target total: **5 min 30 sec**.

| Slide | Time | Content / evidence |
|---|---:|---|
| 1. Goal and workload | 40 s | Static INT8 ResNet-18; RV64IMC; no target FP; useful model MACs and 37 operators; evaluation goal is ISA instructions, not PPA |
| 2. Reference and baseline analysis | 60 s | TFLite → Python export/reference → independent C → ELF → Spike; all intermediate tensors checked; B0 instruction mix and three measured bottlenecks |
| 3. ISA design and verification | 60 s | SS/US four-lane signedness and INT32 accumulation; DR versus SR rounding; alias/x0, directed/random vectors and illegal encodings; refer to ISA table |
| 4. Fair configurations and v2 | 50 s | B0, B1, X1_MAC, final X1_RQ; runtime packing included; original data; RGB v2 removes repeated reconstruction stores without adding an instruction |
| 5. Quantitative results | 80 s | FC microbenchmark ≥2× instruction reduction; two Conv operators + complete block correctness; full-model four-way instruction/code/memory table; custom utilization and coverage; no cycle-speedup claim |
| 6. Reproduction and conclusion | 40 s | Pinned toolchain/Spike; `reproduce.sh quick/full`; tested fixture coverage; GitHub URL and commit; limitations and next steps within course scope |

Minimum figures/tables: one small pipeline illustration, one instruction-mix chart, one four-configuration result table. Use the FC table from README and the freshly reproduced full-model table from `results/reference/`; label compiler, scope and input. A 4.100× FC instruction ratio is not a 4.100× cycle speedup.

Before submission, replace placeholders for team members/GitHub/commit and link the actual slide PDF/PPTX from README. Do not imply that RTL or PPA remains a midterm requirement; the supplied hand-in instructions explicitly exclude it.
