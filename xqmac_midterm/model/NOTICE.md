# Model and reference provenance

* Model: LiteRT Community ResNet-18, static per-channel INT8 variant, file `resnet18_int8_channelwise.tflite`.
* Source: https://huggingface.co/litert-community/resnet18
* Pinned revision: `7eabef429f15b4fcd4db3e225d81bd0fd7860c4f`.
* Exact download: https://huggingface.co/litert-community/resnet18/resolve/7eabef429f15b4fcd4db3e225d81bd0fd7860c4f/resnet18_int8_channelwise.tflite
* Model SHA-256: `8fea1acb62829e120b4953b6fbf0f842e0032909254f51c2d989703b66534683`.
* Model size: 11,855,616 bytes.

`export_model.py` verifies this hash, reads the graph and integer quantization data, generates C declarations/operator calls and runs LiteRT BUILTIN_REF to record reference outputs. It does not train or newly quantize the model. Python package versions are pinned in `requirements-export.txt`.

Three inputs: seeded random INT8 (seed 20261024), quantized real zero (input zero point -14) and maximum INT8 (127). `fixtures/*.bin` stores raw model input followed by all operator reference outputs. The Python reference uses original model operators; C is an independent integer implementation. Reference data are only comparisons during full inference. Isolated FC/block benchmarks deliberately use reference boundary activations as fixture setup.

`assets/asset_hashes.json` guards original generated files. `operators_fc.inc` and `operators_block.inc` select original wrappers for isolated scopes and are not replacements for the full graph.

Model authorship and upstream terms remain those of the linked model repository. Spike is fetched from its upstream repository at the pinned revision in `tools.lock.json`; its source checkout includes its own license and notices. This package makes no claim of authorship of those upstream components.
