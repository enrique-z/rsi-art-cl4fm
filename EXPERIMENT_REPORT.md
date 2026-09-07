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
temperature 0.7 (see A3 below).

**A material infrastructure finding.** The machine's default Ollama server is
shared with other jobs on this host; single requests to it took 414 s and 622 s
for ~75 output tokens (queueing, not compute). Every number in this paper comes
from a **dedicated Ollama instance** started for this experiment on port 11500.

## 3. Deviations and amendments (all pre-committed before affected data existed)

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

## 4. Headline results

Unit of independence = seed; CI = seed-level percentile bootstrap, B = 10 000,
RNG seed 20260907; contrasts are paired by seed.

| arm | FG (GSM8K) | BWT_B (ARC) | BWT_C (CommonsenseQA) |
|---|---|---|---|
| ungated | +0.0333 [-0.0167, +0.0667] | -0.0444 [-0.1167, +0.0167] | -0.0500 [-0.0833, -0.0167] |
| gated   | +0.0167 [-0.0167, +0.0333] | -0.0278 [-0.1167, +0.0167] | -0.0167 [-0.0667, +0.0167] |
| neutral | -0.0500 [-0.1167, +0.0000] | -0.0889 [-0.1333, -0.0333] | -0.0556 [-0.0667, -0.0333] |

## 5. Rival-mechanism controls

**Evaluation-noise null** (rival 2, round-0 vs round-0 with sampling seed
*s* + 100, same fixed items, empty memory):

| family | per-seed shifts | mean [CI] | max\|Δ\| |
|---|---|---|---|
| A | -0.017, -0.067, -0.050 | -0.0444 [-0.0667, -0.0167] | **0.0667** |
| B | +0.017, +0.000, -0.067 | -0.0167 [-0.0667, +0.0167] | **0.0667** |
| C | +0.000, +0.067, -0.033 | +0.0111 [-0.0333, +0.0667] | **0.0667** |

The max-absolute per-seed shift is used as the conservative noise band, as
pre-declared. On every family the noise band is 0.0667, so any observed
|Δ| ≤ 0.0667 is not distinguishable from evaluation noise.

**Paired contrasts** (paired by seed; CI excludes zero flagged with ✱):

| contrast | FG | BWT_B | BWT_C |
|---|---|---|---|
| gated − ungated | -0.0167 [-0.0333, +0.0000] | +0.0167 [+0.0000, +0.0500] | +0.0333 [+0.0167, +0.0500] ✱ |
| neutral − ungated | -0.0833 [-0.1000, -0.0667] ✱ | -0.0444 [-0.0667, -0.0167] ✱ | -0.0056 [-0.0500, +0.0167] |
| gated − neutral | +0.0667 [+0.0333, +0.1000] ✱ | +0.0611 [+0.0167, +0.1167] ✱ | +0.0389 [+0.0000, +0.0833] |

## 6. Verdicts (per pre-declaration)

- **P1 — negative backward transfer under ungated evolution: NOT ESTABLISHED
  at this scale.** BWT_B CI includes zero; BWT_C CI nominally excludes zero
  (−0.0500 [-0.0833, -0.0167]) but its magnitude does not clear the
  pre-registered noise band (0.0667). Forward gain is also indistinguishable
  from zero (+0.0333 [-0.0167, +0.0667]) — the loop bought no measurable
  improvement on the family it was allowed to practise.
- **Pre-declared falsifier: FIRES IN STRONG FORM.** The length-matched
  neutral-memory arm degrades **more** than the ungated arm on family A
  (contrast −0.0833 [-0.1000, -0.0667], CI excludes zero) and family B
  (−0.0444 [-0.0667, -0.0167], CI excludes zero). Content interference is
  refuted; the retention cost is **context dilution**, and the evolved
  content of the ungated arm partially **offsets** that dilution rather than
  causing it.
- **P2 — the retention gate raises BWT: PARTIALLY HOLDS.** gated − ungated on
  BWT_C is +0.0333 [+0.0167, +0.0500] (CI excludes zero); on BWT_B it is
  +0.0167 [+0.0000, +0.0500] (CI touches zero). The plasticity price is not
  measurable (gated − ungated FG = -0.0167 [-0.0333, +0.0000]). Part of the
  benefit is that the gate keeps memory smaller (3.0 vs 8.67 accepted edits
  per seed, mean); the gated − neutral row separates the gate from length
  alone (FG +0.0667 ✱; BWT_B +0.0611 ✱).

## 7. Model-scale robustness (Amendment A2)

The 8B replication (`qwen3:8b`, ungated + gated, seeds 1–2, R = 3, evaluated
on a strict prefix subset of the same fixed items) was pre-committed before
any FG or BWT value existed and had its non-execution clause fixed in advance.
It did not fit the remaining time budget: the 3B grid alone took 4.4 h (with
retries and multiple restarts recorded honestly in `DESIGN_NOTES.md`), and an
8B run was projected at ~10 h on this contended host. Under the pre-committed
non-execution clause, the replication is not run and §Limitations of the paper
states plainly that scale-robustness beyond 3B is untested.

## 8. Protocol-failure accounting

| arm | rounds | proposed | accepted | unparseable reflections | rounds below budget |
|---|---|---|---|---|---|
| ungated | 9 | 27 | 26 | 0 | 0 |
| gated   | 9 | 27 | 9  | 0 | 0 |
| neutral | 9 | 18 | 18 | — (no reflection) | — |

- Total graded model responses: **2 700**.
- Ambiguous parses (deterministic extractor found no candidate; scored
  incorrect and logged): **1** (0.037 %).
- Model-call retries (transient failures re-issued with identical parameters):
  **0** out of **3 098** total logged calls.
- Schema-forced JSON reflection: 100 % parseable across all evolution rounds.

## 9. McNemar robustness check (per-item, pooled across seeds)

Reported beside the seed-level CIs, never in place of them:

| arm | family | b (lost) | c (gained) | exact two-sided p |
|---|---|---|---|---|
| ungated | A | 27 | 33 | 0.519 |
| ungated | B | 21 | 13 | 0.229 |
| ungated | C | 23 | 14 | 0.188 |
| gated   | A | 15 | 18 | 0.728 |
| gated   | B | 14 | 9  | 0.405 |
| gated   | C | 13 | 10 | 0.678 |
| neutral | A | 28 | 19 | 0.243 |
| neutral | B | 24 | 8  | **0.007** |
| neutral | C | 24 | 14 | 0.143 |

The one entry that stands out is neutral vs round 0 on ARC (p = 0.007), which
is consistent with the falsifier reading: dilution costs the neutral arm more
per-item than the evolved memory costs the ungated arm.

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
drawing.

## 11. Artefacts

| path | content |
|---|---|
| `evidence/calls.jsonl` | 3 098 model calls (prompt SHA-256, tokens, latency, retries; reflection and self-judge calls carry full prompt + response text) |
| `evidence/runs/cell_<arm>_seed<N>.jsonl` | Per-round memory state, proposals, acceptances, gate decisions |
| `evidence/runs/cells.jsonl` | Per (arm, seed): FG, BWT_B, BWT_C, edit counts |
| `evidence/runs/noise_null.jsonl` | Round-0 vs round-0 evaluation-noise null |
| `evidence/runs/per_item.jsonl` | 2 700 per-item correctness rows for McNemar |
| `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` | 91 EGCL ledger rows (SUPPORTED verdict) |
| `evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json` | 109 stamped-cell keys mapping into the ledger |
| `evidence/aggregates.json` | Machine-readable aggregates consumed by the figure |
| `fig_cl4fm_selfevolve_forgetting.pdf` | Single evidence figure |
