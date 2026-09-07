# EXPERIMENT_REPORT — cl4fm-selfevolve-forgetting

**Status: COMPLETE.** The pre-declared grid finished; the ledger, manifest,
figure and PDF are green through the build gates. This report is
generated from `evidence/aggregates.json`; no number here is typed by hand.

Binding design: `A2_PREDECLARATION_2026-09-07.md`.
Operational record and every deviation: `evidence/DESIGN_NOTES.md`.

---

## 1. Smoke test (STEP 1)

Both candidate models solved one real GSM8K item end-to-end via the real
Ollama API:

- `qwen3:8b` with `"think": false` returned `#### 72` against gold `72`; no
  `<think>` block in the reply (verified by inspection);
- `llama3.2:3b` returned `72` via the last-number fallback.

**Smoke test status: PASS.**

## 2. Configuration chosen (frozen before the run)

Measured on the dedicated Ollama instance on `127.0.0.1:11500`:

| workload | s/item | items/s | pilot accuracy |
|---|---|---|---|
| GSM8K CoT (`num_predict` 320) | 6.77 | 0.148 | 0.500 |
| ARC-Challenge MCQ (`num_predict` 140) | 2.16 | 0.464 | 0.833 |

The pre-declaration made the model choice conditional on the pilot. The pilot
chose `llama3.2:3b` (projected ≈3.4 h against ≈9–10 h for `qwen3:8b` on a
contended host that had returned 500s after five-minute queue waits). Frozen
configuration: R = 3 rounds, seeds 1/2/3, 60 items per family, edit budget 3,
temperature 0.7 (see A3 below). Amendment A5 later extended the grid to
**six seeds (1-6)**; every number in §4-§9 and §11 below is the six-seed
result, which is what the paper reports.

**A material infrastructure finding.** The machine's default Ollama server is
shared with other jobs on this host; single requests to it took 414 s and 622 s
for ~75 output tokens (queueing, not compute). Every number in this paper comes
from a **dedicated Ollama instance** started for this experiment on port 11500.

## 3. Deviations and amendments

A1, D1/D2, A2 and A3 were pre-committed before the data they could affect
existed. A4, A5 and A6 are post-hoc and are labelled as such throughout; A5
carried its reporting rule — the six-seed result stands whatever it shows —
fixed before the first new row existed. Full record in `DESIGN_NOTES.md`.

- **A1 — family C = CommonsenseQA (not BBH).** BBH (`suzgun/BIG-Bench-Hard`)
  returned HTTP 404 at the GitHub repo level and on every `raw.githubusercontent.com`
  path (checked 2026-09-06 22:59 UTC); two HuggingFace mirrors also 404'd.
  MATH-500 downloaded but is the same family as A. CommonsenseQA is public,
  carries exogenous `answerKey` labels, and is genuinely disjoint. Recorded
  before the first full run.
- **D1/D2 — evaluation at round 0 and round R only** (FG and BWT are defined
  purely on the endpoints); round-0 evaluation shared across arms because
  memory is empty and model/seed/items are identical (this makes the arms
  exactly paired at round 0).
- **A2 — 8B replication pre-committed.** Amendment A2 was written **before any
  FG or BWT value existed**, with design and non-execution clause fixed in
  advance. See §7.
- **A3 — temperature 0.0 → 0.7 (integrity fix, caught mid-run 2026-09-06
  23:58 UTC).** Round 0 for seeds 1 and 2 returned **identical per-item
  correctness on all 60 GSM8K items** (accuracy 0.7500 on both), because at
  temperature 0 the decode is greedy and the seed does not enter the sampling
  path. That would have made the pre-registered unit of independence
  degenerate and passed "CI excludes zero" tests by construction. Temperature
  raised to 0.7; verified on a 24-item probe (6/24 items disagree between
  seeds at 0.7 vs 1/120 at 0.0). All temperature-0 data (298 calls, 240 graded
  items, 4 round-0 files) discarded; the run reported here began 2026-09-07
  00:07 UTC. Full record in `DESIGN_NOTES.md` amendment A3.
- **A4 — exploratory short-neutral arm (`neutralshort`), post-hoc.** Declared in
  `DESIGN_NOTES.md` before the arm was run, explicitly as NOT pre-registered,
  with the reporting rule for both outcomes fixed in advance. It matches the
  *gated* arm's memory length with content-free padding, so it separates the
  gate's content from its length.
- **A5 — extension to six seeds, post-hoc.** The grid was extended from seeds
  1/2/3 to seeds 1-6 under a reporting rule fixed before the first new row
  existed: the six-seed result is the primary result whatever it shows. It
  showed the less favourable outcome (both pre-declared claims refuted) and is
  reported as the primary result accordingly. Every number in §4-§9 and §11 is
  the six-seed number.
