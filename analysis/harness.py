#!/usr/bin/env python3
"""harness.py -- real-data, real-model self-evolution / forgetting harness.

Everything here talks to a live Ollama server and real public benchmark files.
No fixtures, no synthetic items, no simulated model output. If the server is
down or a data file is missing the run aborts rather than degrading.

Families
--------
A (evolved)  GSM8K   -- openai/grade-school-math, train (evolution) + test (eval)
B (held-out) ARC-Challenge -- AI2 ARC-V1-Feb2018, Test split
C (held-out) CommonsenseQA -- AI2 dev_rand_split (labelled)

Arms
----
ungated  : memory edits accepted on the model's own self-judgement
gated    : accepted only if an exogenous checker shows non-decreasing accuracy
           on a family-A probe AND a fixed rehearsal anchor set (B/C items,
           disjoint from evaluation items) does not drop
neutral  : rival-mechanism control -- memory grown to matched token length with
           well-formed but task-irrelevant entries (context dilution only)

Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
DATA = PAPER / "data"
EVID = PAPER / "evidence"
# Dedicated Ollama instance for this paper. The machine's default server on
# :11434 is shared with other jobs; see DESIGN_NOTES.md "Infrastructure".
OLLAMA = os.environ.get("CL4FM_OLLAMA", "http://127.0.0.1:11500")
PARALLEL = int(os.environ.get("CL4FM_PARALLEL", "4"))

# ---------------------------------------------------------------- model calls

_CALL_LOG = None
_LOG_LOCK = threading.Lock()


def _open_call_log(path: Path):
    global _CALL_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    _CALL_LOG = open(path, "a", buffering=1)


MAX_RETRIES = 4


def ollama_chat(model, prompt, seed, num_predict, temperature=0.0, tag="",
                think=False, fmt=None):
    """Real Ollama /api/chat call with bounded retry. Every attempt is logged.

    The host is shared with other jobs and has been observed returning 500 after
    a five-minute queue wait, so a transient failure must not destroy a whole
    (arm, seed) cell. Retries are logged individually with `attempt` and
    `error`, so the retry rate is auditable rather than invisible. The call
    parameters -- including the seed -- are identical on every attempt, so a
    retry cannot change what is being measured.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _ollama_chat_once(model, prompt, seed, num_predict, temperature,
                                     tag, think, fmt, attempt)
        except RuntimeError:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(min(30, 3 * 2 ** (attempt - 1)))


def _ollama_chat_once(model, prompt, seed, num_predict, temperature, tag,
                      think, fmt, attempt):
    body = {
        "model": model,
        "stream": False,
        "options": {"temperature": temperature, "seed": seed, "num_predict": num_predict},
        "messages": [{"role": "user", "content": prompt}],
    }
    if fmt is not None:
        body["format"] = fmt
    if model.startswith("qwen3"):
        body["think"] = think
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    err = None
    text = ""
    d = {}
    try:
        with urllib.request.urlopen(req, timeout=1800) as r:
            d = json.loads(r.read())
        text = d.get("message", {}).get("content", "")
    except Exception as e:  # network / server failure -- recorded, then re-raised
        err = f"{type(e).__name__}: {e}"
    dt = time.time() - t0
    if _CALL_LOG is not None:
      rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tag": tag,
            "model": model,
            "seed": seed,
            "num_predict": num_predict,
            "temperature": temperature,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt_chars": len(prompt),
            "latency_s": round(dt, 3),
            "prompt_eval_count": d.get("prompt_eval_count"),
            "eval_count": d.get("eval_count"),
            "response_chars": len(text),
            "attempt": attempt,
            "error": err,
      }
      # Reflection and self-judgement calls decide what enters the memory, so
      # their full text is logged verbatim -- an auditor must be able to read
      # exactly what the model proposed and how it judged its own proposal.
      if "/reflect" in tag or "/judge" in tag:
          rec["prompt_text"] = prompt
          rec["response_text"] = text
      with _LOG_LOCK:
        _CALL_LOG.write(json.dumps(rec) + "\n")
    if err is not None:
        raise RuntimeError(f"ollama call failed [{tag}]: {err}")
    return text


