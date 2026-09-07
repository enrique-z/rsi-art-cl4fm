# Domain-semantics audit

**Purpose.** Build-guard gates verify that every numeric literal in `main.tex`
matches a ledger row (gate 3), but nothing verifies that the surrounding prose
reasoning about the number is correct in the domain. That is what this file
records.

---

## ⚠ Scope: this file audits the **three-seed** grid and is superseded in part

**Read this before the rows below.** This audit was written against the
three-seed grid, before amendment **A5** extended the experiment to six seeds.
It is kept in the artifact unedited because it is part of the honest record of
how the paper was checked — but **the numbers and two of the verdicts in the
rows below are the three-seed ones and are superseded.** The paper reports the
six-seed result. Where this file and the paper disagree, the paper and the
ledger (`evidence/cl4fm_selfevolve_forgetting_ledger.jsonl`, 612 rows) are
correct.

What A5 changed, taken from the current stamp manifest and the paper's Results
section:

| | three seeds (audited below) | six seeds (reported in the paper) |
|---|---|---|
| `ungated::BWT_C` | -0.05 | **-0.033333** (CI touches zero) |
| `ungated::BWT_B` | -0.044444 | **-0.036111** (CI contains zero) |
| `contrast::gated_minus_ungated__BWT_C` | +0.033333 (CI excluded zero) | **+0.011111** (CI contains zero; sign-flip p = 0.5625) |
| `contrast::gated_minus_ungated__BWT_B` | +0.016667 | **-0.002778** (faintly negative) |
| `contrast::neutral_minus_ungated__BWT_B` | -0.044444 | **-0.033333** |
| `neutral::FG` | -0.05 | **-0.041667** |
| `neutral::BWT_B` | -0.088889 | **-0.069444** |
| `noise_null::C_max_abs` | 0.066667 | **0.116667** |
| `gated::mem_chars` / `ungated::mem_chars` | 258.333333 / 403.0 | **378.833333 / 518.166667** |
| `gated::accepted_edits` | 3.0 | **4.0** |
| `global::n_model_calls` / `n_items_scored` / `n_ambiguous` | 3098 / 2700 / 1 | **7277 / 6480 / 2** |
| **Verdict on P1** | "not established at this scale" | **REFUTED** — criterion met on neither family |
| **Verdict on P2** | "partially holds" (CommonsenseQA only) | **REFUTED** — that contrast is withdrawn too |

The pre-declared falsifier still fires at six seeds (the length-matched neutral
arm degrades more than the ungated arm on families A and B, and the short
padding arm reproduces it on C), so rows 5 and 8 below survive in direction if
not in magnitude. Amendment **A6** additionally flags that the percentile
bootstrap interval is degenerate at small *n*, so every "CI excludes zero"
judgement in the rows below must be read alongside the paired-*t* interval and
sign-flip *p* now stamped in the manifest. `EXPERIMENT_REPORT.md` §4–§6 carries
the six-seed tables and verdicts in full.

---

## Rows (three-seed audit, as written)

One row per abstract claim. Verdicts: PASS / FLAG / BLOCK.

