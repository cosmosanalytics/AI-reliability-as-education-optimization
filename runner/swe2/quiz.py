#!/usr/bin/env python3
"""Closed-book familiarity quiz (pre-education). Items come from knowledge-graph triples
(quiz_items.py); the model sees neither the graph nor the handbook. Each item is asked
SAMPLES times with shuffled option order; we record correctness, stated confidence, and
answer consistency (agreement with the modal answer)."""
import argparse
import json
import os
import random
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm  # noqa: E402
import quiz_items  # noqa: E402
from run_swe2 import FAMILY_TO_RULE, OUT_DIR  # noqa: E402

QUIZ_PATH = os.path.join(OUT_DIR, "quiz_raw.jsonl")
SUMMARY_PATH = os.path.join(OUT_DIR, "familiarity_quiz.json")
SAMPLES = 5
LETTERS = "ABCD"

PROMPT = (
    "Answer from your own knowledge of the conventions a well-run production Python service codebase "
    "would follow.\n\nQUESTION: {stem}\n{opts}\n\nReply with exactly two lines:\nANSWER: <letter>\n"
    "CONFIDENCE: <integer 0-100, the probability your answer is correct>"
)


def ask(job):
    rule, qi, s, (kg, stem, correct, distractors) = job
    rng = random.Random(f"{rule}-{qi}-{s}")
    opts = [correct] + list(distractors)
    rng.shuffle(opts)
    key = LETTERS[opts.index(correct)]
    text = PROMPT.format(stem=stem, opts="\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(opts)))
    r = llm.chat([{"role": "user", "content": text}], max_tokens=40, seed=rng.randint(0, 2**31 - 1))
    m = re.search(r"ANSWER:\s*\(?([A-D])", r["text"], re.I)
    c = re.search(r"CONFIDENCE:\s*(\d+)", r["text"], re.I)
    ans = m.group(1).upper() if m else None
    return {"rule": rule, "item": qi, "sample": s, "kg": kg, "key": key,
            "answer": ans, "chosen": opts[LETTERS.index(ans)] if ans else None,
            "correct": ans == key, "confidence": min(100, int(c.group(1))) / 100 if c else None,
            "raw": r["text"]}


def summarize(rows):
    out = {}
    rule_to_fam = {v: k for k, v in FAMILY_TO_RULE.items()}
    for rule in quiz_items.ITEMS:
        rs = [r for r in rows if r["rule"] == rule]
        items = sorted({r["item"] for r in rs})
        cons = []
        for i in items:
            ch = [r["chosen"] for r in rs if r["item"] == i]
            cons.append(Counter(ch).most_common(1)[0][1] / len(ch))
        confs = [r["confidence"] for r in rs if r["confidence"] is not None]
        acc = sum(r["correct"] for r in rs) / len(rs)
        out[rule_to_fam[rule]] = {
            "rule_id": rule, "n": len(rs), "accuracy": acc, "consistency": sum(cons) / len(cons),
            "mean_confidence": sum(confs) / len(confs) if confs else None,
            "overconfidence": (sum(confs) / len(confs) - acc) if confs else None,
            "per_item_accuracy": [sum(r["correct"] for r in rs if r["item"] == i) / SAMPLES for i in items],
        }
    pairs = [(r["confidence"], r["correct"]) for r in rows if r["confidence"] is not None]
    ece, nb = 0.0, 10
    for b in range(nb):
        xs = [(c, y) for c, y in pairs if (b / nb < c <= (b + 1) / nb) or (b == 0 and c == 0)]
        if xs:
            ece += len(xs) / len(pairs) * abs(sum(c for c, _ in xs) / len(xs) - sum(y for _, y in xs) / len(xs))
    return {"families": out, "overall_accuracy": sum(r["correct"] for r in rows) / len(rows),
            "overall_mean_confidence": sum(c for c, _ in pairs) / len(pairs), "ece": ece,
            "unparsed": sum(r["answer"] is None for r in rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = [(rule, qi, s, it) for rule, its in quiz_items.ITEMS.items() for qi, it in enumerate(its) for s in range(SAMPLES)]
    done = set()
    if os.path.exists(QUIZ_PATH):
        with open(QUIZ_PATH) as f:
            done = {(r["rule"], r["item"], r["sample"]) for r in map(json.loads, f)}
    todo = [j for j in jobs if (j[0], j[1], j[2]) not in done]
    with ThreadPoolExecutor(a.workers) as ex, open(QUIZ_PATH, "a") as f:
        for i, row in enumerate(ex.map(ask, todo), 1):
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"[{i}/{len(todo)}] {row['rule']} q{row['item']} s{row['sample']} -> {row['answer']} "
                  f"({'ok' if row['correct'] else 'x'}) conf={row['confidence']}", flush=True)
    with open(QUIZ_PATH) as f:
        rows = [json.loads(x) for x in f]
    summ = summarize(rows)
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summ, f, indent=2)
    print(json.dumps({k: v for k, v in summ.items() if k != "families"}, indent=1))
    for fam, s in sorted(summ["families"].items(), key=lambda kv: kv[1]["accuracy"]):
        print(f"{fam:20s} {s['rule_id']} acc={s['accuracy']:.2f} cons={s['consistency']:.2f} conf={s['mean_confidence']:.2f}")


if __name__ == "__main__":
    main()
