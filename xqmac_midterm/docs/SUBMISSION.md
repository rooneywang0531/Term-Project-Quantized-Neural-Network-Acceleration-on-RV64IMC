# Midterm hand-in / 提交整理

## One canonical repository

Use this directory as the GitHub repository root. Keep the earlier ZIP files as history outside the submission. Do not merge all historical `stage1`, `block`, `rq`, `full` and `rgb_v2` directories into one dependency chain.

| Earlier material | Canonical location | Role |
|---|---|---|
| Scalar model and bare-metal startup | `workload/kernels_b0.c`, `model.c`, `start.S`, `link.ld` | B0 |
| B1 tiled/unrolled kernels | `workload/kernels_b1.c` | Software-only comparison |
| Final RGB v2 kernels | `workload/kernels_x1.c` | X1_MAC / final X1_RQ from one source |
| Combined MAC + DR/SR plugin | `isa/` | Full instruction semantics and C wrappers |
| Prior MAC tests and latest RQ tests | `tests/mac/`, `tests/instructions/` | Regenerated directed/random/alias/illegal tests |
| Model exporter and original data | `model/` | Original TFLite + reproducible reference assets |
| Separate run/compare scripts | `scripts/` | One entry point per scope/configuration |
| Earlier logs | `results/reference/` | Evidence only; never inputs to a benchmark |

## Files to commit

Commit source, scripts, documentation, `tools.lock.json`, Dockerfile, model `.tflite`, `model/assets/` (including binary constants and all three fixtures), and `results/reference/`. Every included binary model/fixture is below GitHub's ordinary single-file size limit; these assets are required for offline evaluation after tool setup. Do not rely on a missing external download link for golden data.

Do not commit `.tools/`, `.deps/`, `build/`, personal virtual environments or regenerated local results. The supplied `.gitignore` handles them. In particular do not submit a workstation-specific plugin `.so` as the implementation; submit its source and build it against the evaluator's matching Spike headers.

## Hand-in procedure

1. Run the native setup or container build from README on a clean checkout.
2. Run `bash scripts/reproduce.sh quick` and `bash scripts/reproduce.sh full`.
3. Review comparison Markdown, all PASS results and compiler metadata. Keep reference numbers from one toolchain together.
4. Make the actual 5–6 minute slide PDF/PPTX using `slides/outline.md`, place it in `slides/`, and link it in README. The outline itself is not the requested slides.
5. Publish this tree to the team's GitHub repository and verify the README commands from a fresh clone. Add team members and repository link to slides as required by the course.
6. Freeze a Git commit/tag for submission (for example `midterm-v1`) and identify it in the presentation. Submit that GitHub URL and slide file through the course's required channel.

For a new empty GitHub repository, after reviewing the tree and adding the actual slides:

```bash
git init
git add .
git commit -m "Midterm: reproducible ResNet-18 Xqmac ISA evaluation"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
git tag midterm-v1
git push origin midterm-v1
```

Replace the URL placeholder with the team's repository URL. If using an existing repository, preserve its history and adapt these commands instead of reinitializing or force-pushing.

The repository has not been published by this packaging step. A slide deck has not been generated. No midterm RTL/PPA work is required by the supplied checklist; do not delay this ISA submission for it.

## Minimal TA acceptance evidence

* All MAC, DR and SR semantic tests pass; aliases/x0 and illegal encodings are checked.
* FC microbenchmark: all four variants agree with the same 1000 reference outputs; B1/X1_RQ instruction-count ratio >= 2.
* First complete residual block: two major Conv operators plus residual ADD all match reference.
* Full run: all 37 operators and 1000 final logits match for random; final X1 also passes real-zero and maximum cases.
* Reports contain dynamic instruction totals, instruction mix, load+store counts, MAC/instruction, per-operator share, operator/ELF code size and custom utilization. They do not report simulated ISA instructions as hardware cycles.