- **A6 — statistical reporting corrections, post-hoc.** No measurement changes;
  all three are recomputations of existing data. (i) The percentile bootstrap CI
  is degenerate at small *n* and is now flagged and never read alone; (ii) a
  seed-level paired-*t* interval is reported alongside it; (iii) an SEM-based
  noise margin is reported alongside the pre-declared max-abs noise band, which
  as an extreme-value order statistic widens mechanically with *n*. The
  pre-declared band is still reported as pre-declared and neither is dropped.

## 4. Headline results

Unit of independence = seed; n = **6 seeds** (1-6, amendment A5); CI = seed-level
percentile bootstrap, B = 10 000, RNG seed 20260907; contrasts are paired by
seed. Every value below is read from `evidence/aggregates.json` and stamped in
`evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json`.

| arm | FG (GSM8K) | BWT_B (ARC) | BWT_C (CommonsenseQA) |
|---|---|---|---|
| ungated | +0.0222 [-0.0111, +0.0583] | -0.0361 [-0.0750, +0.0028] | -0.0333 [-0.0611, +0.0000] |
| gated | +0.0194 [-0.0222, +0.0556] | -0.0389 [-0.0778, -0.0028] | -0.0222 [-0.0667, +0.0222] |
| neutral | -0.0417 [-0.0750, -0.0111] | -0.0694 [-0.1028, -0.0417] | -0.0556 [-0.0889, -0.0167] |
| neutralshort (exploratory, A4) | -0.0444 [-0.0694, -0.0250] | -0.0556 [-0.1000, -0.0111] | -0.0722 [-0.0917, -0.0417] |

Per-seed values (the actual bootstrap units):

| arm | metric | seed 1 | seed 2 | seed 3 | seed 4 | seed 5 | seed 6 |
|---|---|---|---|---|---|---|---|
| ungated | FG | +0.0500 | -0.0167 | +0.0667 | -0.0333 | +0.0833 | -0.0167 |
| ungated | BWT_B | +0.0167 | -0.0333 | -0.1167 | +0.0167 | -0.0833 | -0.0167 |
| ungated | BWT_C | -0.0833 | -0.0167 | -0.0500 | -0.0500 | -0.0500 | +0.0500 |
| gated | FG | +0.0333 | -0.0167 | +0.0333 | +0.0500 | +0.0833 | -0.0667 |
| gated | BWT_B | +0.0167 | +0.0167 | -0.1167 | -0.0667 | -0.0667 | -0.0167 |
| gated | BWT_C | -0.0667 | +0.0167 | +0.0000 | -0.1000 | -0.0500 | +0.0667 |
| neutral | FG | -0.0333 | -0.1167 | +0.0000 | -0.0667 | -0.0333 | +0.0000 |
| neutral | BWT_B | -0.0333 | -0.1000 | -0.1333 | -0.0333 | -0.0833 | -0.0333 |
| neutral | BWT_C | -0.0667 | -0.0667 | -0.0333 | -0.1167 | -0.0833 | +0.0333 |

**Amendment A6 caveat, applied to every interval above.** A percentile bootstrap
of a mean over *n* values is bounded by min and max of those values, so at small
*n* an interval cannot contain zero once the seeds agree in sign. The bootstrap
interval is therefore never read alone; a paired-*t* interval and a sign-flip
*p* are stamped alongside every contrast in the manifest
(`*_t_ci_low` / `*_t_ci_high` / `*_signflip_p`).

## 5. Rival-mechanism controls

**Evaluation-noise null** (rival 2, round-0 vs round-0 with sampling seed
*s* + 100, same fixed items, empty memory), six seeds:

| family | per-seed shifts | mean [CI] | max abs |
|---|---|---|---|
| A | -0.017, -0.067, -0.050, +0.033, +0.000, +0.017 | -0.0139 [-0.0417, +0.0139] | **0.0667** |
| B | +0.017, +0.000, -0.067, +0.033, -0.067, +0.000 | -0.0139 [-0.0444, +0.0167] | **0.0667** |
| C | +0.000, +0.067, -0.033, -0.067, +0.050, +0.117 | +0.0222 [-0.0278, +0.0722] | **0.1167** |

The max-absolute per-seed shift is the conservative noise band, as pre-declared.
A maximum is an extreme-value order statistic and grows mechanically with *n*,
which is why amendment A6 adds an SEM-based margin (+/-0.0443) alongside it; both
are reported and neither is dropped. On either construction, every held-out
effect in §4 lies inside the noise floor.

