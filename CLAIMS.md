# Claim–Evidence–Risk Registry — cl4fm-selfevolve-forgetting

Venue: CL4FMAgents @ NeurIPS 2026, short track (4 pages body).
Manuscript: `main.tex`. Evidence: `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl`
and `evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json`, both emitted by
`analysis/aggregate.py`.

> **⚠ Scope: this registry was written against the three-seed grid.** Amendment
> **A5** later extended the experiment to six seeds and both pre-registered
> claims were refuted; amendment **A6** added a paired-*t* interval and a
> sign-flip *p* beside every bootstrap CI. The registry is kept unedited as part
> of the record of how the paper was checked, but the values and the
> CI-excludes-zero judgements below are the **three-seed** ones and are
> superseded. The authoritative six-seed numbers are the manifest
> (`evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json`, 612 rows), the
> paper's Results section, and `EXPERIMENT_REPORT.md` §4–§6.
> `DOMAIN_AUDIT.md` carries a three-seed/six-seed comparison table.

**State of this file (2026-09-07, three-seed grid).** The grid has
run, the ledger has landed, and every `\ResultCell` in `main.tex` has been
resolved mechanically to a `\StampedCell`:

```
\ResultCell{g::m}  ->  \StampedCell{g}{m}{<manifest["ledger_rows"]["g::m"]["value"]>}
```

Guard gate 3 passes on every stamped cell; gate 9 reports 0 `[TBD]` in the PDF.
The paper was subsequently revised (2026-09-07) to lead with the
implemented loop and its retention gate, and three design rules (R1–R3,
`\ref{sec:rules}`) were added — **each rule cites an already-stamped cell; no
number, verdict or CI changed in the reframe.** The abstract was rewritten in
the same pass: it now carries the gated-minus-ungated contrast and its FG cost
explicitly, and drops the redundant `noise_null::B_max_abs` and
`gated_minus_ungated__BWT_B` restatements (both still in Table 1).
No value in this file or in `main.tex` may be typed by hand.

---

## Registry

| # | Claim text (verbatim or close) | Type | Evidence (ledger rows) | Statistical treatment | Reviewer-objection risk | Limitation sentence location |
|---|-------------------------------|------|------------------------|-----------------------|------------------------|------------------------------|
| 1 | "Ungated evolution gave … backward transfer `ungated::BWT_B` … and `ungated::BWT_C` … on the held-out families" (P1) | direction set by the ledger (`negative` if a held-out CI sits below zero; honest `diagnostic`/null otherwise) | ledger rows `ungated__BWT_B`, `ungated__BWT_C` (+ `_ci_low` / `_ci_high`) | Seed-level percentile bootstrap, B = 10 000, RNG seed 20260907; unit of independence = seed (n = 3); item sets fixed and identical across arms, so arms are paired by seed and by item | (1) "3 seeds is too few" — pre-registered n; CIs are shown wide and never narrowed by pooling items; (2) "this is context dilution, not forgetting" — answered by the `neutral` arm; (3) "this is sampling noise" — answered by the round-0-vs-round-0 null | §Limitations ¶1 (3B scale, 60 items, 3 seeds, endpoint-only evaluation) |
| 2 | "paired gated minus ungated was `contrast::gated_minus_ungated__BWT_B` and `contrast::gated_minus_ungated__BWT_C`" (P2) | direction set by the ledger | ledger rows `gated_minus_ungated__BWT_B`, `gated_minus_ungated__BWT_C`, `gated_minus_ungated__FG` | Per-seed difference vector, then percentile bootstrap (B = 10 000). "CI excludes zero" is the pre-registered decision rule | (1) "the gate just accepts fewer edits" — answered by `*::proposed_edits` / `*::accepted_edits` and Fig. 1c; (2) "the plasticity cost is hidden" — it is the FG entry of the same contrast row | §Limitations ¶1, final clause ("a null on P2 would bound this one cheap gate") |
| 3 | "a round-0 versus round-0 re-evaluation puts the evaluation-noise band at \|Δ\| ≤ `noise_null::B_max_abs` and `noise_null::C_max_abs`" | diagnostic | ledger rows `noise_null__A/B/C` and `noise_null__A/B/C_max_abs` | Same fixed items, same empty memory, sampling seed s+100; per-seed difference, mean + bootstrap CI + largest absolute per-seed shift (the conservative band) | "the null is only 3 draws" — stated; the max-absolute shift, not the mean, is used as the band | §Limitations ¶1 (seed count) |
| 4 | "a length-matched neutral-memory arm separates content interference from context dilution (`contrast::neutral_minus_ungated__BWT_B`)" | diagnostic / pre-declared falsifier | ledger rows `neutral__BWT_B`, `neutral__BWT_C`, `neutral_minus_ungated__BWT_B`, `neutral_minus_ungated__BWT_C`; plus `neutral::mem_chars` vs `ungated::mem_chars` | Paired-by-seed contrast, bootstrap as above. Falsifier rule: if the neutral arm reproduces the ungated arm's BWT within CI, the content-interference mechanism is falsified and the paper reports context dilution | "length matching is approximate" — the target is measured from the completed ungated cells and both character counts are reported | §Results ¶"Rival mechanisms"; §Limitations ¶1 |
| 5 | "forward gain `ungated::FG`" on the evolved family | diagnostic | ledger row `ungated__FG` (+ CI rows) | As row 1 | "FG may itself be inside the noise band" — the noise null covers family A too (`noise_null::A`) | §Limitations ¶1 |
| 6 | Protocol-failure accounting (`global::n_ambiguous`, `protocol::*`, call counts) | diagnostic | ledger rows `ambiguous_parse_count`, `items_scored_total`, `model_calls_total`, `model_calls_failed`, `protocol_*__unparseable_reflections`, `protocol_*__rounds_below_budget` | Counts; no inference | "a 3B model may not follow the protocol at all" — that is precisely what these counts measure; they are reported, never dropped | §Limitations ¶1, sentence 2 |

