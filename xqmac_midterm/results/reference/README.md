# Reference results (evidence, not test inputs)

`pinned_gcc12/` contains newly rerun benchmark metrics, per-operator CSVs, ELF section sizes, comparisons and console records. Paths in provenance records are normalized to `<repo>` for readability. The scripts never use these files as proof of a new run: they rebuild under `build/` and write fresh `results/<scope>_<config>_<case>/` outputs.

`workstation_gcc16/summary.json` preserves the earlier user-supplied workstation totals. They use a different compiler and must not be combined with GCC-12 counts in a ratio.

| Pinned GCC 12.2, final X1 | Operator instructions | Correctness |
|---|---:|---|
| FC random | 529,049 | All 1000 outputs match |
| First residual block random | 210,133,167 | All three stages match (602,112 values) |
| Full model random | 1,664,344,410 | All 37 operators and 1000 logits match |
| Full model real-zero | 1,662,619,345 | All 37 operators and 1000 logits match |
| Full model maximum | 1,662,734,374 | All 37 operators and 1000 logits match |

The full-model random four-way table is in `pinned_gcc12/comparison_full_random.md`; the FC table is in `comparison_fc_random.md`. Detailed metrics also report the complete Spike histogram total including startup and validation overhead, separate from operator totals used for comparison.

`validation.json` records which paths were exercised. Docker is supplied as an alternative environment definition and was not run here. The native reference-export audit regenerated all constants/fixtures exactly. A relocated checkout quick run verified independence from earlier project directories.