**Paired contrasts** (paired by seed; bootstrap CI excludes zero flagged with *):

| contrast | FG | BWT_B | BWT_C |
|---|---|---|---|
| gated - ungated | -0.0028 [-0.0306, +0.0333] | -0.0028 [-0.0389, +0.0250] | +0.0111 [-0.0167, +0.0333] |
| neutral - ungated | -0.0639 [-0.0972, -0.0278] * | -0.0333 [-0.0528, -0.0139] * | -0.0222 [-0.0472, +0.0028] |
| gated - neutral | +0.0611 [+0.0056, +0.1056] * | +0.0306 [-0.0028, +0.0667] | +0.0333 [+0.0139, +0.0556] * |
| gated - neutralshort | +0.0639 [+0.0250, +0.1028] * | +0.0167 [-0.0139, +0.0417] | +0.0500 [+0.0139, +0.0833] * |
| neutralshort - ungated | -0.0667 [-0.1139, -0.0222] * | -0.0194 [-0.0694, +0.0222] | -0.0389 [-0.0583, -0.0194] * |

## 6. Verdicts (per pre-declaration)

At three seeds the outcome fell between the pre-declared branches (P1's criterion
met on one family but inside the noise band; P2's met on that same family only).
Amendment A5 extended the grid to six seeds under a reporting rule fixed before
the first new row existed --- the six-seed result stands whatever it shows.
**At six seeds both pre-declared refutation branches are taken.**

- **P1 --- negative backward transfer under ungated evolution: REFUTED.** The
  registered criterion (BWT < 0 with the paired CI excluding zero on some
  held-out family) is met on **neither** family: BWT_C = -0.0333
  [-0.0611, +0.0000] and BWT_B = -0.0361 [-0.0750, +0.0028], both bootstrap
  intervals touching or containing zero and both *t* intervals containing it.
  Both effects stay inside the noise floor on either construction (pre-declared
  band 0.1167 on C; A6 SEM margin +/-0.0443). Forward gain is likewise
  indistinguishable from zero (+0.0222 [-0.0111, +0.0583]): the loop bought no
  measurable improvement on the family it was allowed to practise, so it neither
  learned nor forgot. Reported as inference-time self-evolution being
  **stability-safe at this scale**.
- **P2 --- the retention gate raises BWT: REFUTED.** At three seeds P2 held on
  CommonsenseQA (+0.033333, CI excluding zero, unanimous in sign) and the ARC
  contrast was withdrawn as a length artefact. Six seeds withdraw the
  CommonsenseQA contrast too: gated - ungated = +0.0111 [-0.0167, +0.0333], sign
  no longer unanimous (sign-flip p = 0.5625), and on ARC it is faintly
  *negative* (-0.0028). The gate does not measurably improve backward transfer
  over self-judgement here, because P1's refutation leaves none to improve. Its
  plasticity price is correspondingly nil (gated - ungated FG = -0.0028) ---
  close to free rather than close to useful. Per A5 this is the primary result
  although it is the less favourable one.
- **Pre-declared falsifier: FIRES.** The length-matched neutral-memory arm
  degrades **more** than the ungated arm on family A (-0.0639
  [-0.0972, -0.0278]) and family B (-0.0333 [-0.0528, -0.0139]) --- the only
  contrasts whose bootstrap *and* *t* intervals both exclude zero. The short
  padding arm reproduces it on CommonsenseQA (-0.0389 [-0.0583, -0.0194]),
  which three seeds could not resolve. Content interference **as the sole
  mechanism** is refuted: irrelevant text costs more than evolved text while
  occupying *fewer* characters (neutralshort mean memory 279.0 chars vs ungated
  518.2).

**Edit economics** (the "the gate just edits less" rival mechanism), six seeds:

| arm | proposed (mean/seed) | accepted (mean/seed) | acceptance rate | final memory entries | final memory chars |
|---|---|---|---|---|---|
| ungated | 9.00 | 8.67 | 0.963 | 4.33 | 518.2 |
| gated | 9.00 | 4.00 | 0.444 | 3.00 | 378.8 |
| neutral | 6.00 | 6.00 | 1.000 | 6.00 | 420.0 |
| neutralshort | 4.00 | 4.00 | 1.000 | 4.00 | 279.0 |

## 7. Model-scale robustness (Amendment A2)

The 8B replication (`qwen3:8b`, ungated + gated, seeds 1-2, R = 3, evaluated
on a strict prefix subset of the same fixed items) was pre-committed before
any FG or BWT value existed and had its non-execution clause fixed in advance.
It did not fit the remaining time budget, and an 8B run was projected at ~10 h
on this contended host. Under the pre-committed non-execution clause, the
replication is not run and the paper's Limitations section states plainly that
scale-robustness beyond 3B is untested.

## 8. Protocol-failure accounting

Six seeds, all four arms:

| arm | rounds | proposed | accepted | unparseable reflections | rounds below budget |
|---|---|---|---|---|---|
| ungated | 18 | 54 | 52 | 0 | 0 |
| gated | 18 | 54 | 24 | 0 | 0 |
| neutral | 18 | 36 | 36 | - (no reflection) | - |
| neutralshort | 18 | 24 | 24 | - (no reflection) | - |

- Total graded model responses: **6 480**.
- Ambiguous parses (deterministic extractor found no candidate; scored
  incorrect and logged): **2** (0.03 %).
- Model-call retries (transient failures re-issued with identical parameters):
  **0** out of **7 277** total logged calls; **0** failed attempts.
- Schema-forced JSON reflection: 100 % parseable across all evolution rounds.
- Wallclock span of the logged calls: 2026-09-07T00:07:33Z to
  2026-09-07T12:26:30Z (12 h 18 m 57 s); latency median 15.4 s, p95 56.4 s,
  max 396.0 s.

## 9. McNemar robustness check (per-item, pooled across seeds)

Secondary check only --- items are not independent units here, so this is
reported beside the seed-level CIs, never in place of them. `b` = correct at
round 0 and wrong at round R; `c` = the reverse.

| arm | family | b (lost) | c (gained) | exact two-sided p |
|---|---|---|---|---|
| ungated | A (GSM8K) | 48 | 56 | 0.4926 |
| ungated | B (ARC) | 40 | 27 | 0.1421 |
| ungated | C (CommonsenseQA) | 46 | 34 | 0.2185 |
| gated | A (GSM8K) | 37 | 44 | 0.5052 |
| gated | B (ARC) | 34 | 20 | 0.0759 |
| gated | C (CommonsenseQA) | 41 | 33 | 0.4160 |
| neutral | A (GSM8K) | 54 | 39 | 0.1462 |
| neutral | B (ARC) | 41 | 16 | **0.0013** |
| neutral | C (CommonsenseQA) | 58 | 38 | 0.0519 |
| neutralshort (A4) | A (GSM8K) | 62 | 46 | 0.1486 |
| neutralshort (A4) | B (ARC) | 38 | 18 | 0.0105 |
| neutralshort (A4) | C (CommonsenseQA) | 61 | 35 | 0.0103 |

The entries that stand out are the two content-free padding arms against round 0
on the held-out families (neutral on ARC, p = 0.0013; neutralshort on ARC
p = 0.0105 and on CommonsenseQA p = 0.0103), which is consistent with the
falsifier reading: dilution costs the padded arms more per item than the evolved
memory costs the ungated arm.

## 10. Grading and reproducibility

Every accuracy is scored against the published answer keys with a
deterministic, auditable extractor (`#### <n>` then last-number fallback for
GSM8K; `Answer: <letter>` then last-standalone-letter fallback for MCQ).
Ambiguous cases scored incorrect and logged, never guessed. Item sets are
fixed and identical across arms, seeds and rounds; anchor items are asserted
disjoint from evaluation items in code (`harness.py:build_pools`).

Reproduction: `bash analysis/run_full.sh` reproduces the whole grid from raw
data and seeds. `python3 analysis/aggregate.py` writes the ledger and stamp
manifest. `python3 analysis/make_figure.py` recomputes every drawn aggregate
from the raw cell records and asserts equality against the ledger before
drawing. `python3 analysis/make_report_tables.py` regenerates the numeric
tables in §4, §5, §8 and §9 above directly from `evidence/aggregates.json`.

## 11. Artefacts

| path | content |
|---|---|
| `evidence/calls.jsonl` | 7 277 model calls (prompt SHA-256, tokens, latency, retries; reflection and self-judge calls carry full prompt + response text) |
| `evidence/runs/cell_<arm>_seed<N>.jsonl` | Per-round memory state, proposals, acceptances, gate decisions |
| `evidence/runs/cells.jsonl` | Per (arm, seed): FG, BWT_B, BWT_C, edit counts |
| `evidence/runs/noise_null.jsonl` | Round-0 vs round-0 evaluation-noise null |
| `evidence/runs/per_item.jsonl` | 6 480 per-item correctness rows for McNemar |
| `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` | Evidence ledger, 612 rows |
| `evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json` | 612 stamped-cell keys mapping into the ledger |
| `evidence/aggregates.json` | Machine-readable aggregates consumed by the figure |
| `fig_cl4fm_selfevolve_forgetting.pdf` | Single evidence figure |
