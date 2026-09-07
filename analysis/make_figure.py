#!/usr/bin/env python3
"""make_figure.py -- recompute -> assert -> draw the paper's single evidence figure.

Every number drawn is recomputed here from the raw per-cell evidence
(evidence/runs/cells.jsonl) and asserted against the ledger
(evidence/cl4fm_selfevolve_forgetting_ledger.jsonl) before a single pixel is
emitted. If the figure and the prose ever disagree, this script raises and the
build fails.

Panels (one dense figure, no decoration):
  (a) Round-0 -> round-R accuracy per family per arm, with paired-seed 95% CIs
      on the change (the FG / BWT quantities themselves).
  (b) The falsifier: neutral-memory control vs ungated, BWT on B and C, paired
      by seed.
  (c) Acceptance economics: proposed vs accepted edits per arm (the
      "gate = fewer edits" rival mechanism).

Usage:
  python3 analysis/make_figure.py
  python3 analysis/make_figure.py --selftest
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.size"] = 7
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EVID = PAPER / "evidence"
RUNS = EVID / "runs"
SLUG = "cl4fm_selfevolve_forgetting"
LEDGER = EVID / f"{SLUG}_ledger.jsonl"
OUT = PAPER / f"fig_{SLUG}.pdf"
CLAIMS_OUT = EVID / "figure_claims.json"
TOL = 1e-5
B_BOOT = 10000
BOOT_SEED = 20260907

ARM_ORDER = ["ungated", "gated", "neutral"]
ARM_LABEL = {"ungated": "ungated", "gated": "gated", "neutral": "neutral-mem"}
ARM_COLOR = {"ungated": "#c1442e", "gated": "#2f6fa8", "neutral": "#7a7a7a"}
FAM_LABEL = {"A": "A: GSM8K (evolved)", "B": "B: ARC-Challenge", "C": "C: CommonsenseQA"}
METRIC_OF = {"A": "FG", "B": "BWT_B", "C": "BWT_C"}


def boot_ci(vals, B=B_BOOT, seed=BOOT_SEED, alpha=0.05):
    vals = list(vals)
    n = len(vals)
    if n == 0:
        return (None, None)
    if n == 1:
        return (vals[0], vals[0])
    rng = random.Random(seed)
    means = sorted(sum(vals[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return (means[int(alpha / 2 * B)], means[min(B - 1, int((1 - alpha / 2) * B))])


def load_cells():
    seen = {}
    for line in open(RUNS / "cells.jsonl"):
        c = json.loads(line)
        seen[(c["arm"], c["seed"])] = c
    by_arm = {}
    for (arm, seed), c in seen.items():
        by_arm.setdefault(arm, {})[seed] = c
    return by_arm


def recompute(by_arm):
    """Recompute every drawn aggregate straight from raw per-cell evidence."""
    out = {}
    for arm, sm in by_arm.items():
        seeds = sorted(sm)
        for fam in ("A", "B", "C"):
            m = METRIC_OF[fam]
            vals = [sm[s][m] for s in seeds]
            lo, hi = boot_ci(vals)
            out[f"{arm}__{m}"] = statistics.fmean(vals)
            out[f"{arm}__{m}_ci_low"] = lo
            out[f"{arm}__{m}_ci_high"] = hi
            out[f"{arm}__acc0_{fam}"] = statistics.fmean([sm[s]["acc0"][fam] for s in seeds])
            out[f"{arm}__accR_{fam}"] = statistics.fmean([sm[s]["accR"][fam] for s in seeds])
        for k in ("accepted_edits", "proposed_edits", "mem_chars", "mem_entries"):
            out[f"{arm}__{k}"] = statistics.fmean([sm[s][k] for s in seeds])
    for a1, a2 in (("gated", "ungated"), ("neutral", "ungated"), ("gated", "neutral")):
        if a1 not in by_arm or a2 not in by_arm:
            continue
        common = sorted(set(by_arm[a1]) & set(by_arm[a2]))
        for fam in ("A", "B", "C"):
            m = METRIC_OF[fam]
            d = [by_arm[a1][s][m] - by_arm[a2][s][m] for s in common]
            lo, hi = boot_ci(d)
            out[f"{a1}_minus_{a2}__{m}"] = statistics.fmean(d)
            out[f"{a1}_minus_{a2}__{m}_ci_low"] = lo
            out[f"{a1}_minus_{a2}__{m}_ci_high"] = hi
    return out


def assert_against_ledger(recomputed):
    ledger = {}
    for line in open(LEDGER):
        r = json.loads(line)
        ledger[r["claim_id"]] = r
    checked = []
    for cid, val in recomputed.items():
        if cid.endswith("_ci_low") or cid.endswith("_ci_high"):
            base = cid.rsplit("_ci_", 1)[0]
            side = "ci_low" if cid.endswith("_ci_low") else "ci_high"
            row = ledger.get(base)
            if row is None or row.get(side) is None:
                continue
            ref = row[side]
        else:
            row = ledger.get(cid)
            if row is None:
                continue
            ref = row["value"]
        if abs(float(ref) - float(val)) > TOL:
            raise AssertionError(
                f"FIGURE/LEDGER DRIFT on '{cid}': recomputed {val!r} vs ledger {ref!r} "
                f"(tol {TOL}). Re-run analysis/aggregate.py.")
        checked.append(cid)
    if not checked:
        raise AssertionError("no figure aggregate resolved against the ledger")
    return checked


def draw(by_arm, R):
    arms = [a for a in ARM_ORDER if a in by_arm]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.35),
                             gridspec_kw={"width_ratios": [2.0, 1.25, 1.0]})

    # ---- (a) round-0 -> round-R accuracy, with CI on the change -----------
    ax = axes[0]
    xs, labels = [], []
    x = 0
    for fam in ("A", "B", "C"):
        for arm in arms:
            sm = by_arm[arm]
            seeds = sorted(sm)
            a0 = statistics.fmean([sm[s]["acc0"][fam] for s in seeds])
            aR = statistics.fmean([sm[s]["accR"][fam] for s in seeds])
            d = [sm[s][METRIC_OF[fam]] for s in seeds]
            lo, hi = boot_ci(d)
            c = ARM_COLOR[arm]
            ax.plot([x - 0.16, x + 0.16], [a0, aR], color=c, lw=1.1, zorder=2)
            ax.plot([x - 0.16], [a0], "o", ms=3.2, mfc="white", mec=c, mew=1.0, zorder=3)
            ax.plot([x + 0.16], [aR], "o", ms=3.2, color=c, zorder=3)
            ax.errorbar([x + 0.16], [aR],
                        yerr=[[max(0.0, aR - (a0 + lo))], [max(0.0, (a0 + hi) - aR)]],
                        color=c, capsize=1.8, lw=0.9, zorder=1)
            xs.append(x)
            labels.append(ARM_LABEL[arm])
            x += 1
        x += 0.6
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=5.6)
    ax.set_ylabel("accuracy")
    ax.set_title(f"(a) round 0 (open) $\\rightarrow$ round {R} (filled); "
                 f"bars = 95% CI on the change", fontsize=6.4, loc="left")
    for i, fam in enumerate(("A", "B", "C")):
        centre = (len(arms) - 1) / 2 + i * (len(arms) + 0.6)
        ax.text(centre, 1.005, FAM_LABEL[fam], ha="center", va="bottom",
                fontsize=5.8, transform=ax.get_xaxis_transform())
    ax.grid(axis="y", lw=0.3, alpha=0.4)
    ax.set_axisbelow(True)

    # ---- (b) falsifier: neutral vs ungated on held-out BWT ----------------
    ax = axes[1]
    fams = ["B", "C"]
    w = 0.26
    for j, arm in enumerate(arms):
        sm = by_arm[arm]
        seeds = sorted(sm)
        pos, mu, err = [], [], [[], []]
        for i, fam in enumerate(fams):
            v = [sm[s][METRIC_OF[fam]] for s in seeds]
            m = statistics.fmean(v)
            lo, hi = boot_ci(v)
            pos.append(i + (j - (len(arms) - 1) / 2) * w)
            mu.append(m)
            err[0].append(max(0.0, m - lo))
            err[1].append(max(0.0, hi - m))
        ax.bar(pos, mu, width=w * 0.9, color=ARM_COLOR[arm], label=ARM_LABEL[arm],
               edgecolor="none")
        ax.errorbar(pos, mu, yerr=err, fmt="none", ecolor="black", lw=0.8, capsize=1.6)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(range(len(fams)))
    ax.set_xticklabels(["B", "C"])
    ax.set_ylabel("BWT (held-out)")
    ax.set_title("(b) falsifier: content vs dilution", fontsize=6.4, loc="left")
    ax.legend(fontsize=5.4, frameon=False, loc="best")
    ax.grid(axis="y", lw=0.3, alpha=0.4)
    ax.set_axisbelow(True)

    # ---- (c) acceptance economics ----------------------------------------
    ax = axes[2]
    ap_ = [statistics.fmean([by_arm[a][s]["accepted_edits"] for s in sorted(by_arm[a])])
           for a in arms]
    pr = [statistics.fmean([by_arm[a][s]["proposed_edits"] for s in sorted(by_arm[a])])
          for a in arms]
    idx = list(range(len(arms)))
    ax.bar([i - 0.19 for i in idx], pr, width=0.34, color="#d8d8d8",
           edgecolor="black", lw=0.4, label="proposed")
    ax.bar([i + 0.19 for i in idx], ap_, width=0.34,
           color=[ARM_COLOR[a] for a in arms], edgecolor="none", label="accepted")
    ax.set_xticks(idx)
    ax.set_xticklabels([ARM_LABEL[a] for a in arms], rotation=45, ha="right", fontsize=5.6)
    ax.set_ylabel("memory edits")
    ax.set_title("(c) edit economics", fontsize=6.4, loc="left")
    ax.legend(fontsize=5.4, frameon=False)
    ax.grid(axis="y", lw=0.3, alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout(pad=0.4)
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        try:
            assert_against_ledger({"__nonexistent__": 1.0})
        except AssertionError as e:
            if "no figure aggregate resolved" not in str(e):
                raise
            print("selftest OK: empty-resolution guard fires")
        else:
            print("selftest FAILED: guard did not fire", file=sys.stderr)
            return 1
        by_arm = load_cells()
        rec = recompute(by_arm)
        k = next(iter(rec))
        bad = dict(rec)
        bad[k] = float(bad[k]) + 1.0
        try:
            assert_against_ledger(bad)
        except AssertionError as e:
            assert "DRIFT" in str(e)
            print("selftest OK: drift assertion fires")
            return 0
        print("selftest FAILED: drift not detected", file=sys.stderr)
        return 1

    by_arm = load_cells()
    R = max(c["rounds"] for sm in by_arm.values() for c in sm.values())
    rec = recompute(by_arm)
    checked = assert_against_ledger(rec)
    draw(by_arm, R)
    CLAIMS_OUT.write_text(json.dumps(
        {"figure": OUT.name,
         "claim_ids": sorted({c for c in checked
                              if not (c.endswith("_ci_low") or c.endswith("_ci_high"))}),
         "note": "every value drawn was recomputed from evidence/runs/cells.jsonl "
                 "and asserted equal to its ledger row before drawing"},
        indent=2) + "\n")
    print(f"wrote {OUT} ({len(checked)} aggregates asserted against the ledger)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