# ----------------------------------------------------------------- benchmarks

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_gsm8k(split):
    p = DATA / f"gsm8k_{split}.jsonl"
    out = []
    for i, line in enumerate(open(p)):
        r = json.loads(line)
        ans = r["answer"].split("####")[-1].strip().replace(",", "")
        out.append({"uid": f"gsm8k_{split}_{i}", "family": "A", "question": r["question"],
                    "gold": ans, "type": "numeric"})
    return out


def load_arc():
    p = DATA / "arc_extract/ARC-V1-Feb2018-2/ARC-Challenge/ARC-Challenge-Test.jsonl"
    out = []
    for i, line in enumerate(open(p)):
        r = json.loads(line)
        ch = r["question"]["choices"]
        labels = [c["label"] for c in ch]
        # keep only canonical A-D/A-E letter items so the answer space is fixed
        if not all(l in "ABCDE" for l in labels):
            continue
        if r["answerKey"] not in labels:
            continue
        opts = "\n".join(f"{c['label']}. {c['text']}" for c in ch)
        out.append({"uid": f"arc_{r['id']}", "family": "B",
                    "question": r["question"]["stem"] + "\n" + opts,
                    "gold": r["answerKey"], "type": "mcq",
                    "labels": labels})
    return out


def load_csqa():
    p = DATA / "csqa_dev.jsonl"
    out = []
    for line in open(p):
        r = json.loads(line)
        ch = r["question"]["choices"]
        labels = [c["label"] for c in ch]
        opts = "\n".join(f"{c['label']}. {c['text']}" for c in ch)
        out.append({"uid": f"csqa_{r['id']}", "family": "C",
                    "question": r["question"]["stem"] + "\n" + opts,
                    "gold": r["answerKey"], "type": "mcq",
                    "labels": labels})
    return out


# -------------------------------------------------------------------- grading

_NUM = re.compile(r"-?\$?\d[\d,]*\.?\d*")


def extract_numeric(text):
    """Deterministic: prefer '#### <n>', else the last number in the reply.

    Returns (answer_or_None, parse_mode). None => ambiguous/unparseable, logged.
    """
    m = re.findall(r"####\s*\$?(-?[\d,]+\.?\d*)", text)
    if m:
        return m[-1].replace(",", "").rstrip("."), "hash"
    m = _NUM.findall(text)
    if m:
        return m[-1].replace(",", "").replace("$", "").rstrip("."), "lastnum"
    return None, "none"


def extract_mcq(text, labels):
    """Deterministic: 'Answer: X' first, else last standalone label letter."""
    m = re.findall(r"[Aa]nswer\s*[:\-]?\s*\(?([A-E])\)?", text)
    if m and m[-1] in labels:
        return m[-1], "answerkw"
    m = re.findall(r"(?<![A-Za-z])([A-E])(?![A-Za-z])", text)
    m = [x for x in m if x in labels]
    if m:
        return m[-1], "lastletter"
    return None, "none"


def num_eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except Exception:
        return str(a).strip() == str(b).strip()


def grade(item, text):
    if item["type"] == "numeric":
        pred, mode = extract_numeric(text)
        ok = pred is not None and num_eq(pred, item["gold"])
    else:
        pred, mode = extract_mcq(text, item["labels"])
        ok = pred is not None and pred == item["gold"]
    return bool(ok), pred, mode


# --------------------------------------------------------------------- prompts

MEM_HEADER = ("You have a persistent memory of insights learned from past problems. "
              "Use it if it helps.\n--- MEMORY ---\n{mem}\n--- END MEMORY ---\n\n")

ASK_NUMERIC = ("Solve the problem. Reason briefly, then end your reply with "
               "'#### <number>' on its own line.\n\nProblem: {q}\n")

ASK_MCQ = ("Answer the multiple-choice question. Reason in at most two short "
           "sentences, then end your reply with 'Answer: <letter>'.\n\n{q}\n")


