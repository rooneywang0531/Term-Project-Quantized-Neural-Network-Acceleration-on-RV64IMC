# fc four-configuration comparison

Sum inside selected operator symbols, including prologue/return, runtime packing, correction, tails, spills and rounding. Excludes startup, fixture setup, dispatch and golden checks. Not whole-ELF instructions or cycles.

| Metric | B0 | B1 | X1_MAC | X1_RQ |
|---|---:|---:|---:|---:|
| dynamic_instructions | 4118027 | 2169047 | 532049 | 529049 |
| operator_code_bytes | 190 | 712 | 492 | 452 |
| dynamic_memory_instructions | 1028006 | 807027 | 164524 | 164024 |
| custom_dynamic_total | 0 | 0 | 128000 | 129000 |
| custom_instruction_utilization | 0.0 | 0.0 | 0.24057934513550444 | 0.24383374696861726 |
| dense_mac_per_instruction | 0.12433138490835538 | 0.2360483659413558 | 0.9623173805420178 | 0.9677742515343569 |
| executed_mac_per_instruction | 0.12433138490835538 | 0.2360483659413558 | 0.9623173805420178 | 0.9677742515343569 |
| mac_coverage_by_custom_instructions | 0.0 | 0.0 | 1.0 | 1.0 |
| branch_jump | 515001 | 34251 | 34251 | 34251 |
| custom_mac | 0 | 0 | 128000 | 128000 |
| custom_requant | 0 | 0 | 0 | 1000 |
| integer_alu | 2062020 | 814769 | 204274 | 201774 |
| load | 1027003 | 740762 | 163262 | 163012 |
| multiply | 513000 | 513000 | 1000 | 0 |
| store | 1003 | 66265 | 1262 | 1012 |

| Operator | B0 | B1 | X1_MAC | X1_RQ |
|---|---:|---:|---:|---:|
| op_36_fully_connected | 4118027 | 2169047 | 532049 | 529049 |

B1 / X1_RQ instruction-count ratio: 4.100x.
Not a cycle or wall-time speedup. No CV-Wally/PPA claim.
FC microbenchmark: 512 inputs, 1000 outputs, 512000 model MACs. >=2x dynamic-instruction target: PASS