| # | Claim (verbatim or close) | Domain concept | Auditor verdict | Evidence / justification | Location in main.tex |
|---|---|---|---|---|---|
| 1 | "Ungated evolution gave forward gain 0.033 (95% CI [-0.017, +0.067])" | forward gain, GSM8K accuracy, seed-level percentile bootstrap | PASS | Ledger `ungated__FG` = +0.033 with CI [-0.017, +0.067] (B=10 000, seed 20260907); CI includes zero, and the paper reports this honestly as "no measurable forward gain". | Abstract; §Results ¶P1 |
| 2 | "backward transfer -0.044 [-0.117, +0.017] and -0.05 [-0.083, -0.017] on the held-out families" | Lopez-Paz-and-Ranzato-style BWT applied at the memory layer | PASS | Ledger `ungated__BWT_B` = -0.044 [-0.117, +0.017] (CI contains zero) and `ungated__BWT_C` = -0.050 [-0.083, -0.017] (CI nominally excludes zero). Both are reported literally; the P1 sentence is corrected to say the CommonsenseQA CI does not clear the noise band. | Abstract; §Results ¶P1 |
| 3 | "paired gated minus ungated was +0.017 and +0.033" | paired-by-seed difference, bootstrap over difference vector | PASS | Contrast rows `gated_minus_ungated__BWT_B` = +0.017 [0.000, +0.050] and `gated_minus_ungated__BWT_C` = +0.033 [+0.017, +0.050]. The CommonsenseQA CI strictly excludes zero; the ARC CI touches zero. Text reports both faithfully. | Abstract; §Results ¶P2 |
| 4 | "round-0-vs-round-0 re-evaluation puts the noise band at \|Δ\| ≤ 0.067 and 0.067" | measurement-noise null under identical items and empty memory | PASS | `noise_null__B_max_abs` = 0.0667; `noise_null__C_max_abs` = 0.0667. Max-absolute-per-seed shift is the pre-declared conservative band; the paper uses it (not the mean) as the threshold. | Abstract; §Results, Table 1 last block |
| 5 | "length-matched neutral-memory arm separates content interference from context dilution (-0.044)" | rival-mechanism control, character-count target from ungated's own memory | PASS | `contrast::neutral_minus_ungated__BWT_B` = -0.044 [-0.067, -0.017] (CI excludes zero); `..._FG` = -0.083 [-0.100, -0.067] (CI excludes zero). Neutral degrades more than ungated on A and B; the falsifier fires in strong form, and the paper's mechanism sentence is flipped accordingly. | Abstract; §Results ¶Rival mechanisms |
| 6 | Verdict on P1 ("not established at this scale") | pre-registered refutation criterion | PASS | The ungated held-out CIs sit at or within the noise band max-abs 0.0667. Under the pre-declared rule ("CI excludes zero AND clears noise band"), P1 does not hold. Reported plainly. | Abstract; §Results ¶P1 |
| 7 | Verdict on P2 ("partially holds") | pre-registered gated-vs-ungated criterion | PASS | Gated-minus-ungated BWT_C CI excludes zero; BWT_B CI includes zero. The paper says "partially holds", names the family where it does, and reports the ARC null. | Abstract; §Results ¶P2 |
| 8 | Mechanism sentence ("context dilution, not content interference; evolved content partially offsets dilution") | interpretation of the neutral-arm control | FLAG | The claim is *strong* — neutral vs ungated FG contrast excludes zero and the direction is unambiguous — but three seeds is still three seeds, and the sentence would be more defensible with a hedge to "at this budget". Kept as written because the CI genuinely excludes zero; a reviewer objection would be about seed count, which §Limitations already concedes. | Abstract; §Results ¶Rival mechanisms |
| 9 | Deviation A1 (family C = CommonsenseQA, not BBH) | pre-declared design deviation, recorded before the first full run | PASS | `evidence/DESIGN_NOTES.md` §1 records BBH's HTTP 404 with checksummed alternatives; MATH-500 was rejected as same-family as A. CommonsenseQA is disjoint-domain, exogenous-labelled, and disclosed. | §Setup; Appendix A |
| 10 | Temperature amendment A3 (0.0 → 0.7) | measurement integrity — seeds must actually control sampling | PASS | Recorded amendment A3 in `evidence/DESIGN_NOTES.md`; caught mid-run when seeds 1 and 2 gave identical 0.7500 accuracy on 60 GSM8K items. Fixed; run restarted from scratch; all temperature-0 data deleted. Verified with 24-item probe: 6/24 items disagree between seeds at 0.7 (25 %) vs 1/120 at 0.0. | Appendix A "Deviations 2 and 3" ¶; DESIGN_NOTES §A3 |
| 11 | "Gate accepted 3.0 vs ungated 8.67 edits per seed" — economics claim | accepted-edit accounting | PASS | `gated__accepted_edits` = 3.0; `ungated__accepted_edits` = 8.667. Fig 1c backs the same counts. Consistent with the dilution reading: the gate benefits partly by keeping memory smaller. | §Results ¶P2 |
| 12 | Protocol-failure counts (unparseable reflections, rounds below budget, ambiguous parses) | 3B model compliance with schema-forced JSON edits and answer-format instruction | PASS | Ledger rows `protocol_*__unparseable_reflections`, `protocol_*__rounds_below_budget`, `global::n_ambiguous`. **Corrected 2026-09-07:** the manifest reads `global::n_model_calls` = 3098, `global::n_items_scored` = 2700, `global::n_ambiguous` = 1, `global::n_failed_calls` = 0. An earlier draft of this row said "zero ambiguous parses across 1080 graded items", which matched neither the manifest nor `main.tex`; the paper prints the manifest values and is correct. Zero unparseable reflections; ungated/gated rounds all filled the edit budget. Neutral arm has no reflection step. | Appendix A "Protocol-failure accounting" |
| 13 | Model-scale limitation ("result stands at 3B; scale-robustness untested") | pre-committed 8B replication, non-execution clause | PASS | Amendment A2 in `DESIGN_NOTES.md` pre-committed 8B (qwen3:8b) replication and its non-execution clause before any FG/BWT value existed. The replication did not fit the remaining time budget (a full run at 3B took ~4.4 h with retries; 8B was projected at ~10 h) and was not run. §Limitations states this plainly. | §Limitations |

