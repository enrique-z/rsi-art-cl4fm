# Reproducibility Artifact — cl4fm-selfevolve-forgetting

**Venue:** CL4FMAgents — Continual Learning in the Era of Foundation Models and Embodied
Agents, NeurIPS 2026 (Workshop). Double-blind submission.

**Anonymous release.** This repository holds the reproducibility artifacts for one
double-blind submission. Absolute paths have been replaced by placeholders
(`<REPO_ROOT>`, `<HOME>`) and identifying strings removed. The manuscript itself
(`main.tex` / `main.pdf`) is not part of this repository.

---

## What the paper claims

An LLM agent that recursively self-evolves its persistent memory/skill library (learned
insights, worked exemplars, procedural rules — no weight updates) on task family A for R
rounds shows **negative backward transfer** on held-out task families B and C when edits
are accepted by the agent's own self-judgement only ("ungated"), and that a **verifier +
retention gate** (edits accepted only if an exogenous checker confirms improvement on A
and accuracy on a small rehearsal set from B/C does not drop) yields higher (less
negative) backward transfer. Both were pre-registered in
`A2_PREDECLARATION_2026-09-07.md` before any data were collected — and **at six seeds
both are refuted**, which is what the paper reports. The pre-declared *falsifier* does
fire: a length-matched content-free memory arm degrades more than the evolved one, so the
cost of a growing memory is context dilution rather than content interference.

**Seed count matters when reading this repository.** The experiment first ran at three
seeds; amendment **A5** extended it to six under a reporting rule fixed before the first
new row existed, and amendment **A6** corrected the statistical reporting. The ledger,
stamp manifest, `evidence/runs/`, `evidence/aggregates.json`, `EXPERIMENT_REPORT.md` and
the figure in this repository are all the **six-seed** versions that the paper reports.
`DOMAIN_AUDIT.md` and `CLAIMS.md` are the earlier **three-seed** audit documents, kept
unedited as part of the record; each carries a header saying so, and `DOMAIN_AUDIT.md`
tabulates exactly what A5 changed. See `evidence/DESIGN_NOTES.md` for the full
operational record and every deviation from the pre-registered design.

---

## How to reproduce

### Prerequisites

- **Python 3.14** (tested on 3.14.7, macOS arm64)
- **Ollama** with `qwen3:8b` (non-thinking mode; `llama3.2:3b` is the documented fallback)
  served on `127.0.0.1:11500`
- Public datasets (see "Data" section below for URLs and SHA-256 hashes)

### Data

Download and place in `data/`:

| File | URL | SHA-256 |
|------|-----|---------|
| `gsm8k_train.jsonl` | https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl | `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465` |
| `gsm8k_test.jsonl` | https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl | `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14` |
| `arc.zip` (→ `arc_extract/`) | https://ai2-public-datasets.s3.amazonaws.com/arc/ARC-V1-Feb2018.zip | zip `6d2d5ab50b2ceec6ba5f79c921be77cf2de712ea25a2b3f4fff3acc101cecfa0` |
| `csqa_dev.jsonl` | https://s3.amazonaws.com/commensenseqa/dev_rand_split.jsonl | `3210497fdaae614ac085d9eb873dd7f4d49b6f965a93adadc803e1229fd8a02a` |

The ARC zip is ~649 MB; it is NOT included in this bundle (see "Not included" below).

### Reproduce in order

```bash
# 1. Verify the environment
python3 --version        # expect 3.14.x
ollama list              # qwen3:8b must appear

# 2. Run the full experiment (all arms, all seeds)
cd analysis
bash run_full.sh

# 3. Aggregate results
python3 aggregate.py

# 4. Reproduce the figure
python3 make_figure.py

# 5. Verify all ledger rows match the stamp manifest
python3 guard.py --strict
```

All numeric results reported in the paper pass through the ledger
(`evidence/cl4fm_selfevolve_forgetting_ledger.jsonl`) and are verified by `guard.py`
against the stamp manifest.

