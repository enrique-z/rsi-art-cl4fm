#!/usr/bin/env bash
# run_full.sh -- reproduce the whole experiment from raw data + seeds.
#
# Order matters: the neutral-memory control is LENGTH-MATCHED to the ungated
# arm, so the ungated arm must finish first and its realised memory length is
# measured into the config before the neutral arm starts.
set -euo pipefail
cd "$(dirname "$0")/.."
export CL4FM_OLLAMA="${CL4FM_OLLAMA:-http://127.0.0.1:11500}"
export CL4FM_PARALLEL="${CL4FM_PARALLEL:-6}"
CFG=analysis/config_full.json

echo "=== [1/6] ungated arm (also computes the shared round-0 evaluation) ==="
python3 -u analysis/harness.py --config "$CFG" --arms ungated

echo "=== [2/6] measure the ungated arm's memory length into the config ==="
python3 -u analysis/set_neutral_target.py

echo "=== [3/6] gated arm ==="
python3 -u analysis/harness.py --config "$CFG" --arms gated

echo "=== [4/6] neutral-memory control (length-matched to ungated) ==="
python3 -u analysis/harness.py --config "$CFG" --arms neutral

echo "=== [5/6] evaluation-noise null (round 0 vs round 0, different sampling seed) ==="
python3 -u analysis/harness.py --config "$CFG" --noise-null

echo "=== [6/6] aggregate -> ledger + manifest, then the figure ==="
python3 -u analysis/aggregate.py
python3 -u analysis/make_figure.py

echo "=== ALL DONE ==="
