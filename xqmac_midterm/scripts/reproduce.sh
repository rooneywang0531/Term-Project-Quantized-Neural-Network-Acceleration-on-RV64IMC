#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/env.sh"
cd "$repo_root"
mode="${1:-quick}"
case "$mode" in quick|full|all) ;; *) echo 'Usage: bash scripts/reproduce.sh quick|full|all' >&2; exit 1;; esac
python3 scripts/test_profiler.py
python3 scripts/run_unit.py
if [[ "$mode" == quick || "$mode" == all ]]; then
    for config in B0 B1 X1_MAC X1_RQ; do python3 scripts/benchmark.py --scope fc --config "$config"; done
    python3 scripts/compare.py fc
    python3 scripts/benchmark.py --scope block --config X1_RQ
fi
if [[ "$mode" == full || "$mode" == all ]]; then
    for config in B0 B1 X1_MAC X1_RQ; do python3 scripts/benchmark.py --scope full --config "$config"; done
    python3 scripts/compare.py full
    for case_id in 1 2; do python3 scripts/benchmark.py --scope full --config X1_RQ --case "$case_id"; done
fi
