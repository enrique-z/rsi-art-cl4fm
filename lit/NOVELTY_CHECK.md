# Novelty Check — cl4fm-selfevolve-forgetting

**Claim under examination:** Ungated recursive self-evolution of an LLM agent's persistent
memory/skill library on one task family produces negative backward transfer (forgetting) on
held-out task families; a verifier + retention (rehearsal-anchor) gate reduces this loss.

Scope of sweep: forward/backward transfer in memory-based self-evolving agents; context-level
interference in skill libraries; rehearsal gates for self-improvement loops.
All five papers below were searched and read in detail.

---

## 5 Closest Prior Works to Our Specific Claim

### 1. lin2026selfregress — "Self-Improvement Can Self-Regress" (Lin 2026, arXiv:2606.21090)

**Proximity:** HIGH. Documents that self-improvement loops collapse on the *training* metric.

**Key difference:** Lin studies within-task collapse under weight-update REINFORCE (fine-tuning),
not cross-task backward transfer. The collapse mechanism is policy over-optimization on a fixed
reward distribution; KL/EWC constraints do not prevent it. Our claim is orthogonal: we study
*cross-family* forgetting at the inference-time memory/skill-library level, with no weight updates.
Neither paper overlaps the other's failure mode or proposed fix.

**Novelty threat:** LOW. Lin's paper does not demonstrate or address cross-task BWT in
inference-time self-evolution, which is our primary contribution.

---

### 2. ding2026memory — "Controlled Memory Interference in Continual LLM Agents" (Ding et al. 2026, arXiv:2608.07622)

**Proximity:** HIGH. Studies how memory evolution in LLM agents produces interference.

**Key difference:** Ding et al. build a *diagnostic framework* (CMI) for characterising
memory interference patterns and generating synthetic interference datasets. They do not
measure backward transfer across held-out task families, do not run sustained self-evolution
loops on a single task domain, and do not evaluate a rehearsal-anchor gate as a remedy.
The paper is descriptive/analytical rather than proposing a gating mechanism.

**Novelty threat:** MEDIUM. CMI covers the interference phenomenon but not the self-evolution
loop setup, BWT quantification across distinct task families, or the gated-vs-ungated comparison
that is our paper's contribution.

---

### 3. li2026jitrl — "Just-In-Time Reinforcement Learning" (Li et al. 2026, arXiv:2601.18510)

**Proximity:** MEDIUM. Enables inference-time continual learning in LLM agents via a dynamic
episodic memory without gradient updates.

**Key difference:** JitRL focuses on *improving* performance on a target task stream; it does not
measure backward transfer on intentionally held-out families and does not study what happens when
the memory is saturated with a single-task distribution. The rehearsal mechanism in JitRL (non-parametric
experience retrieval) is designed for positive transfer, not for protecting against negative backward
transfer from within-family specialisation.

**Novelty threat:** LOW. JitRL does not make, test, or address our claim.

---

### 4. wang2023voyager — "Voyager" (Wang et al. 2023, arXiv:2305.16291)

**Proximity:** MEDIUM. Closest prior system with a *gated* skill library: Voyager's
execution-check gate prevents broken skills from entering the library.

**Key difference:** Voyager's gate checks functional correctness within Minecraft (the evolved
domain); it is not designed to detect or prevent forgetting on other task families. Voyager never
measures backward transfer to held-out domains; the game setting provides no natural multi-family
evaluation. Our work shows that a *domain-local* gate (analogous to Voyager's) is insufficient
and that a *retention gate* referencing held-out rehearsal anchors is needed.

**Novelty threat:** LOW. Voyager's contribution is the skill-library architecture, not backward-transfer
analysis or cross-family retention gating.

---

### 5. wu2024selfimpreversal — "Progress or Regress?" (Wu et al. 2024, arXiv:2407.05013)

**Proximity:** MEDIUM. Documents that LLM self-improvement can decrease out-of-distribution
generalisation and diversity while increasing benchmark scores.

**Key difference:** Wu et al. study OOD generalisation under *single-pass* self-improvement
(post-training on curated data); they do not study persistent memory/skill libraries, recursive
multi-cycle evolution on a fixed family, or backward transfer measured with the GEM BWT metric.
Their finding (OOD generalisation declines) is consistent with our claim but measured in a
fundamentally different regime (weight updates, not inference-time memory evolution).

**Novelty threat:** LOW-MEDIUM. Wu et al. provide supporting evidence that self-improvement
degrades generalisation, but their setup, measurement, and proposed remedies are different.

---

## Honest Assessment of Novelty

**Does any prior work already make our specific claim?**
No. The specific combination of (a) inference-time self-evolution, (b) persistent skill/memory
library updated on one task family, (c) backward transfer measured on held-out families using
BWT metrics, and (d) a rehearsal-anchor gate as the remedy is not made by any of the five
closest works or by any other paper found in this sweep.

**Sub-claim risk:** The partial result that "LLM self-improvement can hurt OOD performance"
is present in wu2024selfimpreversal and lin2026selfregress, but neither paper addresses the
inference-time memory-evolution regime or the gated-vs-ungated comparison.

**Contingent risk:** If ding2026memory (August 2026) includes experiments comparing gated vs
ungated memory updates across held-out tasks with BWT metrics, that would be the closest
overlap. From our reading, it does not; the paper focuses on diagnostic taxonomy rather than
gated remediation.

**Recommendation:** Proceed with submission. Related-work section must clearly distinguish our
claim from lin2026selfregress (within-task weight-update collapse) and ding2026memory (diagnostic
taxonomy without gating experiments). These are the two papers most likely to be raised by reviewers
as prior art.