def render_memory(entries):
    if not entries:
        return ""
    body = "\n".join(f"- {e}" for e in entries)
    return MEM_HEADER.format(mem=body)


def ask(model, item, memory, seed, cfg, tag):
    tmpl = ASK_NUMERIC if item["type"] == "numeric" else ASK_MCQ
    np_ = cfg["np_numeric"] if item["type"] == "numeric" else cfg["np_mcq"]
    prompt = render_memory(memory) + tmpl.format(q=item["question"])
    return ollama_chat(model, prompt, seed, np_, cfg["temperature"], tag)


def _ask_and_grade(args):
    model, it, memory, seed, cfg, tag = args
    txt = ask(model, it, memory, seed, cfg, tag)
    return (it,) + grade(it, txt)


def evaluate(model, items, memory, seed, cfg, tag, out_fh, meta):
    """Score a fixed item set (parallel over items). Per-item rows for McNemar.

    Parallelism is over ITEMS ONLY. Determinism is unaffected: every call
    carries its own fixed seed and temperature 0, and grading is order-free.
    """
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        results = list(ex.map(_ask_and_grade,
                              [(model, it, memory, seed, cfg, tag) for it in items]))
    n_ok = 0
    for it, ok, pred, mode in results:
        n_ok += ok
        rec = dict(meta)
        rec.update({"uid": it["uid"], "family": it["family"], "correct": int(ok),
                    "pred": pred, "gold": it["gold"], "parse_mode": mode,
                    "ambiguous": pred is None})
        out_fh.write(json.dumps(rec) + "\n")
    return n_ok / len(items)


# ---------------------------------------------------------- self-evolution loop

REFLECT = """You just attempted {n} grade-school math word problems using your current memory.
Here is what happened (the correct answer is given for each):

{transcript}

Write exactly {budget} new memory entries. Each entry is one short, reusable,
self-contained rule or insight that would help you solve problems like these
next time. Do not restate a specific problem; write something general.

Reply with a JSON object of the form
{{"edits": [{{"op":"add","text":"..."}}, {{"op":"add","text":"..."}}]}}
containing exactly {budget} entries.
"""

REFLECT_WITH_DELETE = """You just attempted {n} grade-school math word problems using your current memory.
Here is what happened (the correct answer is given for each):

{transcript}

Your current memory entries, indexed:
{memlist}

Write exactly {budget} memory edits. Each edit is either a new reusable rule to
add, or the removal of an existing entry above that is not helping you. Prefer
"add" unless an existing entry is clearly useless. Write general rules, not
restatements of a specific problem.

Reply with a JSON object of the form
{{"edits": [{{"op":"add","text":"..."}}, {{"op":"delete","index":0}}]}}
containing exactly {budget} entries.
"""

SELFJUDGE = """You are judging whether a proposed addition to your persistent memory will
make you better at solving problems in general. Answer with one word.

Proposed memory entry: "{text}"

Will keeping this entry improve your future performance? Answer KEEP or DROP."""