*No row may be marked complete before its ledger row exists with
`verdict=SUPPORTED` (or is honestly reported as the negative branch with the
paper's interpretive sentences flipped).*

---

## Abstract claims

**Required — gate 14 parses this section.** Every claim in the abstract mapped to
the stamp-manifest key that carries it.

| # | Claim text (verbatim from abstract) | claim_id | Evidence locator |
|---|-------------------------------------|----------|-------------------|
| 1 | "The gate raises held-out backward transfer by +0.033333 [0.016667, 0.05] on CommonsenseQA" | `contrast::gated_minus_ungated__BWT_C` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 2 | (lower CI bound of claim 1) | `contrast::gated_minus_ungated__BWT_C_ci_low` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 3 | (upper CI bound of claim 1) | `contrast::gated_minus_ungated__BWT_C_ci_high` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 4 | "at a plasticity cost we cannot distinguish from zero (-0.016667 [-0.033333, 0.0])" | `contrast::gated_minus_ungated__FG` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 5 | (lower CI bound of claim 4) | `contrast::gated_minus_ungated__FG_ci_low` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 6 | (upper CI bound of claim 4) | `contrast::gated_minus_ungated__FG_ci_high` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 7 | "Ungated evolution gave forward gain 0.033333 (95% seed-bootstrap CI [-0.016667, 0.066667])" | `ungated::FG` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 8 | (lower CI bound of claim 7) | `ungated::FG_ci_low` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 9 | (upper CI bound of claim 7) | `ungated::FG_ci_high` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 10 | "and backward transfer -0.044444 on ARC" | `ungated::BWT_B` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 11 | "and -0.05 on CommonsenseQA" | `ungated::BWT_C` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 12 | "both sit inside the measured noise floor (\|Δ\| ≤ 0.066667)" | `noise_null::C_max_abs` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |
| 13 | "the length-matched neutral memory degrades more than the evolved memory (-0.044444 on ARC)" | `contrast::neutral_minus_ungated__BWT_B` | `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` |

*Rules honoured:* every `claim_id` is a manifest key of the form `group::metric`
and resolves in `evidence/*_stamp_manifest.json` once `analysis/aggregate.py` has
run. The abstract contains no numeric sentence without a computable evidence
row; its only non-numeric sentences describe the design and point at the
verdict, and assert nothing measurable.

---

## Verdict-dependent sentences (flip after the ledger lands)

Each is marked in `main.tex` with a `% VERDICT-DEPENDENT SENTENCE` comment
immediately above it. All four are written to be true under either outcome;
replace each with the actual verdict once the numbers exist.

1. **Abstract, final sentence** — "Read against refutation criteria fixed before
   data collection, these numbers decide both pre-registered claims (Section 3),
   at the scale stated in Section 5." Replace with the verdict for P1 and P2,
   e.g. "Ungated evolution therefore shows negative backward transfer on
   ARC-Challenge …" or "No held-out family shows negative backward transfer with
   a CI excluding zero, so inference-time self-evolution is stability-safe at
   this scale …".
2. **§Results, P1 paragraph** — "P1 holds only if some held-out family has mean
   BWT < 0 with its paired 95% CI excluding zero and clearing the noise band in
   Table 1."
3. **§Results, P2 paragraph** — "P2 holds only if the gated-minus-ungated
   contrast is positive with a CI excluding zero on a held-out family."
4. **§Results, Rival mechanisms** — "This is the pre-declared falsifier: a
   length-matched control that reproduces the ungated arm's backward transfer
   within CI falsifies content interference, leaves context dilution, and is
   then what we report." If the falsifier fires, the mechanism sentence in the
   introduction ("a rule distilled from one family is applied, unbidden, to the
   rest") must be restated as a context-length claim.

Nothing else in the manuscript presupposes a direction: the title is a question,
and no other sentence asserts an outcome.

---

## Per-citation aptness (load-bearing citations only)

- `lopezpaz2017gem` — supports "using the FG/BWT metrics of Lopez-Paz and
  Ranzato" because that paper defines backward transfer as the change in
  accuracy on an earlier task after learning later ones, i.e. exactly the
  endpoint quantity `acc_X(R) − acc_X(0)` we compute per held-out family.
- `chaudhry2019tiny` — supports "make an 8-item anchor a design rather than a
  gesture" because its central result is that extremely small episodic memories
  already recover much of the replay benefit, which is what makes a very small
  rehearsal anchor a defensible design point.
- `wang2023voyager` — supports "Voyager gates each new skill on an execution
  check inside the evolved domain, so cross-domain interference cannot appear"
  because Voyager admits a skill to its library only after in-environment
  self-verification in Minecraft and reports no evaluation on any task family
  outside that environment.
- `ding2026memory` — supports "a diagnostic taxonomy with no gating remedy"
  because Controlled Memory Interference contributes a framework for
  characterising and generating memory-interference cases in continual LLM
  agents, and evaluates no accept/reject gate and no held-out-family backward
  transfer.
- `lin2026selfregress` — supports "a within-task collapse under weight updates"
  because its rise-and-collapse phenomenon is measured as pass@1 on the training
  task itself under REINFORCE-style self-training, i.e. weight updates on a
  single task, not cross-family transfer.
- `cobbe2021gsm8k` — supports using GSM8K as family A with exogenous labels
  because the released split ships gold answers in the `#### <n>` format our
  extractor compares against.
- `clark2018arc` — supports using ARC-Challenge as held-out family B because the
  released Challenge test split ships an `answerKey` per item, the exogenous
  label our multiple-choice extractor compares against.
- `suzgun2022bbh` — identifies the benchmark named in the pre-declaration; the
  unavailability claim itself rests on the recorded HTTP 404 responses in
  `evidence/DESIGN_NOTES.md`, not on the citation.
- `hendrycks2021math` — supports "MATH-500 is the same task family as A" because
  the MATH dataset is competition mathematics, i.e. the same arithmetic/algebraic
  reasoning family as grade-school word problems, which is why substituting it
  would confound backward transfer with near-transfer.
- `zheng2023mtbench` — supports "judges are biased: position and verbosity
  effects" because that paper reports both biases for a strong LLM judge
  alongside its high human-agreement result.
- `wang2023llmfair` — supports "order sensitivity that reverses rankings"
  because it shows that permuting candidate order changes which response an LLM
  evaluator prefers.
- `diazrodriguez2018dont` — supports "reported per family rather than as an
  average that hides the stability–plasticity trade" because its argument is
  that accuracy-only continual-learning summaries conceal forgetting and
  transfer behaviour.
- `mirzadeh2024gsmsymbolic` — supports "GSM8K accuracy is brittle to superficial
  perturbation" because GSM-Symbolic shows accuracy degrading when only surface
  details of GSM8K items are varied.
- `wahi2026proctor` — supports "recent work argues self-improving agents need
  deterministic guardrails" because that is the paper's stated thesis: an
  LLM-as-a-judge is not an oracle and self-improvement loops require
  deterministic checks.

---

## Checklist

- [ ] `analysis/aggregate.py` has run; ledger and stamp manifest both exist
- [ ] Every `\ResultCell{g::m}` in `main.tex` replaced by `\StampedCell{g}{m}{v}`
- [ ] The four verdict-dependent sentences rewritten to the actual verdict
- [ ] Abstract regenerated from the stamped PDF
- [ ] Build gates green: anti-fabrication guard, bibliography (≥30 refs),
      body page cap with zero spill, metadata consistency, domain audit
- [ ] No bare prose percentage or ratio in the PDF lacks a row here
- [ ] CI includes-zero status noted for every CI in the registry
