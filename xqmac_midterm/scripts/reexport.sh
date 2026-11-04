#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# Optional audit path: never overwrite the committed reference assets.
python3 "$repo_root/model/export_model.py" "$repo_root/model/resnet18_int8_channelwise.tflite" --output "$repo_root/build/reexport"
python3 - "$repo_root" <<'PY'
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);expected=json.loads((r/'model/assets/asset_hashes.json').read_text())
for name,sha in expected.items():
    p=r/'build/reexport'/name
    assert p.is_file(),'Re-export missing: '+name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,'Re-export differs: '+name
print('PASS: regenerated constants, graph and fixtures match every committed exporter asset hash.')
PY