NEUTRAL_POOL = [
    "The Danube flows through ten countries before reaching the Black Sea.",
    "A standard shipping pallet in Europe measures 1200 by 800 millimetres.",
    "Basalt is an extrusive igneous rock formed from rapidly cooling lava.",
    "The kakapo is a flightless nocturnal parrot endemic to New Zealand.",
    "Cartography distinguishes conformal, equal-area and equidistant projections.",
    "The Hanseatic League coordinated trade among northern European ports.",
    "Sourdough fermentation relies on wild yeasts and lactic acid bacteria.",
    "Mount Erebus in Antarctica holds one of the few persistent lava lakes.",
    "A hurdy-gurdy produces sound with a rosined wheel turned by a crank.",
    "Cochineal insects were historically farmed for carmine dye.",
    "The Bessemer process removed impurities from pig iron by blowing air through it.",
    "Lichens are composite organisms of a fungus and a photosynthetic partner.",
    "Ushuaia in Tierra del Fuego is often called the southernmost city.",
    "Terrazzo flooring embeds stone chips in a cement or resin matrix.",
    "The koto is a Japanese zither with thirteen strings and movable bridges.",
    "Alluvial fans form where a stream leaves a confined channel onto a plain.",
    "Semaphore lines relayed messages by rotating mechanical arms on towers.",
    "The Marianas Trench reaches nearly eleven kilometres below sea level.",
    "Damascus steel patterns arise from banded carbide microstructures.",
    "Baleen whales filter feed using keratin plates instead of teeth.",
    "The Antikythera mechanism modelled astronomical cycles with bronze gears.",
    "Espresso extraction typically uses about nine bars of pump pressure.",
    "Peat bogs accumulate partially decayed plant matter under waterlogged conditions.",
    "The tuatara is the only surviving member of the order Rhynchocephalia.",
    "Guilloche engraving cuts repeating geometric patterns into metal.",
    "Foucault's pendulum demonstrates the rotation of the Earth.",
    "Mangrove roots trap sediment and buffer coastlines against storm surge.",
    "The shakuhachi is an end-blown bamboo flute used in Zen practice.",
    "Anodising thickens the natural oxide layer on aluminium surfaces.",
    "Salt flats such as Salar de Uyuni form from evaporated prehistoric lakes.",
]


# Ollama structured-output schema for the edit proposal. Forcing the shape at
# decode time removes a whole class of silent budget starvation: without it a 3B
# model emits near-JSON (`["rule": "..."]`) that the parser must discard, which
# would make the proposal budget differ across arms by accident rather than by
# design. Measured in the pre-run pilot; see DESIGN_NOTES.
EDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "edits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["add", "delete"]},
                    "text": {"type": "string"},
                    "index": {"type": "integer"},
                },
                "required": ["op"],
            },
        }
    },
    "required": ["edits"],
}


def parse_edits(text, budget, n_mem):
    """Deterministic, auditable parse of the model's proposed edits."""
    arr = None
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and isinstance(obj.get("edits"), list):
            arr = obj["edits"]
        elif isinstance(obj, list):
            arr = obj
    except Exception:
        pass
    if arr is None:
        m = re.search(r"\[.*\]", text, re.S)
        if not m:
            return [], "no_json"
        try:
            arr = json.loads(m.group(0))
        except Exception:
            return [], "bad_json"
    if not isinstance(arr, list):
        return [], "not_list"
    out = []
    for e in arr:
        if not isinstance(e, dict):
            continue
        op = str(e.get("op", "")).lower()
        if op == "add" and isinstance(e.get("text"), str) and e["text"].strip():
            out.append({"op": "add", "text": " ".join(e["text"].split())[:400]})
        elif op == "delete":
            try:
                idx = int(e["index"])
            except Exception:
                continue
            if 0 <= idx < n_mem:
                out.append({"op": "delete", "index": idx})
        if len(out) >= budget:
            break
    return out, "ok"


def apply_edits(memory, edits):
    mem = list(memory)
    for e in edits:
        if e["op"] == "add":
            mem.append(e["text"])
    dels = sorted({e["index"] for e in edits if e["op"] == "delete"}, reverse=True)
    for i in dels:
        if i < len(mem):
            mem.pop(i)
    return mem


def probe_accuracy(model, items, memory, seed, cfg, tag):
    with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        res = list(ex.map(_ask_and_grade,
                          [(model, it, memory, seed, cfg, tag) for it in items]))
    return sum(r[1] for r in res) / len(items)


