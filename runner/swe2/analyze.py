#!/usr/bin/env python3
"""SWE-2 analysis: familiarity ranking (pre-education) vs gains after education."""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_swe2 import ARMS, FAMILY_TASKS, FAMILY_TO_RULE, OUT_DIR, load_records  # noqa: E402

QUIZ = os.path.join(OUT_DIR, "familiarity_quiz.json")


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return float("nan") if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y, perms=20000, seed=0):
    rho = pearson(rank(x), rank(y))
    if math.isnan(rho):
        return rho, float("nan")
    rng, ry, hits = random.Random(seed), rank(y), 0
    rx = rank(x)
    for _ in range(perms):
        sh = ry[:]
        rng.shuffle(sh)
        v = pearson(rx, sh)
        if not math.isnan(v) and abs(v) >= abs(rho) - 1e-12:
            hits += 1
    return rho, (hits + 1) / (perms + 1)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    recs = [r for r in load_records() if r.get("run_idx", 0) > 0]
    quiz = json.load(open(QUIZ))["families"] if os.path.exists(QUIZ) else {}
    fams = list(FAMILY_TASKS)
    cell = {}
    for r in recs:
        cell.setdefault((r["arm"], r["family"]), []).append(r)

    def rate(arm, fam):
        rs = cell.get((arm, fam), [])
        return (sum(r["strict_pass"] for r in rs) / len(rs)) if rs else float("nan"), len(rs)

    rows = []
    for f in fams:
        q = quiz.get(f, {})
        row = {"family": f, "rule_id": FAMILY_TO_RULE[f], "quiz_acc": q.get("accuracy", float("nan")),
               "quiz_cons": q.get("consistency", float("nan")), "quiz_conf": q.get("mean_confidence", float("nan"))}
        for a in ARMS:
            row[a], row[a + "_n"] = rate(a, f)
        rows.append(row)
    have = [r for r in rows if not math.isnan(r["B0"]) and not math.isnan(r["quiz_acc"])]
    if have:
        ra, rb = rank([r["quiz_acc"] for r in have]), rank([r["B0"] for r in have])
        for r, x, y in zip(have, ra, rb):
            r["familiarity"] = (x + y) / 2
    for r in rows:
        r.setdefault("familiarity", float("nan"))
    rows.sort(key=lambda r: (r["familiarity"], r["quiz_acc"], r["B0"]))

    L = ["# SWE-2 results: ontology + knowledge harness + confidence harness", ""]
    L += ["Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp, CPU). Strict pass on hidden tests.", ""]
    L += ["## Arm totals", "", "| Arm | strict pass | rate | 95% CI | gain vs B0 (pp) |", "|---|---|---|---|---|"]
    tot = {}
    for a in ARMS:
        rs = [r for r in recs if r["arm"] == a]
        k, n = sum(r["strict_pass"] for r in rs), len(rs)
        tot[a] = (k, n)
        if n:
            lo, hi = wilson(k, n)
            g = 100 * (k / n - tot["B0"][0] / tot["B0"][1]) if tot["B0"][1] else float("nan")
            L.append(f"| {a} | {k}/{n} | {100 * k / n:.1f}% | {100 * lo:.0f}-{100 * hi:.0f}% | {g:+.1f} |")
    L += ["", "## Familiarity ranking (before education) and per-family strict pass", "",
          "Familiarity = mean of the ranks of closed-book quiz accuracy and B0 debugging pass rate (1 = least familiar).",
          "", "| Pos | Family | Rule | Quiz acc | Quiz consistency | Quiz conf | " + " | ".join(ARMS) + " |",
          "|" + "---|" * (6 + len(ARMS))]
    for i, r in enumerate(rows, 1):
        L.append(f"| {i} | {r['family']} | {r['rule_id']} | {r['quiz_acc']:.2f} | {r['quiz_cons']:.2f} | "
                 f"{r['quiz_conf']:.2f} | " + " | ".join(
                     f"{100 * r[a]:.0f}% ({r[a + '_n']})" if r[a + "_n"] else "-" for a in ARMS) + " |")
    L += ["", "## Familiarity vs gain (Spearman rho across families, permutation p)", "",
          "| Gain of arm over B0 | vs quiz accuracy | vs B0 pass rate | vs composite familiarity | vs quiz consistency |",
          "|---|---|---|---|---|"]
    corr = {}
    for a in ARMS[1:]:
        sub = [r for r in rows if r[a + "_n"] and r["B0_n"] and not math.isnan(r["familiarity"])]
        if len(sub) < 4:
            continue
        gain = [r[a] - r["B0"] for r in sub]
        res = {m: spearman([r[m] for r in sub], gain) for m in ("quiz_acc", "B0", "familiarity", "quiz_cons")}
        corr[a] = {m: {"rho": v[0], "p": v[1], "n": len(sub)} for m, v in res.items()}
        L.append(f"| {a} (n={len(sub)}) | " + " | ".join(
            f"{res[m][0]:+.2f} (p={res[m][1]:.3f})" for m in ("quiz_acc", "B0", "familiarity", "quiz_cons")) + " |")
    # education-specific effect: KNOW over PLACEBO
    for a, b in (("KNOW", "PLACEBO"), ("KNOW_SURE", "KNOW"), ("SURE", "B0")):
        sub = [r for r in rows if r[a + "_n"] and r[b + "_n"] and not math.isnan(r["familiarity"])]
        if len(sub) >= 4:
            rho, p = spearman([r["familiarity"] for r in sub], [r[a] - r[b] for r in sub])
            L.append(f"| {a} - {b} (n={len(sub)}) | | | {rho:+.2f} (p={p:.3f}) | |")
            corr[f"{a}-{b}"] = {"familiarity": {"rho": rho, "p": p, "n": len(sub)}}

    L += ["", "## Harness diagnostics", ""]
    for a in ("PLACEBO", "KNOW", "KNOW_SURE"):
        rs = [r for r in recs if r["arm"] == a]
        if rs:
            hit = sum(r["rule_id"] in r.get("retrieved", []) for r in rs) / len(rs)
            kt = sum("know" in r.get("tools_used", []) for r in rs) / len(rs)
            L.append(f"- {a}: retrieval contained the family's rule in {100 * hit:.0f}% of attempts; "
                     f"`know` tool used in {100 * kt:.0f}%.")
    for a in ("SURE", "KNOW_SURE"):
        rs = [r for r in recs if r["arm"] == a and r.get("sure")]
        if rs:
            rev = [r for r in rs if r.get("revised")]
            fixed = sum((not r["attempt1_strict_pass"]) and r["strict_pass"] for r in rs)
            broke = sum(r["attempt1_strict_pass"] and not r["strict_pass"] for r in rs)
            conf = sum(r["sure"]["conflict"] for r in rs)
            L.append(f"- {a}: revised {len(rev)}/{len(rs)} (conflict {conf}); revision fixed {fixed}, broke {broke}; "
                     f"first-draft pass {sum(r['attempt1_strict_pass'] for r in rs)}/{len(rs)} -> final "
                     f"{sum(r['strict_pass'] for r in rs)}/{len(rs)}.")
    b0 = [r for r in recs if r["arm"] == "B0" and r.get("probe", {}).get("confidence") is not None]
    if b0:
        mc = sum(r["probe"]["confidence"] for r in b0) / len(b0)
        L.append(f"- B0 stated confidence (post-hoc probe) mean {mc:.2f} vs actual pass "
                 f"{sum(r['strict_pass'] for r in b0) / len(b0):.2f} (n={len(b0)}).")
    tools = [r for r in recs]
    if tools:
        L.append(f"- Attempts using at least one tool: {sum(bool(r.get('tool_calls')) for r in tools)}/{len(tools)}; "
                 f"tampering: {sum(r['tamper'] for r in tools)}.")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "REPORT_TABLES.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
        json.dump({"rows": rows, "totals": tot, "correlations": corr}, f, indent=2)
    print("\n".join(L))


if __name__ == "__main__":
    main()
