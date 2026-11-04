#!/usr/bin/env bash
# Source this file; all defaults are relative to this checkout.
xqmac_repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$xqmac_repo_root/.tools/cross/usr/bin:$xqmac_repo_root/.tools/bin:$PATH"
export SPIKE_SRC="${SPIKE_SRC:-$xqmac_repo_root/.deps/spike}"
export SPIKE_BUILD="${SPIKE_BUILD:-$SPIKE_SRC/build}"
export SPIKE_BIN="${SPIKE_BIN:-$xqmac_repo_root/.tools/bin/spike}"