def run_cell(model, arm, seed, cfg, pools, out_dir):
    """One (arm, seed) trajectory. Checkpoints after every round."""
    rng = random.Random(seed)
    cellfile = out_dir / f"cell_{arm}_seed{seed}.jsonl"
    fh = open(cellfile, "a", buffering=1)
    memory = []
    rounds_log = []
    train = list(pools["A_train"])
    rng.shuffle(train)
    cursor = 0
    accepted_total = 0
    proposed_total = 0

    for rnd in range(1, cfg["rounds"] + 1):
        batch = train[cursor:cursor + cfg["n_A_train"]]
        cursor += cfg["n_A_train"]
        tag = f"{arm}/s{seed}/r{rnd}"

        if arm.startswith("neutral"):
            # Rival-mechanism control (pre-declared gate-13b falsifier): grow the
            # memory to MATCHED LENGTH with well-formed but task-irrelevant
            # entries. No attempts, no reflection, no self-judgement -- the only
            # thing that changes across rounds is how many characters of
            # well-formed prose sit in front of the question.
            #
            # The per-round character target is measured from the ungated arm's
            # realised memory (cfg["neutral_target_chars"], filled in by
            # tools/set_neutral_target.py after the ungated arm completes), so
            # "length-matched" is matched to observed data, not to a guess.
            # "neutral" is the pre-declared arm, length-matched to ungated.
            # "neutralshort" is the exploratory A4 arm, length-matched to gated.
            # Each reads its OWN target vector; neither can see the other's.
            tkey = ("neutral_target_chars" if arm == "neutral"
                    else f"{arm}_target_chars")
            targets = cfg.get(tkey)
            if not targets:
                raise RuntimeError(
                    f"arm '{arm}' requires cfg['{tkey}'] (per-round cumulative "
                    "character targets measured from the arm it is matched to). "
                    "Run that arm first, then analysis/set_neutral_target.py.")
            target = targets[min(rnd - 1, len(targets) - 1)]
            picks = []
            j = 0
            cur = sum(len(x) for x in memory)
            while cur < target and j < 4 * len(NEUTRAL_POOL):
                p = NEUTRAL_POOL[(seed * 7 + rnd * 5 + j) % len(NEUTRAL_POOL)]
                picks.append(p)
                cur += len(p)
                j += 1
            memory = memory + picks
            edits = [{"op": "add", "text": p} for p in picks]
            proposed, accepted = len(picks), len(picks)
            proposed_total += proposed
            parse_status = f"neutral_control_target_chars={target}"
        else:
            # attempt with current memory
            with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
                attempts = list(ex.map(
                    _ask_and_grade,
                    [(model, it, memory, seed, cfg, tag + "/attempt") for it in batch]))
            transcript = [
                f"Problem: {it['question'][:400]}\n"
                f"Your answer: {pred} ({'CORRECT' if ok else 'WRONG'}); "
                f"correct answer: {it['gold']}"
                for it, ok, pred, _ in attempts]
            # Offer the delete op only when there is something to delete: with an
            # empty memory a 3B model happily emits deletes of indices that do
            # not exist, which the parser then discards, silently starving the
            # proposal budget. Measured in the pre-run pilot; see DESIGN_NOTES.
            if memory:
                memlist = "\n".join(f"{i}: {t}" for i, t in enumerate(memory))
                rprompt = REFLECT_WITH_DELETE.format(
                    n=len(batch), transcript="\n\n".join(transcript),
                    budget=cfg["edit_budget"], memlist=memlist)
            else:
                rprompt = REFLECT.format(
                    n=len(batch), transcript="\n\n".join(transcript),
                    budget=cfg["edit_budget"])
            rtxt = ollama_chat(model, rprompt, seed, cfg["np_reflect"],
                               cfg["temperature"], tag + "/reflect",
                               fmt=EDIT_SCHEMA)
            edits, parse_status = parse_edits(rtxt, cfg["edit_budget"], len(memory))
            proposed = len(edits)
            proposed_total += proposed

            if arm == "ungated":
                adds = [e for e in edits if e["op"] == "add"]
                with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
                    judgements = list(ex.map(
                        lambda e: ollama_chat(model, SELFJUDGE.format(text=e["text"]),
                                              seed, cfg["np_judge"], cfg["temperature"],
                                              tag + "/judge"),
                        adds))
                keep_add = {id(e) for e, j in zip(adds, judgements) if "KEEP" in j.upper()}
                edits = [e for e in edits
                         if e["op"] == "delete" or id(e) in keep_add]
            elif arm == "gated":
                cand = apply_edits(memory, edits)
                a_base = probe_accuracy(model, pools["A_gate"], memory, seed, cfg, tag + "/gateA0")
                a_new = probe_accuracy(model, pools["A_gate"], cand, seed, cfg, tag + "/gateA1")
                r_base = probe_accuracy(model, pools["anchor"], memory, seed, cfg, tag + "/gateR0")
                r_new = probe_accuracy(model, pools["anchor"], cand, seed, cfg, tag + "/gateR1")
                passed = (a_new >= a_base) and (r_new >= r_base)
                fh.write(json.dumps({"kind": "gate", "arm": arm, "seed": seed, "round": rnd,
                                     "a_base": a_base, "a_new": a_new,
                                     "anchor_base": r_base, "anchor_new": r_new,
                                     "passed": bool(passed)}) + "\n")
                if not passed:
                    edits = []
            accepted = len(edits)
            memory = apply_edits(memory, edits)

        accepted_total += accepted
        mem_chars = sum(len(x) for x in memory)
        rec = {"kind": "round", "arm": arm, "seed": seed, "round": rnd,
               "n_proposed": proposed, "n_accepted": accepted,
               "mem_entries": len(memory), "mem_chars": mem_chars,
               "parse_status": parse_status, "memory": memory}
        fh.write(json.dumps(rec) + "\n")
        rounds_log.append(rec)

    fh.close()
    return memory, rounds_log, accepted_total, proposed_total


