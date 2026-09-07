#!/usr/bin/env python3
"""make_report_tables.py -- emit the numeric sections of EXPERIMENT_REPORT.md
directly from evidence/aggregates.json.

No number in the report is typed by hand. This script prints markdown that is
pasted between the RESULTS-BEGIN / RESULTS-END markers of EXPERIMENT_REPORT.md,
so every figure in the report traces to a ledger row.
"""
from __future__ import annotations

import json
import collections
import datetime
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
EVID = PAPER / "evidence"
A = json.load(open(EVID / "aggregates.json"))
ARMS = [a for a in ("ungated", "gated", "neutral") if a in A["arms"]]
FAMS = [("A", "FG", "GSM8K (evolved)"),
        ("B", "BWT_B", "ARC-Challenge (held out)"),
        ("C", "BWT_C", "CommonsenseQA (held out)")]


def ci(d):
    return f"[{d['ci_low']:+.4f}, {d['ci_high']:+.4f}]"


def excl0(d):
    return "yes" if (d["ci_low"] > 0 or d["ci_high"] < 0) else "no"


out = []
w = out.append

w("### Round-0 and round-R accuracy, and the pre-registered metrics\n")
w("Unit of independence = seed. CI = percentile bootstrap over the seed vector, "
  f"B = 10,000. n = {A['arms'][ARMS[0]]['n_seeds']} seeds "
  f"({A['arms'][ARMS[0]]['seeds']}).\n")
w("| arm | family | acc round 0 | acc round R | metric | mean | 95% CI | CI excludes 0 |")
w("|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    e = A["arms"][arm]
    for fam, metric, label in FAMS:
        d = e[metric]
        w(f"| {arm} | {label} | {e[f'acc0_{fam}']['mean']:.4f} | "
          f"{e[f'accR_{fam}']['mean']:.4f} | {metric} | {d['mean']:+.4f} | "
          f"{ci(d)} | {excl0(d)} |")
w("")

w("### Per-seed values (the actual bootstrap units)\n")
w("| arm | metric | " + " | ".join(f"seed {s}" for s in A["arms"][ARMS[0]]["seeds"]) + " |")
w("|---|---|" + "---|" * len(A["arms"][ARMS[0]]["seeds"]))
for arm in ARMS:
    for _, metric, _ in FAMS:
        vals = A["arms"][arm][metric]["per_seed"]
        w(f"| {arm} | {metric} | " + " | ".join(f"{v:+.4f}" for v in vals) + " |")
w("")

w("### Paired arm contrasts (paired by seed)\n")
w("| contrast | metric | mean difference | 95% CI | CI excludes 0 |")
w("|---|---|---|---|---|")
for key, c in A["contrasts"].items():
    w(f"| {c['pair']} | {c['metric']} | {c['mean']:+.4f} | "
      f"[{c['ci_low']:+.4f}, {c['ci_high']:+.4f}] | "
      f"{'yes' if c['excludes_zero'] else 'no'} |")
w("")

w("### Edit economics (the \"the gate just edits less\" rival mechanism)\n")
w("| arm | edits proposed (mean/seed) | edits accepted (mean/seed) | "
  "acceptance rate | final memory entries | final memory chars |")
w("|---|---|---|---|---|---|")
for arm in ARMS:
    e = A["arms"][arm]
    p = e["proposed_edits"]["mean"]
    a_ = e["accepted_edits"]["mean"]
    rate = f"{a_/p:.3f}" if p else "n/a"
    w(f"| {arm} | {p:.2f} | {a_:.2f} | {rate} | "
      f"{e['mem_entries']['mean']:.2f} | {e['mem_chars']['mean']:.1f} |")
w("")

w("### McNemar robustness check (per item, pooled across seeds)\n")
w("Secondary check only -- items are not independent units here, so this is "
  "reported beside the seed-level CIs, never in place of them. "
  "`b` = correct at round 0 and wrong at round R; `c` = the reverse.\n")
w("| arm | family | b (lost) | c (gained) | exact two-sided p |")
w("|---|---|---|---|---|")
for arm in ARMS:
    for fam, _, label in FAMS:
        m = A["mcnemar"].get(f"{arm}__{fam}")
        if m:
            w(f"| {arm} | {label} | {m['b_lost']} | {m['c_gained']} | {m['p']:.4f} |")
w("")

w("### Grading audit\n")
w(f"- graded model responses: **{A['n_items_scored']}**")
w(f"- responses where the deterministic extractor found no candidate answer "
  f"(logged, scored incorrect, never guessed): **{A['n_ambiguous_parses']}** "
  f"({A['n_ambiguous_parses']/max(A['n_items_scored'],1)*100:.2f}%)")

# call-log audit
calls = [json.loads(l) for l in open(EVID / "calls.jsonl")]
errs = sum(1 for c in calls if c.get("error"))
retries = sum(1 for c in calls if (c.get("attempt") or 1) > 1)
lat = sorted(c["latency_s"] for c in calls)
tags = collections.Counter(c["tag"].rsplit("/", 1)[-1] for c in calls)
t0 = min(c["ts"] for c in calls)
t1 = max(c["ts"] for c in calls)
fmt = "%Y-%m-%dT%H:%M:%SZ"
span = (datetime.datetime.strptime(t1, fmt) - datetime.datetime.strptime(t0, fmt))
w("")
w("### Model-call audit (`evidence/calls.jsonl`)\n")
w(f"- total logged Ollama calls: **{len(calls)}**")
w(f"- failed attempts (retried): **{errs}**; calls that needed a retry: **{retries}**")
w(f"- wallclock span: {t0} to {t1} ({span})")
w(f"- latency median {lat[len(lat)//2]:.1f} s, p95 {lat[int(len(lat)*0.95)]:.1f} s, "
  f"max {lat[-1]:.1f} s")
w(f"- call purposes: {dict(tags)}")

print("\n".join(out))