| 14 | Method statement: "temperature fixed at 0.7 for every call" | measurement integrity — the stated decode config must be the config that ran | PASS (was BLOCK) | **Found and fixed, 2026-09-07.** `main.tex` §Setup previously read "at temperature 0, with seeds carrying the sampling variation" — false against `evidence/calls.jsonl` (3098/3098 calls at temperature 0.7) and self-contradictory, since at temperature 0 the seed cannot carry sampling variation. That is exactly the defect amendment A3 caught and fixed mid-run. Left uncorrected it would have invited a clean reject ("your three seeds are the same draw, so your CIs are meaningless"). §Setup now states 0.7, and the amendment (discovery, restart, discarded data) is disclosed in Appendix A. | §Setup ¶Families, model, metrics; Appendix A ¶Amendment A3 |
| 15 | "P1 not established" vs the registered P1 criterion | pre-registration bookkeeping | PASS (was FLAG) | The registered rule is "BWT < 0 with paired CI excluding zero on at least one held-out family" and CommonsenseQA meets it. The paper previously declared P1 "not established" while only calling the CI "nominal" — readable as a post-hoc goalpost move. §Results now states that the registered criterion **is met** on CommonsenseQA and that we decline the claim because pre-declared rival mechanism 2 (evaluation noise) is not excluded, i.e. the conservative reading. Verdict unchanged; the bookkeeping is now visible. | §Results ¶P1; Appendix A ¶Pre-declared refutation branches |
| 16 | Design rules R1–R3 (added 2026-09-07) | constructive restatement of already-audited cells | PASS | R1 cites `neutral::FG` = -0.05 and `neutral::BWT_B` = -0.088889; R2 cites `contrast::gated_minus_ungated__BWT_C` = 0.033333, `gated::mem_chars` = 258.333333, `ungated::mem_chars` = 403.0; R3 cites `noise_null::C_max_abs` = 0.066667 and `ungated::BWT_C` = -0.05. Every value is an existing stamped cell already audited in rows 1–7; the rules restate them as guidance and introduce no new claim. | §Design rules for inference-time self-evolution |

| 17 | Design rule R3: "the noise floor is larger than every held-out effect" | internal arithmetic | PASS (was BLOCK) | **Found in a second verification pass and fixed.** `noise_null::C_max_abs` = 0.066667, but `neutral::BWT_B` = -0.088889 has magnitude 0.0889 > 0.0667, so the original sentence was false against the paper's own Table 1. R3 now reads "larger than every held-out effect the *evolved* arms produced (the neutral arm's -0.088889 is the one that clears it)" — narrower, true, and it names the one held-out effect that does beat the floor, which is the dilution result. | §Design rules R3 |
| 18 | Abstract ordering and the gate/length confound | claim scoping | PASS | The abstract now leads with the falsifier/dilution result (identified) and presents the gate contrast second, stated inline against the memory length it saves (`gated::mem_chars` = 258.333333 vs `ungated::mem_chars` = 403.0) with the explicit words "we price that advantage against the length it saves instead of claiming it independently". Verification identified the gate/length confound as the paper's top rejection risk; the paper now concedes it before a reviewer can catch it, and does not rest its lead result on it. No number changed. | Abstract; §Results ¶P2; §Design rules R2; §1 ¶What we claim |
| 19 | Family A train/test disjointness | evaluation hygiene | PASS | `analysis/harness.py` draws evolution and gate-probe items from GSM8K `train` and evaluation items from GSM8K `test`, with `assert not (A_test uids & A_train uids)`. This was enforced in code but not stated; §Setup now says "evolved on *train* items and scored on *test* items asserted disjoint in code". | §Setup ¶Families, model, metrics |

