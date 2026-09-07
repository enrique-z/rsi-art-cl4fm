# Related Work Notes — cl4fm-selfevolve-forgetting

Comparative sentences for the 8 most important works.
Format: **what they did** / **what we do differently**.

---

## 1. Voyager (wang2023voyager)

**What they did:** Wang et al. build an open-ended embodied agent that accumulates a growing skill library in Minecraft; new skills are verified by an in-context execution check before being added, enabling monotonic forward progress on that single game domain.

**What we do differently:** We hold the task family constant (arithmetic, GSM8K) and evolve the skill/prompt library on it, then measure **backward transfer** to held-out families (ARC, BBH, HumanEval). Voyager never measures cross-domain interference; we show ungated evolution produces statistically significant forgetting even when each individual skill addition passes local verification.

---

## 2. Reflexion (shinn2023reflexion)

**What they did:** Shinn et al. let an agent verbally reflect on failure trajectories and store these reflections in an episodic memory, iterating within a single episode family to improve task success.

**What we do differently:** Reflexion's memory is session-scoped and task-specific; interference across task families is not studied. We run inference-time evolution for many cycles on one family, observe that accumulated reflections degrade held-out performance, and show that a retention gate (rehearsal anchors) recovers it.

---

## 3. ExpeL (zhao2023expel)

**What they did:** Zhao et al. extract cross-episode "insights" from experience pools into a persistent, queryable skill store; the agent retrieves and applies these insights at inference time without weight updates.

**What we do differently:** ExpeL evaluates insight transfer *within* the same task distribution and does not stress-test backward transfer when the insight store is densely updated from a single task family. Our work specifically isolates this regime and shows that dense updates without rehearsal anchors cause forgetting.

---

## 4. STaR / ReST (zelikman2022star, gulcehre2023rest)

**What they did:** Zelikman et al. bootstrap chain-of-thought rationales by filtering self-generated solutions on correctness, and Gulcehre et al. extend this with RL-guided grow/improve steps to fine-tune model weights.

**What we do differently:** STaR and ReST involve *weight updates*; our setting is fully inference-time (no gradient steps), relying on an evolving prompt/skill library. We study the analogous "soft fine-tuning" that occurs when an LLM's persistent memory scaffold is updated, and show forgetting still arises through context displacement even without gradient interference.

---

## 5. Self-Improvement Can Self-Regress (lin2026selfregress)

**What they did:** Lin (2026) documents a rise-and-collapse pattern in REINFORCE post-training for code: pass@1 on the *training* task peaks then crashes due to within-task policy over-optimization.

**What we do differently:** Lin shows within-task collapse under weight updates. Our contribution is orthogonal: we demonstrate **cross-task backward transfer** under inference-time evolution (no weight updates), and we show a rehearsal-anchor gate mitigates it. The two failure modes are complementary.

---

## 6. EWC (kirkpatrick2017ewc)

**What they did:** Kirkpatrick et al. penalize changes to parameters that are important for previously learned tasks, identified via the Fisher information matrix, thus protecting old knowledge during sequential weight updates.

**What we do differently:** EWC requires gradient access and operates on network weights. Our regime uses frozen open-source LLMs (Qwen3-8B / Llama-3.2-3B via Ollama) with no weight updates; we instead implement a rehearsal anchor in the memory-management layer, making EWC's approach inapplicable. Our paper demonstrates that the stability–plasticity tension re-emerges at the prompt/memory level.

---

## 7. GEM (lopezpaz2017gem)

**What they did:** Lopez-Paz & Ranzato project gradient updates to avoid increasing loss on episodic memory examples from previous tasks, formalizing backward transfer (BWT) and forward transfer (FWT) as evaluation metrics.

**What we do differently:** We adopt GEM's BWT/FWT metric framework but apply it to inference-time memory evolution rather than parameter updates. Our gating mechanism—accepting skill/prompt updates only when rehearsal anchors pass a verifier—is analogous to GEM's projection step but operates at the skill-library level without access to gradients.

---

## 8. Judging LLM-as-a-Judge (zheng2023mtbench)

**What they did:** Zheng et al. show that GPT-4 as an evaluator achieves high agreement with human raters on MT-Bench, establishing LLM-as-judge as a scalable evaluation paradigm but also identifying position and verbosity biases.

**What we do differently:** We use LLM-based verifiers as *gates* in the self-evolution loop rather than as the final metric, and we pair them with exogenous-label held-out benchmarks (GSM8K, ARC, BBH, MMLU) precisely because verifier bias could mask backward transfer. Our design explicitly accounts for the evaluator-corruption risk Zheng et al. identify.
