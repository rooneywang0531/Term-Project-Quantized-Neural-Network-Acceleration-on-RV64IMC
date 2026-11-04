#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/env.sh"
spike_revision="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["spike_commit"])' "$repo_root/tools.lock.json")"
mkdir -p "$repo_root/.deps" "$repo_root/.tools/bin"
if [[ ! -d "$SPIKE_SRC/.git" ]]; then
    git init "$SPIKE_SRC"
    git -C "$SPIKE_SRC" remote add origin https://github.com/riscv-software-src/riscv-isa-sim.git
    git -C "$SPIKE_SRC" fetch --depth 1 origin "$spike_revision"
    git -C "$SPIKE_SRC" checkout --detach FETCH_HEAD
fi
actual_revision="$(git -C "$SPIKE_SRC" rev-parse HEAD)"
[[ "$actual_revision" == "$spike_revision" ]] || { echo 'Spike checkout differs from tools.lock.json; choose a fresh SPIKE_SRC directory.' >&2; exit 1; }
git -C "$SPIKE_SRC" submodule update --init --recursive --depth 1
mkdir -p "$SPIKE_BUILD"
cd "$SPIKE_BUILD"
"$SPIKE_SRC/configure" --prefix="$repo_root/.tools" > configure.log 2>&1
make -j"${BUILD_JOBS:-2}" spike > build.log 2>&1
install -m 755 spike "$repo_root/.tools/bin/spike"
echo "Built pinned Spike: $spike_revision"
echo "Next: source $repo_root/env.sh"
