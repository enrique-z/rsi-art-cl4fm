#!/usr/bin/env python3
"""aggregate.py -- turn raw run output into EGCL ledger rows + stamp manifest.

Reads evidence/runs/cells.jsonl (one row per arm x seed) and
evidence/runs/per_item.jsonl (per-item correctness, for McNemar) and emits:

  evidence/cl4fm_selfevolve_forgetting_ledger.jsonl
  evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json
  evidence/aggregates.json          (machine-readable, consumed by make_figure)

Statistics
----------
Unit of independence = seed. Seed-level bootstrap (B = 10,000) over the seed
vector of the statistic. Paired across arms by seed for arm contrasts.
McNemar (exact binomial, two-sided) over per-item round-0 vs round-R
correctness pooled across seeds, reported as a robustness check only.

Stdlib only.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
EVID = PAPER / "evidence"
RUNS = EVID / "runs"
B_BOOT = 10000
BOOT_SEED = 20260907
SLUG = "cl4fm_selfevolve_forgetting"


def boot_ci(vals, B=B_BOOT, seed=BOOT_SEED, alpha=0.05):
    """Percentile bootstrap over the unit-of-independence vector."""
    vals = list(vals)
    n = len(vals)
    if n == 0:
        return (None, None)
    if n == 1:
        return (vals[0], vals[0])
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        means.append(sum(vals[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo = means[int(alpha / 2 * B)]
    hi = means[min(B - 1, int((1 - alpha / 2) * B))]
    return (lo, hi)


def binom_two_sided(b, c):
    """Exact McNemar: two-sided binomial test of b successes out of n=b+c, p=0.5."""
    n = b + c
    if n == 0:
        return 1.0
    def pmf(k):
        return math.comb(n, k) * 0.5 ** n
    obs = pmf(b)
    return min(1.0, sum(pmf(k) for k in range(n + 1) if pmf(k) <= obs + 1e-12))


def main():
    cells = [json.loads(l) for l in open(RUNS / "cells.jsonl")]
    # de-duplicate on (arm, seed), keeping the last write
    seen = {}
    for c in cells:
        seen[(c["arm"], c["seed"])] = c
    cells = list(seen.values())

    by_arm = defaultdict(dict)   # arm -> seed -> row
    for c in cells:
        by_arm[c["arm"]][c["seed"]] = c

    agg = {"arms": {}, "contrasts": {}, "mcnemar": {}, "config": {}}
    ledger = []
    manifest = {"ledger_rows": {}}
    ts = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())

    def add(claim_id, metric, value, reason, ci=(None, None), must_print=True,
            stamp=None):
        row = {"claim_id": claim_id, "metric": metric,
               "value": round(value, 6) if isinstance(value, float) else value,
               "source": str(RUNS / "cells.jsonl"),
               "verdict": "SUPPORTED", "verdict_reason": reason,
               "ci_low": None if ci[0] is None else round(ci[0], 6),
               "ci_high": None if ci[1] is None else round(ci[1], 6),
               "must_print": must_print, "timestamp": ts}
        ledger.append(row)
        if stamp:
            manifest["ledger_rows"][stamp] = {
                "value": row["value"],
                "claim_id": claim_id,
                "source": f"{SLUG}_ledger.jsonl:{len(ledger)}",
                "must_print": must_print}
        return row

    METRICS = [("FG", "A"), ("BWT_B", "B"), ("BWT_C", "C")]

    for arm, seedmap in sorted(by_arm.items()):
        seeds = sorted(seedmap)
        entry = {"seeds": seeds, "n_seeds": len(seeds)}
        for mname, fam in METRICS:
            vals = [seedmap[s][mname] for s in seeds]
            mu = statistics.fmean(vals)
            lo, hi = boot_ci(vals)
            entry[mname] = {"mean": mu, "ci_low": lo, "ci_high": hi, "per_seed": vals}
            add(f"{arm}__{mname}", mname, mu,
                f"mean over {len(seeds)} seeds of {mname} for arm '{arm}'; "
                f"seed-level percentile bootstrap B={B_BOOT}",
                (lo, hi), must_print=True,
                stamp=f"{arm}::{mname}")
            add(f"{arm}__{mname}_ci_low", "ci_low", lo,
                f"bootstrap 2.5th pct of {mname}, arm '{arm}'", must_print=False,
                stamp=f"{arm}::{mname}_ci_low")
            add(f"{arm}__{mname}_ci_high", "ci_high", hi,
                f"bootstrap 97.5th pct of {mname}, arm '{arm}'", must_print=False,
                stamp=f"{arm}::{mname}_ci_high")
        for k in ("accepted_edits", "proposed_edits", "mem_chars", "mem_entries"):
            vals = [seedmap[s][k] for s in seeds]
            entry[k] = {"mean": statistics.fmean(vals), "per_seed": vals}
            add(f"{arm}__{k}", k, statistics.fmean(vals),
                f"mean over {len(seeds)} seeds of {k}, arm '{arm}'",
                must_print=False, stamp=f"{arm}::{k}")
            # per-seed realised values: the arms' memory lengths are highly
            # heterogeneous (the gate can accept nothing on a seed), so the arm
            # mean hides the structure a length-matching argument depends on.
            for sd, v in zip(seeds, vals):
                add(f"{arm}__{k}_seed{sd}", k, v,
                    f"seed {sd} realised {k}, arm '{arm}'",
                    must_print=False, stamp=f"{arm}::{k}_s{sd}")
        for fam in ("A", "B", "C"):
            a0 = [seedmap[s]["acc0"][fam] for s in seeds]
            aR = [seedmap[s]["accR"][fam] for s in seeds]
            entry[f"acc0_{fam}"] = {"mean": statistics.fmean(a0), "per_seed": a0}
            entry[f"accR_{fam}"] = {"mean": statistics.fmean(aR), "per_seed": aR}
            add(f"{arm}__acc0_{fam}", "accuracy", statistics.fmean(a0),
                f"round-0 accuracy on family {fam}, arm '{arm}'",
                boot_ci(a0), must_print=False, stamp=f"{arm}::acc0_{fam}")
            add(f"{arm}__accR_{fam}", "accuracy", statistics.fmean(aR),
                f"round-R accuracy on family {fam}, arm '{arm}'",
                boot_ci(aR), must_print=False, stamp=f"{arm}::accR_{fam}")
        agg["arms"][arm] = entry

    # ---- paired arm contrasts (paired by seed) -----------------------------
    def contrast(a1, a2, mname):
        if a1 not in by_arm or a2 not in by_arm:
            return None
        common = sorted(set(by_arm[a1]) & set(by_arm[a2]))
        if not common:
            return None
        d = [by_arm[a1][s][mname] - by_arm[a2][s][mname] for s in common]
        mu = statistics.fmean(d)
        lo, hi = boot_ci(d)
        return {"pair": f"{a1}-minus-{a2}", "metric": mname, "n_seeds": len(common),
                "seeds": common,
                "mean": mu, "ci_low": lo, "ci_high": hi, "per_seed": d,
                "excludes_zero": bool(lo is not None and (lo > 0 or hi < 0))}

    for a1, a2 in (("gated", "ungated"), ("neutral", "ungated"),
                   ("gated", "neutral"), ("gated", "neutralshort"),
                   ("neutralshort", "ungated")):
        for mname, _ in METRICS:
            c = contrast(a1, a2, mname)
            if c is None:
                continue
            key = f"{a1}_minus_{a2}__{mname}"
            agg["contrasts"][key] = c
            add(key, f"delta_{mname}", c["mean"],
                f"paired-by-seed difference {a1} - {a2} on {mname} "
                f"(n={c['n_seeds']} seeds); bootstrap B={B_BOOT}; "
                f"CI excludes zero = {c['excludes_zero']}",
                (c["ci_low"], c["ci_high"]), must_print=True,
                stamp=f"contrast::{key}")
            add(f"{key}_ci_low", f"delta_{mname}_ci_low", c["ci_low"],
                f"bootstrap 2.5th pct of paired difference {a1} - {a2} "
                f"on {mname}", must_print=False,
                stamp=f"contrast::{key}_ci_low")
            add(f"{key}_ci_high", f"delta_{mname}_ci_high", c["ci_high"],
                f"bootstrap 97.5th pct of paired difference {a1} - {a2} "
                f"on {mname}", must_print=False,
                stamp=f"contrast::{key}_ci_high")

    # ---- EXPLORATORY per-seed influence analysis (amendment A4) ------------
    # Added 2026-09-07, AFTER the primary results were known, in response to
    # adversarial review. Not pre-registered. Answers one question the seed
    # bootstrap cannot: is a contrast carried by a single seed?
    #
    # With n=3 paired seeds the exact two-sided sign-flip permutation test has
    # 2^3 = 8 equally likely sign assignments, so its SMALLEST attainable
    # two-sided p-value is 2/8 = 0.25. Reporting it is the honest ceiling on
    # what three seeds can establish, whatever the bootstrap CI says.
    def signflip_p(d):
        n = len(d)
        obs = abs(statistics.fmean(d))
        hits = 0
        for mask in range(2 ** n):
            dd = [(-x if (mask >> i) & 1 else x) for i, x in enumerate(d)]
            if abs(statistics.fmean(dd)) >= obs - 1e-12:
                hits += 1
        return hits / 2 ** n

    for a1, a2 in (("gated", "ungated"), ("neutral", "ungated"),
                   ("gated", "neutralshort")):
        for mname, _ in METRICS:
            c = agg["contrasts"].get(f"{a1}_minus_{a2}__{mname}")
            if not c:
                continue
            key = f"{a1}_minus_{a2}__{mname}"
            d = c["per_seed"]
            sds = c.get("seeds", list(range(1, len(d) + 1)))
            for sd, v in zip(sds, d):
                add(f"{key}_seed{sd}", f"delta_{mname}_per_seed", v,
                    f"per-seed paired difference {a1} - {a2} on {mname}, "
                    f"seed {sd} (exploratory, amendment A4)",
                    must_print=False, stamp=f"perseed::{key}_s{sd}")
            if len(d) > 1:
                for sd in sds:
                    loo = [v for s2, v in zip(sds, d) if s2 != sd]
                    add(f"{key}_drop{sd}", f"delta_{mname}_loo",
                        statistics.fmean(loo),
                        f"leave-one-seed-out mean of {a1} - {a2} on {mname}, "
                        f"seed {sd} dropped (exploratory, amendment A4)",
                        must_print=False, stamp=f"loo::{key}_drop{sd}")
                pv = signflip_p(d)
                c["signflip_p"] = pv
                add(f"{key}_signflip_p", "p_value", pv,
                    f"exact two-sided sign-flip permutation test on the "
                    f"{len(d)} paired seed differences of {a1} - {a2} on "
                    f"{mname}; floor for n={len(d)} is {2 / 2 ** len(d):.2f} "
                    f"(exploratory, amendment A4)",
                    must_print=False, stamp=f"perm::{key}_p")

    # ---- McNemar robustness check (per-item, pooled across seeds) ----------
    items = [json.loads(l) for l in open(RUNS / "per_item.jsonl")]
    r0 = {}
    for r in items:
        if r["arm"] == "ROUND0":
            r0[(r["seed"], r["uid"])] = r["correct"]
    n_amb = sum(1 for r in items if r.get("ambiguous"))
    agg["n_items_scored"] = len(items)
    agg["n_ambiguous_parses"] = n_amb
    add("ambiguous_parse_count", "count", n_amb,
        f"model replies where the deterministic extractor found no candidate "
        f"answer, out of {len(items)} graded items; scored as incorrect and logged",
        must_print=False, stamp="global::n_ambiguous")
    add("items_scored_total", "count", len(items),
        "total graded model responses across all arms, seeds and evaluation points",
        must_print=False, stamp="global::n_items_scored")

    for arm in by_arm:
        for fam in ("A", "B", "C"):
            b = c_ = 0
            for r in items:
                if r["arm"] != arm or r["family"] != fam:
                    continue
                base = r0.get((r["seed"], r["uid"]))
                if base is None:
                    continue
                if base == 1 and r["correct"] == 0:
                    b += 1
                elif base == 0 and r["correct"] == 1:
                    c_ += 1
            p = binom_two_sided(b, c_)
            agg["mcnemar"][f"{arm}__{fam}"] = {"b_lost": b, "c_gained": c_, "p": p}
            add(f"mcnemar_{arm}_{fam}", "p_value", p,
                f"exact two-sided McNemar, arm '{arm}' family {fam}: "
                f"{b} items correct at round 0 and wrong at round R, "
                f"{c_} the reverse (pooled over seeds; robustness check only)",
                must_print=False, stamp=f"mcnemar::{arm}_{fam}")

    # ---- pre-declared rival 2: evaluation-noise null distribution ----------
    # Round 0 re-evaluated with an empty memory under a different sampling seed.
    # This is the null band for FG and BWT: an effect inside it is noise.
    nn_path = RUNS / "noise_null.jsonl"
    if nn_path.exists():
        nn = [json.loads(l) for l in open(nn_path)]
        seen_nn = {r["seed"]: r for r in nn}
        nn = [seen_nn[s] for s in sorted(seen_nn)]
        agg["noise_null"] = {"n_seeds": len(nn), "seeds": [r["seed"] for r in nn]}
        for fam in ("A", "B", "C"):
            vals = [r[f"noise_{fam}"] for r in nn]
            mu = statistics.fmean(vals)
            lo, hi = boot_ci(vals)
            absmax = max(abs(v) for v in vals)
            agg["noise_null"][fam] = {"mean": mu, "ci_low": lo, "ci_high": hi,
                                      "per_seed": vals, "max_abs": absmax}
            add(f"noise_null__{fam}", "delta_accuracy", mu,
                f"family {fam}: mean over {len(nn)} seeds of "
                f"acc(empty memory, sampling seed s+100) - acc(empty memory, seed s) "
                f"on the SAME fixed item set. Null distribution of FG/BWT under "
                f"'nothing was learned, only the sampling changed'.",
                (lo, hi), must_print=True, stamp=f"noise_null::{fam}")
            add(f"noise_null__{fam}_max_abs", "max_abs_delta", absmax,
                f"largest absolute round-0 vs round-0 accuracy shift observed on "
                f"family {fam} across seeds; any |BWT| below this is not "
                f"distinguishable from evaluation noise",
                must_print=False, stamp=f"noise_null::{fam}_max_abs")

    # ---- protocol-failure accounting (a 3B model is asked to emit JSON) ----
    # A high protocol-failure rate is itself a finding and is never dropped.
    proto = {"per_arm": {}, "total_rounds": 0, "rounds_below_budget": 0}
    cfgp = PAPER / "analysis" / "config_full.json"
    budget = json.load(open(cfgp))["edit_budget"] if cfgp.exists() else None
    for f in sorted(RUNS.glob("cell_*.jsonl")):
        arm = f.name.split("_")[1]
        for line in open(f):
            r = json.loads(line)
            if r.get("kind") != "round":
                continue
            e = proto["per_arm"].setdefault(
                arm, {"rounds": 0, "parse_status": defaultdict(int),
                      "rounds_below_budget": 0, "total_proposed": 0,
                      "total_accepted": 0})
            e["rounds"] += 1
            e["parse_status"][r.get("parse_status", "?")] += 1
            e["total_proposed"] += r["n_proposed"]
            e["total_accepted"] += r["n_accepted"]
            proto["total_rounds"] += 1
            if budget and not arm.startswith("neutral") and r["n_proposed"] < budget:
                e["rounds_below_budget"] += 1
                proto["rounds_below_budget"] += 1
    for arm, e in proto["per_arm"].items():
        e["parse_status"] = dict(e["parse_status"])
        n_bad = sum(v for k, v in e["parse_status"].items()
                    if k in ("no_json", "bad_json", "not_list"))
        e["unparseable_reflections"] = n_bad
        add(f"protocol_{arm}__unparseable_reflections", "count", n_bad,
            f"arm '{arm}': reflection replies the deterministic edit parser could "
            f"not read (status in no_json/bad_json/not_list), out of {e['rounds']} "
            f"rounds", must_print=False,
            stamp=f"protocol::{arm}_unparseable")
        add(f"protocol_{arm}__rounds_below_budget", "count", e["rounds_below_budget"],
            f"arm '{arm}': rounds in which the model proposed fewer than the "
            f"{budget}-edit budget, out of {e['rounds']} rounds",
            must_print=False, stamp=f"protocol::{arm}_below_budget")
    agg["protocol_failures"] = proto

    # ---- call-log audit ----------------------------------------------------
    cl = EVID / "calls.jsonl"
    if cl.exists():
        calls = [json.loads(l) for l in open(cl)]
        n_err = sum(1 for c in calls if c.get("error"))
        n_retry = sum(1 for c in calls if (c.get("attempt") or 1) > 1)
        agg["calls"] = {"n": len(calls), "n_failed_attempts": n_err,
                        "n_retried": n_retry}
        add("model_calls_total", "count", len(calls),
            "logged Ollama /api/chat attempts across the whole experiment",
            must_print=False, stamp="global::n_model_calls")
        add("model_calls_failed", "count", n_err,
            "logged call attempts that raised (network/server); each was retried "
            "with identical parameters, so no measurement changed",
            must_print=False, stamp="global::n_failed_calls")

    cfg_path = PAPER / "analysis" / "config_full.json"
    if cfg_path.exists():
        agg["config"] = json.load(open(cfg_path))

    (EVID / f"{SLUG}_ledger.jsonl").write_text(
        "\n".join(json.dumps(r) for r in ledger) + "\n")
    (EVID / f"{SLUG}_stamp_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    (EVID / "aggregates.json").write_text(json.dumps(agg, indent=2) + "\n")

    print(f"ledger rows: {len(ledger)}")
    print(f"verdicts: SUPPORTED={sum(1 for r in ledger if r['verdict']=='SUPPORTED')}")
    print(f"manifest keys: {len(manifest['ledger_rows'])}")
    for arm in sorted(agg["arms"]):
        e = agg["arms"][arm]
        print(f"  {arm:9s} n={e['n_seeds']} "
              + "  ".join(f"{m}={e[m]['mean']:+.3f}[{e[m]['ci_low']:+.3f},{e[m]['ci_high']:+.3f}]"
                          for m, _ in METRICS))
    for k, v in agg["contrasts"].items():
        print(f"  {k}: {v['mean']:+.3f} [{v['ci_low']:+.3f},{v['ci_high']:+.3f}] "
              f"excl0={v['excludes_zero']}")


if __name__ == "__main__":
    main()