| 20 | Exploratory arm A4 (`neutralshort`) and the `gated - neutralshort` contrast | identification of the gate effect independently of memory length | PASS | Declared in `DESIGN_NOTES.md` **before the run**, explicitly as NOT pre-registered, with the reporting rule for both outcomes fixed in advance. Result: `contrast::gated_minus_neutralshort__FG` = +0.072222 [+0.033333,+0.133333], `__BWT_B` = +0.033333 [+0.016667,+0.05], `__BWT_C` = +0.072222 [+0.016667,+0.116667] — all CIs exclude zero, all seeds same sign. At matched length the gated memory's content is worth something, so the gate is not merely a device for keeping the prompt short. Caveat carried in the text: the match is at the arm mean, and the gated arm's per-seed lengths (393/0/382) admit no per-seed scalar target. | §Results ¶P2; Table 1; Appendix A ¶A4 |
| 21 | Withdrawal of the ARC gate contrast | post-hoc honesty about a one-seed effect | PASS (was an overclaim) | `perseed::gated_minus_ungated__BWT_B_s1/s2/s3` = 0.0 / 0.05 / 0.0 and `loo::..._drop2` = 0.0 exactly; `perm::gated_minus_ungated__BWT_B_p` = **1.0**, the maximum. The single seed that moves it is the seed where the gate accepted zero edits and held `gated::mem_chars_s2` = 0 — an empty prompt. The paper now names it a length artefact and withdraws it rather than reporting "CI touches zero", which would have implied a real-but-underpowered effect. | §Results ¶P2; Appendix A ¶Per-seed influence |
| 22 | Permutation-test floor disclosure | honest ceiling on what n=3 can establish | PASS | With 3 paired seeds an exact two-sided sign-flip test has 2^3 = 8 assignments, so its minimum attainable p is 0.25. Every contrast the paper claims sits exactly at that floor (`perm::gated_minus_ungated__BWT_C_p` = 0.25, `perm::gated_minus_neutralshort__BWT_C_p` = 0.25, `perm::neutral_minus_ungated__BWT_B_p` = 0.25) and every contrast it declines sits at 1.0. Stated in the body: "Nothing here is significant on a permutation test and we do not claim otherwise." | §Results ¶P2; Abstract |
| 23 | Design rule R1 revised after the new arm contradicted it | interpretive integrity | PASS (was an unsupported inference) | R1 previously read "what a memory costs by occupying the prompt dominates what its content contributes". The new arm refutes that: at matched length the gated arm beats content-free padding by +0.072 on FG and BWT_C, so content is *not* the smaller term. Worse, shortening padding from `neutral::mem_chars` 416.67 to `neutralshort::mem_chars` 278.67 helped on ARC (-0.088889 to -0.061111) but **hurt** on CommonsenseQA (-0.055556 to -0.088889), so the length-harm relation is not even monotone. R1 now says the lesson is not "shorter is safer" — which we cannot show — but that occupying context is a real cost only useful content repays. | §Design rules R1 |

Verdicts summary: 22 PASS, 1 FLAG (row 8, now largely absorbed: the abstract's
mechanism sentence carries the "at this budget" hedge the auditor advised, and
§Results says content interference is refuted *as the sole mechanism*). 0 BLOCK.
Seven defects were found and repaired on 2026-09-07 (rows 14 and 15); row 12's
own bookkeeping was wrong and is corrected. No claim in the abstract or results
is unsupported by a ledger row with a passing verdict.

## Rival mechanisms / discriminator falsifier

Pre-declared in `A2_PREDECLARATION_2026-09-07.md`. Disposition:

- **Rival 1: Scaffold-length / context-dilution artefact** → measured by the
  `neutral` arm, length-matched to the ungated arm's realised memory. Falsifier
  fires in strong form (neutral degrades *more* than ungated on FG and BWT_B,
  CIs exclude zero). Paper reports context dilution as the mechanism and
  evolved content as partially offsetting it. §Results ¶Rival mechanisms.
- **Rival 2: Evaluation noise** → measured by the round-0-vs-round-0 null with
  a different sampling seed. Max-absolute per-seed shift = 0.0667 on every
  family; the ungated arm's held-out effects are of the same magnitude, so the
  paper reports P1 as "not established". §Results Table 1 last block.
- **Rival 3: Gate = fewer edits** → answered by the accepted-edit counts
  (3.0 gated vs 8.67 ungated) and the `gated_minus_neutral` contrast, which
  isolates the gate from memory length alone. The gate-vs-neutral row is what
  attributes the gated arm's advantage rather than the gate-vs-ungated row
  alone. §Results ¶P2 and Fig 1c.

## Auditor note

This audit was produced after the run completed, against the sealed pre-declaration
and the ledger. Every value in this file is a ledger cell; no domain claim was
verified against external domain literature (the domain here is inference-time LLM
self-evolution and CL metrics, not wet lab).
