# DESIGN_NOTES — cl4fm-selfevolve-forgetting

Operational record for the experiment phase. Everything below the "frozen"
line was written **before** the full run and is not edited afterwards; changes
appear only as dated amendments at the bottom.

Binding design: `A2_PREDECLARATION_2026-09-07.md`.

---

## 1. Data sources (REAL, downloaded live 2026-09-06/07)

All files live in `papers/cl4fm-selfevolve-forgetting/data/`. Downloaded with
`curl -sL`, HTTP status recorded, SHA-256 computed on the file as it landed.

| Family | Role | File | URL | HTTP | Bytes | Lines | SHA-256 |
|---|---|---|---|---|---|---|---|
| A | evolution prompts | `gsm8k_train.jsonl` | `https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl` | 200 | 4166206 | 7473 | `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465` |
| A | evaluation | `gsm8k_test.jsonl` | `https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl` | 200 | 749738 | 1319 | `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14` |
| B | held-out eval + anchor | `arc.zip` → `arc_extract/ARC-V1-Feb2018-2/ARC-Challenge/ARC-Challenge-Test.jsonl` | `https://ai2-public-datasets.s3.amazonaws.com/arc/ARC-V1-Feb2018.zip` | 200 | 680841265 (zip) | 1172 (test) | zip `6d2d5ab50b2ceec6ba5f79c921be77cf2de712ea25a2b3f4fff3acc101cecfa0`; test jsonl `9fa8ffb3e3a1f88cb302d53dd95aae81e39209ad9bcf974376b319d8fd35717c` |
| C | held-out eval + anchor | `csqa_dev.jsonl` | `https://s3.amazonaws.com/commensenseqa/dev_rand_split.jsonl` | 200 | 471653 | 1221 | `3210497fdaae614ac085d9eb873dd7f4d49b6f965a93adadc803e1229fd8a02a` |
| — | downloaded, NOT used (see amendment A1) | `math500_test.jsonl` | `https://huggingface.co/datasets/HuggingFaceH4/MATH-500/resolve/main/test.jsonl` | 200 | 446564 | 500 | `35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132` |

Download timestamp: 2026-09-06, 22:57–23:00 UTC. Checksums computed
2026-09-06 23:02 UTC with `shasum -a 256`.

No item in any family is authored, edited or synthesised here. Labels are the
published exogenous answer keys (`#### <n>` for GSM8K, `answerKey` for ARC and
CommonsenseQA).

### Amendment A1 (recorded before the full run) — family C source

The pre-declaration named "BBH subset or MATH-500 subset" as candidate
family C. **BBH is unobtainable**: `github.com/suzgun/BIG-Bench-Hard` returns
`404` from the GitHub API (`GET /repos/suzgun/BIG-Bench-Hard` → 404) and every
`raw.githubusercontent.com` path under `main` and `master` returns 404
(checked 2026-09-06 22:59 UTC). Two HuggingFace mirrors (`lukaemon/bbh`,
`Joschka/big_bench_hard`) also 404'd on their parquet paths.

MATH-500 downloads fine (row above) but is the **same task family as A**
(competition mathematics vs grade-school mathematics), which defeats the
purpose of a *disjoint* held-out family and would confound negative backward
transfer with near-transfer.