**Reproducing all six seeds.** `analysis/config_full.json` is the configuration frozen
*before* the run and still names `"seeds": [1, 2, 3]` — it is deliberately left as
written so the pre-run commitment is auditable. The six-seed grid of amendment A5 was
produced by re-running the same harness with the extra seeds and no other change:

```bash
python3 analysis/harness.py --config analysis/config_full.json --arms ungated      --seeds 4,5,6
python3 analysis/harness.py --config analysis/config_full.json --arms gated        --seeds 4,5,6
python3 analysis/harness.py --config analysis/config_full.json --arms neutral      --seeds 4,5,6
python3 analysis/harness.py --config analysis/config_full.json --arms neutralshort --seeds 4,5,6
python3 analysis/harness.py --config analysis/config_full.json --noise-null        --seeds 4,5,6
python3 analysis/aggregate.py && python3 analysis/make_figure.py
```

`analysis/aggregate.py` picks up whatever seeds are present in `evidence/runs/` and
emits the ledger, the stamp manifest and `evidence/aggregates.json` for all of them. The
six-seed records for every arm are already checked in under `evidence/runs/`.

---

## File inventory

| Path | Description |
|------|-------------|
| `A2_PREDECLARATION_2026-09-07.md` | Pre-registration (binding design, before any data) |
| `CLAIMS.md` | Claim/evidence/risk registry — **three-seed scope**, superseded in part by A5 |
| `DOMAIN_AUDIT.md` | Domain validity audit — **three-seed scope**; its header tabulates what A5 changed |
| `EXPERIMENT_REPORT.md` | Post-hoc report; numeric tables regenerated from `evidence/aggregates.json` (six seeds) |
| `analysis/harness.py` | Core self-evolution harness |
| `analysis/aggregate.py` | Ledger aggregation |
| `analysis/make_figure.py` | Figure generation |
| `analysis/guard.py` | Anti-fabrication guard (E1–E7) |
| `analysis/run_full.sh` | Top-level reproduction script |
| `evidence/cl4fm_selfevolve_forgetting_ledger.jsonl` | Per-claim evidence ledger |
| `evidence/cl4fm_selfevolve_forgetting_stamp_manifest.json` | Stamp manifest for guard |
| `evidence/DESIGN_NOTES.md` | Operational record, amendments, software versions |
| `evidence/runs/` | Per-seed per-arm run records (JSONL) |
| `evidence/pilot/` | Pilot run records |
| `refs.bib` | Bibliography (BibTeX) |
| `build.guard.log` | Anti-fabrication guard output for the submitted manuscript: every stamped cell resolved against the manifest |
| `lit/` | Literature notes, novelty check, citation verification log |

---

## Software versions (from `evidence/DESIGN_NOTES.md`)

| Component | Version |
|-----------|---------|
| Python | 3.14.7 |
| Ollama model (primary) | qwen3:8b, non-thinking mode |
| Ollama model (fallback) | llama3.2:3b |
| Platform | macOS, arm64 |

---

## Data that must be downloaded separately

- **arc.zip** (649 MB): https://ai2-public-datasets.s3.amazonaws.com/arc/ARC-V1-Feb2018.zip —
  SHA-256 `6d2d5ab50b2ceec6ba5f79c921be77cf2de712ea25a2b3f4fff3acc101cecfa0`.
  This is the AI2 ARC dataset; excluded from this bundle due to size.

All other benchmark files (`gsm8k_*.jsonl`, `csqa_dev.jsonl`) are under 5 MB and
their hashes are given above.

---

## What is NOT included and why

| Excluded | Reason |
|----------|--------|
| `main.tex` / `main.pdf` | The manuscript is not part of the artifact repository |
| `data/arc.zip` | 649 MB — far above this repository's size budget. Re-download it from the URL above and verify the SHA-256; extract to `data/arc_extract/` before running `analysis/run_full.sh`. |
| `data/` (benchmark CSVs/JSONLs) | Downloaded corpora; URLs and hashes are in `evidence/DESIGN_NOTES.md` |
| `__pycache__/` | Python bytecode |
| `.git/` | Repository history |
