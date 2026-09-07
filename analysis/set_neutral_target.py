#!/usr/bin/env python3
"""set_neutral_target.py -- measure the ungated arm's realised memory length and
write it into the config as the neutral-memory control's per-round target.

The pre-declared falsifier (gate 13b) needs a "length-matched neutral-memory"
arm. Matched to WHAT is a measurement, not a guess: this script reads the
completed ungated cells, takes the mean cumulative memory length in characters
after each round, and writes that vector into config_full.json as
`neutral_target_chars`. The neutral arm then pads with task-irrelevant
sentences until it reaches that length.

Run AFTER the ungated arm completes and BEFORE the neutral arm starts.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
RUNS = PAPER / "evidence" / "runs"
CFG = PAPER / "analysis" / "config_full.json"


def main():
    # Optional: --from-arm <arm> --key <cfg key>. Defaults reproduce the
    # original behaviour exactly (ungated -> neutral_target_chars), so
    # analysis/run_full.sh is unaffected.
    argv = sys.argv[1:]
    from_arm = "ungated"
    key = "neutral_target_chars"
    if "--from-arm" in argv:
        from_arm = argv[argv.index("--from-arm") + 1]
    if "--key" in argv:
        key = argv[argv.index("--key") + 1]

    cfg = json.load(open(CFG))
    per_round = defaultdict(list)
    files = sorted(RUNS.glob(f"cell_{from_arm}_seed*.jsonl"))
    if not files:
        print(f"no completed {from_arm} cells found in evidence/runs/", file=sys.stderr)
        return 1
    for f in files:
        for line in open(f):
            r = json.loads(line)
            if r.get("kind") == "round":
                per_round[r["round"]].append(r["mem_chars"])
    if not per_round:
        print(f"{from_arm} cells contain no round records", file=sys.stderr)
        return 1
    targets = [int(round(statistics.fmean(per_round[k])))
               for k in sorted(per_round)]
    cfg[key] = targets
    cfg["_" + key + "_provenance"] = {
        "measured_from": [f.name for f in files],
        "per_round_observed_mem_chars": {str(k): per_round[k] for k in sorted(per_round)},
        "rule": f"mean over {from_arm} seeds of cumulative memory length in "
                "characters after each round",
    }
    CFG.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"{key} = {targets}")
    print(f"measured from {len(files)} {from_arm} cells: "
          + "; ".join(f"r{k}={per_round[k]}" for k in sorted(per_round)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