Substituted: **CommonsenseQA** (Talmor et al. 2019), AI2's own
`dev_rand_split.jsonl`, which is public, carries exogenous `answerKey` labels,
and is a genuinely different reasoning family (commonsense association) from
both A (arithmetic word problems) and B (grade-school science). This is a
deviation from the pre-declaration's *examples*, not from its *requirement*
("a second reasoning family disjoint from A ... exact choice and item counts
recorded in evidence/DESIGN_NOTES.md before the first full run"). It is
recorded here before the first full run, as required.

---

## 2. Infrastructure

Local Ollama, Apple Silicon, Metal backend.

**Contention finding (material, and it drove the model choice).** The machine's
default Ollama server on `:11434` is **shared with other jobs on this host**.
During the pilot its server log showed a foreign client submitting 4 000–7 800
token prompts and a `POST /api/chat` returning `500` after a 5-minute timeout;
system load average peaked at 470 with a 12-worker multiprocessing pool from an
unrelated job saturating every core. Single requests issued to `:11434` took
414 s and 622 s wallclock for 72 and 82 output tokens respectively — queueing,
not compute.

Mitigation, applied before the throughput pilot: a **dedicated Ollama server
instance for this paper** on `127.0.0.1:11500`
(`OLLAMA_NUM_PARALLEL=4`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=24h`),
sharing the same on-disk model blobs but with its own scheduler and its own
KV-cache slots. All numbers in this paper come from `:11500`. The harness
default endpoint is `http://127.0.0.1:11500` (`CL4FM_OLLAMA` overrides).

---

## 3. Smoke test and throughput pilot (STEP 1 — completed before the full run)

**60-second smoke test.** One real `/api/chat` call, one GSM8K test item scored
end to end.

- `qwen3:8b`, `"think": false` — returned `... #### 72`, gold `72`, **graded
  correct**; 82 output tokens. Confirms non-thinking mode works: no
  `<think>` block in the response body.
- `llama3.2:3b` — returned `... 48 + 24 = 72`, gold `72`, **graded correct**
  via the last-number fallback; 72 output tokens.

Both on `:11434` under contention, hence the wallclock figures above are
queueing-dominated and are not used for planning.

**Throughput pilot on the dedicated `:11500` instance** (2026-09-06 23:12–23:20 UTC):

| workload | model | pool | N | wall | s/item | items/s | accuracy | mean output tokens |
|---|---|---|---|---|---|---|---|---|
| GSM8K test, CoT, `num_predict=320` | `llama3.2:3b` | 4 | 12 | 81.2 s | 6.77 | 0.148 | 0.500 | 167 |
| ARC-Challenge MCQ, `num_predict=140` | `llama3.2:3b` | 8 | 24 | 51.8 s | 2.16 | 0.464 | 0.833 | 46 |

Model warm-load: 7.0 s.

### Model choice — `llama3.2:3b` (a pre-declared option)

The pre-declaration says: *"primary `qwen3:8b`, non-thinking mode; fallback
`llama3.2:3b` if throughput demands — the pilot decides and the choice is
recorded before the full run."* The pilot decides `llama3.2:3b`.

Reason: `qwen3:8b` is a 5.2 GB model against `llama3.2:3b`'s 2.0 GB and, in the
smoke test, produced 82 tokens where `llama3.2:3b` produced 72 for the same
item at roughly 1.5× the per-token cost; scaling the measured `llama3.2:3b`
budget below by the parameter ratio puts the full run at roughly 9–10 h on a
host that is already contended by other jobs and has shown 5-minute request
timeouts. `llama3.2:3b` brings the full run to ~3 h, leaving headroom for a
re-run if a cell fails. Its pilot accuracies (0.50 on A, 0.83 on B) sit away
from both floor and ceiling, so both forward gain and backward loss are
measurable.

### Throughput arithmetic for the frozen configuration

Call counts implied by §4, split by cost class:

- GSM8K-class calls (`num_predict` 320, 0.148 items/s):
  round-0 eval 3 seeds × 60 = 180; round-R eval 3 arms × 3 seeds × 60 = 540;
  ungated attempts 3 × 3 × 6 = 54; gated attempts + gate probes
  3 × 3 × (6 + 2 × 6) = 162. Total 936 → **6 324 s**.
- MCQ-class calls (`num_predict` 140, 0.464 items/s):
  round-0 eval 3 seeds × 120 = 360; round-R eval 3 × 3 × 120 = 1 080;
  gated anchor probes 3 × 3 × (2 × 8) = 144. Total 1 584 → **3 414 s**.
- Reflection calls (`num_predict` 500, long prompt): 2 arms × 3 seeds ×
  3 rounds = 18 → **~270 s**. Self-judge calls (`num_predict` 8):
  ≤ 3 seeds × 3 rounds × 3 = 27 → **~30 s**.

Predicted total **≈ 10 000 s ≈ 2.8 h**, plus growth in prompt length as memory
fills (bounded above by 9 entries ≈ 900 tokens ≈ +20 %) ⇒ **≈ 3.4 h**, inside
the ≤ 8 h budget. The neutral arm costs no evolution calls, only its
round-R evaluation, already counted.

---

## 4. Frozen configuration (`analysis/config_full.json`)

Written **before** the first full run.

| parameter | value | note |
|---|---|---|
| model | `llama3.2:3b` | pilot decision above |
| temperature | 0.0 | fixed; seeds carry the sampling variation |
| seeds | 1, 2, 3 | unit of independence = seed; ≥ 3 as pre-declared |
| rounds R | 3 | pre-declared minimum |
| eval items, family A | **60** | GSM8K test; pre-declared floor of ≥ 60 |
| eval items, family B | **60** | ARC-Challenge test |
| eval items, family C | **60** | CommonsenseQA dev |
| evolution items / round | 6 | GSM8K **train** (disjoint from A-test by split) |
| edit proposal budget / round | 3 | **identical in every arm** |
| gate probe set (family A) | 6 | GSM8K train tail, disjoint from evolution items |
| rehearsal anchor set | 4 ARC + 4 CSQA | **disjoint from the B and C evaluation items** — asserted in code (`build_pools`) |
| item selection | `random.Random(20260907).shuffle` then take the first n | same items for every arm, seed and round |

Item sets are **fixed and identical across arms, seeds and rounds**, as
pre-declared.

### Deviation D1 — evaluation points

The pre-declaration says "Evaluation at round 0 and after every round".
The frozen configuration evaluates at **round 0 and after round R = 3 only**.

Rationale, pre-committed: FG and BWT are defined purely on the endpoints
(`FG = acc_A(R) − acc_A(0)`, `BWT_X = acc_X(R) − acc_X(0)`), so no
pre-registered quantity is lost. Evaluating after every round would multiply
the evaluation cost by 3 (2 160 → 6 480 GSM8K-class-equivalent calls) and push
the run past the deadline on a contended host. What is lost is the
*intermediate trajectory*, which is descriptive only; the paper will not claim
anything about per-round dynamics.

### Deviation D2 — round-0 evaluation is computed once per seed

At round 0 the memory is empty in **every** arm, the model, the seed, the
temperature and the item set are identical, so `acc_X(0)` is by construction
the same measurement for all three arms. It is therefore computed once per
seed and shared. This is not an approximation; it is the same call that would
otherwise be made three times. It also makes the arms *exactly* paired at
round 0, which strengthens the paired-by-seed contrasts.

---

## 5. Operational definitions

**Memory.** An ordered list of short natural-language strings. It is rendered
verbatim into the prompt above the question, under a fixed header
(`harness.py:MEM_HEADER`). Nothing else about the model changes between rounds:
no weight updates, no fine-tuning, no retrieval index. Round 0 = empty memory.

**A round** (arms `ungated`, `gated`): the agent attempts `n_A_train = 6`
GSM8K **train** items with its current memory → is shown its own answers
alongside the exogenous gold answers → proposes at most `edit_budget = 3`
memory edits as a JSON array of `{"op":"add","text":...}` /
`{"op":"delete","index":...}` → edits are filtered by the arm's accept rule →
survivors are applied.

**Accept rule, `ungated`.** For each proposed *add*, the model is asked a
single self-judgement question (`harness.py:SELFJUDGE`) and the edit is kept
iff the reply contains `KEEP`. Proposed *deletes* are accepted unconditionally.
No exogenous signal is consulted.

**Accept rule, `gated`.** The whole proposed edit set is applied to a candidate
memory, and the candidate is accepted **iff both**: (i) accuracy on a fixed
6-item family-A probe set is `>=` its value under the current memory, and
(ii) accuracy on the fixed 8-item rehearsal anchor set (4 ARC + 4
CommonsenseQA, **disjoint from the evaluation items**) is `>=` its value under
the current memory. Otherwise the round's edits are all rejected. Both
comparisons are recomputed under the current memory in the same round, so the
gate never compares against a stale baseline. Every gate decision is written to
`evidence/runs/cell_gated_seed<N>.jsonl` with all four accuracies.

**Accept rule, `neutral`.** No attempts, no reflection, no judgement. The
memory is padded each round with well-formed but task-irrelevant sentences
(`harness.py:NEUTRAL_POOL`, 30 factual sentences about geography, materials,
instruments and natural history) until it reaches the character count the
**ungated** arm actually reached at that round. This isolates context dilution
from content interference — the pre-declared gate-13b falsifier. The per-round
character targets are measured from the completed ungated cells by
`analysis/set_neutral_target.py` and written back into the config, so
"length-matched" means matched to observed data.

**Answer extraction (deterministic, auditable — `harness.py:extract_numeric`,
`extract_mcq`).**
- Numeric (family A): first try `#### <number>`; if absent, take the **last**
  number in the reply. Comparison is numeric with tolerance 1e-6 against the
  published `####` gold.
- MCQ (families B, C): first try `Answer: <letter>`; if absent, take the last
  standalone `A`–`E` that is one of the item's own option labels. Comparison is
  exact string equality against the published `answerKey`.
- If neither rule yields a candidate, the item is recorded with
  `"ambiguous": true`, `"pred": null` and **scored incorrect**. Ambiguous
  parses are counted and reported (`global::n_ambiguous`); they are never
  guessed at and never silently dropped.
- Which rule fired is recorded per item as `parse_mode`
  (`hash` / `lastnum` / `answerkw` / `lastletter` / `none`).

ARC items whose option labels are not a subset of `A`–`E`, or whose
`answerKey` is not among their own labels, are filtered out of the pool before
sampling (a handful of ARC items use `1`–`4`); this keeps the answer space
fixed and is applied identically to every arm.

**Metrics.** `FG = acc_A(R) − acc_A(0)`; `BWT_X = acc_X(R) − acc_X(0)` for
X ∈ {B, C}. Unit of independence = **seed**. 95 % CIs by percentile bootstrap
over the seed vector, B = 10 000, bootstrap RNG seed 20260907. Arm contrasts
are formed **paired by seed** (per-seed difference, then bootstrap the
difference vector). Per-item correctness is logged for every evaluation so an
exact two-sided McNemar can be computed as a robustness check; McNemar pools
items across seeds and is therefore reported as a secondary check only, never
as the primary inference.

**Every model call is logged** to `evidence/calls.jsonl`: UTC timestamp, tag
(arm/seed/round/purpose), model id, seed, `num_predict`, temperature,
SHA-256 of the exact prompt, prompt length, wallclock latency, server-reported
prompt and output token counts, and any error.

**Checkpointing.** Every `(arm, seed)` cell writes `cell_<arm>_seed<N>.jsonl`
as it goes and a `done_<arm>_seed<N>.json` sentinel when complete; round-0
results write `r0_seed<N>_<fam>.done`. Re-invoking the harness skips completed
cells. A crash loses at most the cell in flight.

---

## 6. Pre-run implementation pilot on the proposal mechanism (before the frozen run)

A mini end-to-end run (1 seed, 2 rounds, 4 eval items per family) exposed two
defects in the edit-proposal step. Both were fixed **before** the frozen run;
both fixes are recorded here because they change what the agent is able to
propose, and therefore the strength of the treatment.

**Defect 1 — invalid deletes starve the budget.** With an *empty* memory the
model answered the reflection prompt with three `{"op":"delete","index":k}`
objects for indices that do not exist. The parser discarded all three (correctly
— they are unresolvable) and the round accepted zero edits. The proposal budget
was thus being spent on impossible operations, and it would have been spent
differently in different arms by accident rather than by design. Fix: the
delete op is offered **only when the memory is non-empty**
(`REFLECT` vs `REFLECT_WITH_DELETE`).

**Defect 2 — malformed JSON.** The model emitted near-JSON
(`["rule": "...", "rule": "..."]`) that no parser can read, again silently
zeroing the round's proposals. Fix: the reflection call now uses Ollama's
**structured-output mode** with an explicit schema (`harness.py:EDIT_SCHEMA`,
an object with an `edits` array of `{op, text?, index?}`), so the shape is
enforced at decode time rather than hoped for. The parser still accepts a bare
array as a fallback and still reports `no_json` / `bad_json` / `not_list`
per round in `parse_status`, so a future failure is visible rather than silent.

After both fixes, a verification probe returned exactly `edit_budget = 3`
well-formed edits from an empty memory and 3 from a non-empty memory
(2 adds + 1 valid delete). The proposal budget is therefore identical and
fully spendable in the `ungated` and `gated` arms, as pre-declared.

The reflection prompt is otherwise unchanged across arms: **the arms differ
only in the accept rule.** The self-judgement call is not schema-constrained
(it is a one-word KEEP/DROP reply; the pilot returned `'KEEP.'`).

---

## 7. Pre-declared rival mechanism 2 — the evaluation-noise null

The pre-declaration lists three rival mechanisms. Rival 1 (scaffold length) is
the `neutral` arm. Rival 3 (gate = fewer edits) is the acceptance-rate and
matched-accepted-edit reporting. Rival 2 is **evaluation noise**: *"BWT within
sampling noise. Test: round-0 vs round-0 re-evaluation with a different seed
gives the null distribution."*

Implementation (`harness.py --noise-null`, step 5 of `analysis/run_full.sh`):
for each seed *s*, the **same fixed item sets** are re-evaluated with the
**same empty memory** under sampling seed *s + 100*. The per-family difference

    noise_X(s) = acc_X(empty, seed s+100) − acc_X(empty, seed s)

is a draw from the null distribution of the FG and BWT statistics under
"the accuracy moved but nothing was learned". It is aggregated exactly like the
treatment effects — mean over seeds, seed-level bootstrap CI, plus the largest
absolute per-seed shift — and any measured |FG| or |BWT| that does not clear
this band is reported as indistinguishable from evaluation noise.

The offset of 100 is arbitrary and fixed in advance; it only has to produce a
different sampling stream from any experimental seed (1–3).

## 8. Protocol-failure accounting

A 3-billion-parameter model is being asked to emit schema-constrained JSON and
to follow an answer-format instruction. How often it fails is a **finding**, not
an embarrassment to be dropped. The following are counted and enter the ledger:

- `global::n_ambiguous` — graded responses where the deterministic extractor
  found no candidate answer at all. Scored incorrect; never guessed.
- `protocol::<arm>_unparseable` — reflection replies whose edit list could not
  be parsed (`no_json` / `bad_json` / `not_list`).
- `protocol::<arm>_below_budget` — rounds in which the model proposed fewer
  edits than the budget allowed (budget starvation).
- `global::n_model_calls`, `global::n_failed_calls` — total call attempts and
  attempts that raised. Failures are retried with **identical** parameters
  (same seed, same prompt, same `num_predict`), so a retry cannot change what
  is measured; the retry count is logged per call as `attempt`.

---

*Frozen 2026-09-06 23:33 UTC, before the first full run.*

**Run history (honest record).** The grid was started four times. Every restart
deleted `evidence/calls.jsonl` and `evidence/runs/` first, so no data from an
abandoned start survives or enters the ledger.

| start | time (UTC) | why it was abandoned |
|---|---|---|
| 1 | 2026-09-06 23:34 | killed after ~4 min to add bounded retry around the model call, so a transient failure on this contended host cannot destroy a whole cell |
| 2 | 2026-09-06 23:38 | killed after ~3 min to add the evaluation-noise null step (rival mechanism 2) |
| 3 | 2026-09-06 23:41 | killed after ~17 min — **integrity fix**: the temperature-0 seed-inertness described in amendment A3. 4 round-0 family evaluations had completed; all discarded |
| **4** | **2026-09-07 00:07** | **the run reported in this paper** |

Pilot-phase calls (smoke test, throughput measurement, prompt probes, and the
temperature verification probe of amendment A3) are retained separately in
`evidence/pilot/` and are never mixed into the run ledger.

---

## Amendments after the frozen line

### Amendment A3 — temperature 0.0 → 0.7 (integrity fix, found mid-run 2026-09-06 23:58 UTC)

**What was wrong.** The frozen configuration set `temperature = 0.0`. The
pre-declaration says *"Temperature fixed; seeds control sampling"* and names the
**seed** as the unit of independence. At temperature 0 the decode is greedy, so
the seed controls nothing — it never enters the sampling path.

**How it was caught.** When round 0 completed for seeds 1 and 2, the per-item
correctness vectors were compared directly rather than trusted:

| family | items compared | items where seed 1 and seed 2 disagree |
|---|---|---|
| A (GSM8K) | 60 | **0** |
| B (ARC-Challenge) | 60 | **1** |

Both seeds returned accuracy exactly 0.7500 on family A, on the same 60 items,
item for item. The single family-B disagreement is float non-determinism from
parallel batching on Metal, not sampling.

**Why this had to be fixed rather than reported.** With ≈0 variance between
seeds, a seed-level bootstrap CI collapses toward a point. Every pre-registered
"CI excludes zero" test would then have been passed *by construction*: a
near-zero-width interval around any non-zero mean excludes zero. That is a
fabricated significance claim, and it would have passed the stamped-cell guard
silently, because every individual number would still have traced correctly to a
real ledger row backed by real model calls. This is precisely the failure mode
a known design trap — a bootstrap whose clustering
argument is not actually doing anything.

**The fix.** `temperature = 0.7` for every call, in every arm, for every family.
The seed now genuinely controls sampling, which is what the pre-declaration
requires. "Temperature fixed" is still satisfied — it is fixed at 0.7
everywhere; only the value changed, not its constancy. Item sets remain fixed
and identical across arms, seeds and rounds, so the paired-by-seed contrasts are
unaffected.

**Verified empirically before the restart**, on a 24-item probe (12 GSM8K +
12 ARC) drawn from the same fixed pools, run twice with seeds 1 and 2:

| temperature | items compared | items where seed 1 and seed 2 disagree |
|---|---|---|
| 0.0 | 120 (60 A + 60 B, from the discarded round 0) | 1 (0.8 %) |
| 0.7 | 24 (12 A + 12 B) | **6 (25 %)** |

The seed now moves the sampling. (Both seeds happened to score 0.7917 on that
small probe; equal *accuracy* on 24 items is unremarkable — what matters is that
the per-item vectors differ, which is what creates genuine between-seed
variance.)

**Consequences accepted.** Accuracy sits lower than the temperature-0 round-0
values (A 0.750, B 0.783, C 0.800 — **superseded, and used nowhere**), and
per-seed variance is now real rather than zero, which **widens** every CI.
Wider honest intervals are the correct outcome. The fix also makes the
evaluation-noise null of §7 meaningful: at temperature 0 that null would have
been identically zero and rival mechanism 2 would have been untestable.

**Data discarded.** All output collected under temperature 0 (298 calls,
240 graded items, 4 completed round-0 family evaluations) was deleted before the
restart and enters neither the ledger nor the report.

### Amendment A2 — model-scale robustness replication (pre-committed 2026-09-06 23:45 UTC, BEFORE any result was visible)

The main grid runs at 3 B parameters. A reviewer will reasonably ask whether any
effect is an artefact of a model too weak to follow the memory-edit protocol at
all, rather than a property of self-evolution. A **reduced replication at 8 B**
is therefore pre-committed here, before the first cell of the main grid has
completed and before any FG or BWT value exists.

Design, fixed now:

- model `qwen3:8b`, `"think": false` (non-thinking mode **verified by
  inspecting the response body**, not assumed — see §3);
- arms `ungated` and `gated` only (the two arms that carry P1 and P2);
- seeds 1 and 2;
- R = 3, same evolution items, same edit budget of 3 — identical protocol;
- evaluation on a **strict prefix subset of the same fixed item sets** used in
  the main grid, so the two models are scored on the same items. The exact
  per-family count is set by a throughput pilot on `qwen3:8b` immediately after
  the main grid finishes, chosen as the largest value that fits a **3 h**
  wallclock budget, and written here before that replication starts.

Reporting rule, fixed now: the replication is reported as a **robustness check
with its own CIs**, never pooled with the 3 B grid and never used to rescue a
3 B result. With 2 seeds its CI is wide and will be presented as such. **If the
replication does not fit the remaining time budget it will not be run, and the
paper's limitations section will state plainly that the result is established
at 3 B and that scale-robustness is untested.** No intermediate outcome — a
partially completed replication, a single seed, a different item set — is
reported as if it were the pre-committed design.

### Amendment A4 — short-neutral arm (EXPLORATORY, declared 2026-09-07 after the primary results were known)

**Status, stated plainly: this is NOT part of the pre-registration.** A2 was
frozen on 2026-09-06 and the primary grid (ungated / gated / neutral + noise
null) completed before this arm was conceived. A4 was added on 2026-09-07 in
response to adversarial review, *after* every FG, BWT and contrast value in the
paper already existed and had been read. Anything it produces is labelled
exploratory in the manuscript and is never described as pre-registered.

**Why it is being run.** The pre-declared `neutral` arm is length-matched to the
**ungated** arm (403.0 realised characters). The `gated` arm holds
258.333333 characters. So `gated - ungated` confounds two differences at once —
the accept rule *and* the realised memory length — and the existing
`gated - neutral` contrast does not resolve it either, because `neutral` is
matched to the wrong arm. Two independent adversarial reviews named this
unidentified confound as the paper's single most likely cause of rejection. The
paper currently concedes the confound; this arm is an attempt to *resolve* it.

**Configuration, fixed before the run.**

- Arm id: `neutralshort` (no underscore: `analysis/aggregate.py` derives the arm
  from `f.name.split("_")[1]`, so an underscore in the arm name would silently
  merge this arm's protocol counters into the pre-declared `neutral` arm).
- Behaviour: byte-identical to the `neutral` arm — task-irrelevant but
  well-formed padding from the same `NEUTRAL_POOL`, no attempts, no reflection,
  no self-judgement — differing ONLY in the per-round character target.
- Per-round cumulative character targets: **[227, 227, 258]**, the mean over the
  three completed `gated` seeds of realised cumulative memory length after each
  round (observed: r1 [393, 0, 289], r2 [393, 0, 289], r3 [393, 0, 382]).
  Written to `analysis/config_full.json` as `neutralshort_target_chars` by
  `analysis/set_neutral_target.py --from-arm gated --key neutralshort_target_chars`.
- Model `llama3.2:3b`, temperature 0.7, seeds [1, 2, 3], R=3, the same fixed
  60-item evaluation sets, and the SAME cached round-0 accuracies
  (`r0_seed*_*.done`) as every other arm — so the new arm is exactly paired at
  the origin with the others and costs no extra round-0 compute.

**The contrast this licenses, and the reporting rule, both fixed now.**
`gated - neutralshort` compares the gated arm against a content-free memory of
the same length. It is the gate's *content* contribution at equal context
occupancy.

- If `gated - neutralshort` is positive with a CI excluding zero: the gate does
  something beyond keeping memory short.
- If it contains zero or is negative: the gate's apparent benefit is **not**
  separable from length, and the honest reading is that the gated arm helps
  mainly by holding a shorter memory. **This outcome will be reported exactly as
  plainly as the favourable one, and it retracts the gate's mechanism claim.**
  A clean identification that kills our own mitigation claim is a better paper
  than an unidentified confound.
- Either way the arm is reported as exploratory, and the pre-registered P1/P2
  verdicts are NOT restated or revised on the basis of it.

**No pre-existing value may change.** The arm adds cells; it does not touch the
others. `boot_ci` constructs a fresh `random.Random(BOOT_SEED)` on every call, so
bootstrap results are independent of how many arms exist or the order they are
processed in. This is asserted mechanically after regeneration: every one of the
194 previously stamped cells must resolve to a byte-identical value.

#### A4 addendum — reporting rule for the per-seed length inversion (fixed 2026-09-07 07:3x UTC, with seed 3 STILL RUNNING)

Written before the third `neutralshort` seed completed and therefore before the
three-seed contrast existed. Two seeds were visible; the primary statistic was
not.

**What was observed.** The gated arm's realised memory is
`[393, 0, 382]` characters, so no scalar target can length-match it per seed.
`neutralshort` is matched to the gated arm *mean*, exactly as the pre-declared
`neutral` arm is matched to the ungated arm mean. The consequence is that the
match **inverts** per seed: on seeds 1 and 3 the gated arm carries *more* text
than its own length-matched control (393 vs 276; 382 vs ~280), while on seed 2
the gate accepted nothing and held an empty memory against padded control text.

**How this will be reported, decided now:**

1. The **primary is the pre-committed three-seed `gated - neutralshort`
   contrast**, reported with its sign-flip p whatever its direction. No two-seed
   statistic is substituted for it.
2. **No claim is made on the two non-empty seeds.** Selecting the seeds where
   the gate happened to retain a memory is a property observed *after* the run;
   reporting a contrast on that subset would be post-hoc subset selection. This
   project has refused that everywhere else (a nominal P1 pass inside the noise
   floor was declined; the temperature-0 data was discarded rather than
   reinterpreted), and it is not spent here. **No subset p-value, no subset mean
   presented as an estimate.**
3. The inversion **is** reported, as verifiable structure rather than as a
   result: the per-seed realised memory lengths of both arms go in the table, and
   the text states that on the seeds where the gate retained a memory it carried
   more text than its control, while on the remaining seed the comparison is
   empty-vs-padded and therefore pure dilution.
4. One sentence names the consequence for identification: the arm-mean match
   tests content value **under a length penalty** on the seeds that matter, which
   is conservative rather than favourable to the claim. This is an argument about
   **design, not evidence**, and is written that way.
5. **If the three-seed contrast is null or negative, A4 governs and the gate's
   mechanism claim is retracted, reported as plainly as a favourable result.**
   The inversion does NOT become a rescue argument for an unfavourable primary.

### Amendment A5 — extension to six seeds (EXPLORATORY, declared 2026-09-07 08:07 UTC, BEFORE the first new row)

**State at time of writing, recorded so this entry is auditable:** 12 completed
cells (4 arms x seeds 1-3), 262 ledger rows, `main.pdf` sha256
`f31b08f3218b2dccf4a89d90326fdc1e77d74fb2255f0c5a1a5da01922d687f2`, 17 gates
green. No seed-4/5/6 data of any kind exists yet.

**Status: NOT pre-registered.** A2 fixed `seeds = [1,2,3]`. This extension was
decided on 2026-09-07 *after* the three-seed results were known and read. The
manuscript will say so in those words: the sample was extended post hoc, and
n=6 is not a pre-registered scale.

**Why.** With three paired seeds an exact two-sided sign-flip permutation test
has 2^3 = 8 assignments, so its smallest attainable p is 2/8 = **0.25**. The
paper currently states in its own body that no contrast can reach significance
at this n. Six seeds give 2^6 = 64 assignments and a floor of 2/64 =
**0.03125**, which is the only route to an actual significance claim. Nothing
else about the design changes.

**Scope, fixed now.** Seeds 4, 5, 6 are run for **all four arms** --- ungated,
gated, neutral, neutralshort --- plus the round-0 baselines and the
round-0-vs-round-0 noise null for those seeds. The design is seed-paired and
must stay balanced; a partial extension of some arms only is forbidden.

**The neutral-arm targets are FROZEN and will NOT be recomputed.**
`neutral_target_chars = [308, 409, 403]` and
`neutralshort_target_chars = [227, 227, 258]` were measured from seeds 1-3 and
stay exactly as they are. Re-running `set_neutral_target.py` over six ungated
seeds would give the padding arms different targets on seeds 4-6 than on 1-3 and
destroy comparability within an arm. The targets are part of the frozen
configuration, not a quantity to be re-estimated.

**Reporting rule, fixed before any new row exists --- this is the point of the entry:**

1. **The six-seed result is the reported result, whatever it shows.** It replaces
   the three-seed estimates as the paper's primary numbers.
2. **This holds if the effects get worse.** If the CommonsenseQA gate contrast,
   or `gated - neutralshort`, weakens, loses CI separation, or reverses at n=6,
   that is the reported finding and the corresponding claim is narrowed or
   withdrawn exactly as the ARC contrast already was. **We may not fall back to
   the three-seed numbers because they looked better.** If effects shrink, the
   honest reading is that three seeds overstated them --- which is what more data
   is for.
3. **Both are shown.** Three-seed and six-seed values are reported side by side
   so a reader sees the trajectory rather than only the endpoint.
4. **One run, no optional stopping.** Seeds 4-6 are run once, as a block. Seeds
   are NOT added incrementally until something crosses a threshold; that would
   be optional stopping and would invalidate the very permutation test this
   extension exists to enable.
5. **Reproducibility check instead of value-invariance.** The three-seed
   estimates *will* legitimately change, because they now pool six seeds, so the
   byte-identical rule used for A4 does not apply. Instead: every previously
   reported three-seed value must be exactly reproducible from the six-seed
   ledger by restricting to seeds 1-3. Any value that is not reproducible that
   way indicates contamination rather than extension, and is reported as such.

**Hard stop.** If the run or the rebuild is not green by 2026-09-08 04:00 UTC,
the six-seed work is abandoned and the tagged three-seed submission
(`cl4fm-green-72`) ships unchanged.

### Amendment A6 — statistical reporting corrections (EXPLORATORY, declared 2026-09-07, after a cross-family statistical review)

Not pre-registered. Prompted by an external statistical review received while the
six-seed run of A5 was executing. Three additions, none of which changes any
measurement; all are recomputations of existing data.

1. **The percentile bootstrap CI is degenerate at n=3 and we now say so.** At
   small n the percentile interval is bounded below by `min(d)` and above by
   `max(d)`, so when every per-seed difference shares a sign the interval
   *cannot* contain zero whatever the effect size. Verified directly against our
   own ledger: `gated - ungated` on CommonsenseQA has per-seed differences
   [0.016667, 0.033333, 0.05] and a reported CI of exactly
   [0.016667, 0.05] = [min, max]; `gated - neutralshort` likewise. So "CI
   excludes zero" at n=3 carries no information beyond "the three seeds agree in
   sign", which is the p=0.25 sign test we already report. A
   `bootstrap_ci_degenerate` flag is now computed per contrast.
2. **Seed-level paired t interval added.** Reported alongside the bootstrap. It
   does not have the degeneracy above.
3. **SEM-based noise floor added alongside the pre-declared max band.** The
   pre-declared band is the maximum absolute per-seed shift; a maximum is an
   extreme-value order statistic that grows mechanically as seeds are added, so
   that band widens with n even when the noise does not --- which matters
   precisely because A5 is adding seeds. It also compares a multi-seed *mean*
   effect against a *single-seed* maximum. The pre-declared band is still
   reported as pre-declared; the SEM margin is reported next to it as the
   sounder comparison, and neither is dropped.
