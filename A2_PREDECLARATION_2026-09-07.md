# A2 Pre-declaration — cl4fm-selfevolve-forgetting

**Date:** 2026-09-07 (UTC) · **Venue:** CL4FMAgents — Continual Learning in the Era of Foundation
Models and Embodied Agents, NeurIPS 2026 (`NeurIPS.cc/2026/Workshop/CL4FMAgents`, deadline
2026-09-08 11:59 UTC) · **Track:** Short paper (4 pages body) · **Blind:** double.
**CFP topics hit:** agent self-evolution / recursive self-improvement; memory architectures;
catastrophic forgetting & forward/backward transfer; safety and reliability during self-improvement.


## Pre-registered claims

**Primary (P1, negative-transfer):** An LLM agent that recursively self-evolves its persistent
memory/skill library (learned insights, worked exemplars, procedural rules — no weight updates)
on task family A for R rounds, with edits accepted by its own self-judgement only ("ungated"),
shows **negative backward transfer** on held-out task families B and C: mean BWT < 0 with the
paired-seed 95% CI excluding zero, on at least one held-out family.

**Secondary (P2, gating):** A **verifier + retention gate** — edits are kept only if (i) an
exogenous checker confirms improvement on family A and (ii) accuracy on a small fixed rehearsal
anchor set drawn from B/C does not drop — yields BWT that is higher (less negative) than the
ungated arm, paired 95% CI excluding zero.

## Design (fixed before any run)

- Model: one small open model served locally via Ollama (primary `qwen3:8b`, non-thinking mode;
  fallback `llama3.2:3b` if throughput demands — the pilot decides and the choice is recorded
  before the full run). Temperature fixed; seeds control sampling.
- Family A (evolved): GSM8K (public, exogenous labels; train split for evolution prompts, test
  split for evaluation). Held-out families with exogenous labels: B = ARC-Challenge (science MCQ),
  C = a second reasoning family disjoint from A (e.g., BBH subset or MATH-500 subset); exact
  choice and item counts recorded in `evidence/DESIGN_NOTES.md` before the first full run.
- Self-evolution loop (identical in both arms except the gate): each round, the agent attempts
  n_A training items with its current memory, reflects on failures/successes, and proposes edits
  to its memory (add/modify/delete entries); the proposal budget per round is identical across
  arms. Ungated arm accepts edits its own self-judge scores as improvements; gated arm applies
  the verifier + retention gate.
- Rounds R = 3 (minimum) up to 5; seeds ≥ 3 per arm. Evaluation at round 0 and after every round
  on A-test, B, C. Item counts per family ≥ 60, fixed and identical across arms and rounds.
- Metrics (Lopez-Paz & Ranzato style, adapted): forward gain FG = acc_A(R) − acc_A(0);
  backward transfer BWT_X = acc_X(R) − acc_X(0) for X ∈ {B, C}. Unit of independence = seed
  (paired across arms by seed and by item set). 95% CIs by seed-level bootstrap (≥10,000) plus
  per-item McNemar as a robustness check.
- Every number enters the paper only via `evidence/` ledger rows → stamped cells.

## Refutation criteria / honest-negative fallback

- P1 refuted if no held-out family shows BWT < 0 with CI excluding zero → paper reports
  "inference-time self-evolution is stability-safe at this scale" (positive stability finding).
- P2 refuted if gated − ungated BWT CI includes zero → paper reports the gate's ceiling.
- Both outcomes are submitted in the same 4-page format.

## Rival mechanisms (to be addressed; gate 13b)

1. **Scaffold-length / prompt-drift artefact** — longer evolved memories degrade held-out
   performance by context dilution, not by content interference. Test: a *length-matched
   neutral-memory* control arm (same token count of irrelevant but well-formed entries).
2. **Evaluation noise** — BWT within sampling noise. Test: round-0 vs round-0 re-evaluation with a
   different seed gives the null distribution.
3. **Gate = fewer edits** — the gated arm merely edits less. Test: report BWT at matched
   accepted-edit counts and the acceptance rates per arm.

**Discriminator/falsifier:** if the length-matched neutral-memory control reproduces the ungated
arm's BWT within CI, the "content interference" mechanism is falsified (it is context dilution),
and the paper says so.

## Feasibility bound and fallback timeline

- 60-second foreground pilot (1 round × 5 items × 1 arm) must succeed on real Ollama calls.
- Throughput pilot fixes model + counts so the full run completes in ≤ 12 h wallclock.
- If no runnable pilot exists by 2026-09-07 04:00 UTC, fall back to pool row H01 (4-page
  meta-audit) for the deadline, and this study continues for a later venue.