# ------------------------------------------------------------------------ main

def build_pools(cfg):
    rng = random.Random(cfg["item_seed"])
    a_train = load_gsm8k("train")
    a_test = load_gsm8k("test")
    b = load_arc()
    c = load_csqa()
    rng.shuffle(a_train); rng.shuffle(a_test); rng.shuffle(b); rng.shuffle(c)
    nB = cfg["n_eval_B"]; nC = cfg["n_eval_C"]
    nA = cfg["n_eval_A"]
    ka = cfg["n_anchor_B"]; kc = cfg["n_anchor_C"]
    pools = {
        "A_train": a_train[: cfg["rounds"] * cfg["n_A_train"] * 3],
        "A_gate": a_train[-cfg["n_gate_A"]:],
        "A_test": a_test[:nA],
        "B": b[:nB],
        "C": c[:nC],
        # rehearsal anchor: held separate from the evaluation items
        "anchor": b[nB:nB + ka] + c[nC:nC + kc],
    }
    assert not ({i["uid"] for i in pools["B"]} & {i["uid"] for i in pools["anchor"]})
    assert not ({i["uid"] for i in pools["C"]} & {i["uid"] for i in pools["anchor"]})
    assert not ({i["uid"] for i in pools["A_test"]} & {i["uid"] for i in pools["A_train"]})
    return pools


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--arms", default="ungated,gated,neutral")
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--noise-null", action="store_true",
                    help="pre-declared evaluation-noise rival: re-evaluate the "
                         "SAME fixed item sets with an EMPTY memory under a "
                         "different sampling seed, so the BWT/FG statistics can "
                         "be compared against the null distribution of "
                         "'accuracy moved but nothing was learned'.")
    ap.add_argument("--noise-seed-offset", type=int, default=100)
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    out_dir = Path(a.out or (EVID / "runs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    _open_call_log(EVID / "calls.jsonl")

    pools = build_pools(cfg)
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else cfg["seeds"]
    arms = a.arms.split(",")
    model = cfg["model"]

    items_fh = open(out_dir / "per_item.jsonl", "a", buffering=1)

    # --- round 0: memory is empty in every arm, so evaluate ONCE per seed and
    # share the result across arms (identical model, seed, memory, item set).
    r0 = {}
    for seed in seeds:
        r0[seed] = {}
        for fam, key in (("A", "A_test"), ("B", "B"), ("C", "C")):
            f = out_dir / f"r0_seed{seed}_{fam}.done"
            if f.exists():
                r0[seed][fam] = json.loads(f.read_text())["acc"]
                continue
            acc = evaluate(model, pools[key], [], seed, cfg, f"r0/s{seed}/{fam}",
                           items_fh, {"arm": "ROUND0", "seed": seed, "round": 0})
            f.write_text(json.dumps({"acc": acc, "n": len(pools[key])}))
            r0[seed][fam] = acc
            print(f"[round0] seed={seed} {fam} acc={acc:.3f}", flush=True)

    # --- pre-declared rival mechanism 2: evaluation noise -------------------
    # Round 0 re-evaluated on the SAME item sets with the SAME empty memory but
    # a different sampling seed. The resulting per-seed accuracy differences are
    # the null distribution of the FG/BWT statistics under "nothing was learned,
    # only the sampling changed". Any BWT inside this band is noise, not
    # interference, and the report says so.
    if a.noise_null:
        nfh = open(out_dir / "noise_null.jsonl", "a", buffering=1)
        for seed in seeds:
            nseed = seed + a.noise_seed_offset
            row = {"seed": seed, "noise_seed": nseed}
            for fam, key in (("A", "A_test"), ("B", "B"), ("C", "C")):
                f = out_dir / f"r0b_seed{seed}_{fam}.done"
                if f.exists():
                    acc = json.loads(f.read_text())["acc"]
                else:
                    acc = evaluate(model, pools[key], [], nseed, cfg,
                                   f"r0b/s{seed}/{fam}", items_fh,
                                   {"arm": "ROUND0B", "seed": seed, "round": 0})
                    f.write_text(json.dumps({"acc": acc, "n": len(pools[key]),
                                             "noise_seed": nseed}))
                row[f"acc0_{fam}"] = r0[seed][fam]
                row[f"acc0b_{fam}"] = acc
                row[f"noise_{fam}"] = acc - r0[seed][fam]
            nfh.write(json.dumps(row) + "\n")
            print(f"[noise-null] seed={seed} "
                  + " ".join(f"{f}={row[f'noise_{f}']:+.4f}" for f in "ABC"),
                  flush=True)
        nfh.close()
        items_fh.close()
        return

    summary_fh = open(out_dir / "cells.jsonl", "a", buffering=1)
    for arm in arms:
        for seed in seeds:
            done = out_dir / f"done_{arm}_seed{seed}.json"
            if done.exists():
                print(f"[skip] {arm} seed={seed} already complete", flush=True)
                continue
            t0 = time.time()
            mem, rlog, acc_edits, prop_edits = run_cell(model, arm, seed, cfg, pools, out_dir)
            accR = {}
            for fam, key in (("A", "A_test"), ("B", "B"), ("C", "C")):
                accR[fam] = evaluate(model, pools[key], mem, seed, cfg,
                                     f"{arm}/s{seed}/rR/{fam}", items_fh,
                                     {"arm": arm, "seed": seed, "round": cfg["rounds"]})
            row = {"arm": arm, "seed": seed, "rounds": cfg["rounds"],
                   "acc0": r0[seed], "accR": accR,
                   "FG": accR["A"] - r0[seed]["A"],
                   "BWT_B": accR["B"] - r0[seed]["B"],
                   "BWT_C": accR["C"] - r0[seed]["C"],
                   "accepted_edits": acc_edits, "proposed_edits": prop_edits,
                   "mem_entries": len(mem), "mem_chars": sum(len(x) for x in mem),
                   "wall_s": round(time.time() - t0, 1)}
            summary_fh.write(json.dumps(row) + "\n")
            done.write_text(json.dumps(row))
            print(f"[cell] {arm} s{seed} FG={row['FG']:+.3f} "
                  f"BWT_B={row['BWT_B']:+.3f} BWT_C={row['BWT_C']:+.3f} "
                  f"({row['wall_s']}s)", flush=True)
    summary_fh.close()
    items_fh.close()


if __name__ == "__main__":
    main()
