"""Paper-style analysis ("Instruction Gains Track the Knowledge Gap") for a local-model replication.

Reads the per-attempt records written by run_dimensions.py (arms B0, PLACEBO, RULE, FULL), ranks the
14 families by baseline (familiarity), and correlates the handbook gain with that ranking. The Claude
Sonnet and Gemini 2.5 Flash cells are copied from Tables 1 and 2 of the paper for comparison.

Usage: python3 runner/analyze_paper_replication.py <results subdirectory> [--label NAME]
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import binomtest, spearmanr  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))
from run_dimensions import FAMILY_TASKS, FAMILY_TO_RULE  # noqa: E402

ARMS = ["B0", "PLACEBO", "RULE", "FULL"]

# (baseline, placebo, rule only, full handbook) as (k, n), from the paper's Tables 1 and 2.
PAPER = {
    "Claude Sonnet": {
        "idempotency_keys": [(0, 16), (0, 16), (16, 16), (16, 16)],
        "state_transitions": [(0, 32), (0, 32), (32, 32), (32, 32)],
        "csv_roundtrip": [(4, 16), (4, 16), (16, 16), (16, 16)],
        "wire_envelope": [(16, 40), (17, 40), (40, 40), (40, 40)],
        "permission_prefix": [(8, 16), (8, 16), (8, 16), (8, 16)],
        "money_rounding": [(8, 12), (8, 12), (12, 12), (8, 12)],
        "event_ordering": [(11, 16), (7, 16), (16, 16), (16, 16)],
        "calendar_recurrence": [(6, 8), (7, 8), (8, 8), (8, 8)],
        "metric_percentiles": [(12, 16), (12, 16), (16, 16), (15, 16)],
        "cache_ttl": [(16, 16), (16, 16), (16, 16), (16, 16)],
        "config_lists": [(16, 16), (16, 16), (16, 16), (16, 16)],
        "config_merge": [(8, 8), (4, 8), (4, 8), (8, 8)],
        "service_errors": [(16, 16), (16, 16), (9, 16), (15, 16)],
        "timestamp_iso": [(16, 16), (16, 16), (16, 16), (16, 16)],
    },
    "Gemini 2.5 Flash": {
        "state_transitions": [(0, 16), (0, 16), (16, 16), (13, 16)],
        "idempotency_keys": [(0, 16), (0, 16), (16, 16), (13, 16)],
        "service_errors": [(0, 16), (0, 16), (16, 16), (16, 16)],
        "config_merge": [(1, 8), (5, 8), (1, 8), (4, 8)],
        "event_ordering": [(4, 16), (4, 16), (16, 16), (16, 16)],
        "wire_envelope": [(4, 16), (0, 16), (14, 16), (16, 16)],
        "csv_roundtrip": [(6, 16), (4, 16), (15, 16), (13, 16)],
        "permission_prefix": [(7, 16), (4, 16), (9, 16), (13, 16)],
        "metric_percentiles": [(9, 16), (7, 16), (16, 16), (16, 16)],
        "money_rounding": [(11, 18), (8, 18), (12, 18), (12, 18)],
        "config_lists": [(10, 16), (6, 16), (16, 16), (14, 16)],
        "timestamp_iso": [(15, 16), (12, 16), (16, 16), (14, 16)],
        "cache_ttl": [(16, 16), (16, 16), (15, 16), (16, 16)],
        "calendar_recurrence": [(16, 16), (15, 16), (16, 16), (16, 16)],
    },
}


def pct(c):
    return 100.0 * c[0] / c[1] if c[1] else float("nan")


def rho(x, y):
    return float(spearmanr(x, y).correlation)


def load(out_dir):
    raw = os.path.join(out_dir, "raw")
    recs = []
    for fn in sorted(os.listdir(raw)):
        if fn.endswith(".json"):
            with open(os.path.join(raw, fn), encoding="utf-8") as f:
                r = json.load(f)
            if r.get("status") == "COMPLETED" and r["arm"] in ARMS:
                recs.append(r)
    return recs


def cells(recs, key="strict_pass"):
    out = {}
    for fam in FAMILY_TASKS:
        out[fam] = []
        for arm in ARMS:
            rs = [r for r in recs if r["family"] == fam and r["arm"] == arm]
            out[fam].append((sum(1 for r in rs if r.get(key)), len(rs)))
    return out


def gains(table, arm_idx):
    return {f: pct(c[arm_idx]) - pct(c[0]) for f, c in table.items() if c[0][1] and c[arm_idx][1]}


def kn(c):
    return f"{c[0]}/{c[1]}" if c[1] else "–"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()
    out_dir = os.path.join(REPO_ROOT, "results", args.out)
    label = args.label or args.out
    recs = load(out_dir)
    tab = cells(recs)
    func = cells(recs, "func_pass")
    tamper = cells(recs, "tamper")

    order = sorted(tab, key=lambda f: (pct(tab[f][0]), f))
    lines = ["| Pos | Family | Rule | Baseline | Placebo | Rule only | Full handbook | Rule gain | Full gain | Headroom |",
             "|:-:|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|"]
    g_rule, g_full = gains(tab, 2), gains(tab, 3)
    for i, f in enumerate(order, 1):
        c = tab[f]
        gr = f"{g_rule[f]:+.0f}" if f in g_rule else "–"
        gf = f"{g_full[f]:+.0f}" if f in g_full else "–"
        lines.append(f"| {i} | `{f}` | {FAMILY_TO_RULE[f]} | {kn(c[0])} | {kn(c[1])} | {kn(c[2])} | {kn(c[3])} "
                     f"| {gr} | {gf} | {100 - pct(c[0]):.0f} |")
    tot = [(sum(tab[f][a][0] for f in tab), sum(tab[f][a][1] for f in tab)) for a in range(4)]
    lines.append(f"| | **All** | | {kn(tot[0])} | {kn(tot[1])} | {kn(tot[2])} | {kn(tot[3])} "
                 f"| {pct(tot[2]) - pct(tot[0]):+.0f} | {pct(tot[3]) - pct(tot[0]):+.0f} | |")
    table_md = "\n".join(lines)

    base = {f: pct(tab[f][0]) for f in tab if tab[f][0][1]}
    summary = {"label": label, "n_attempts": len(recs), "cells": {f: tab[f] for f in order},
               "func_pass_cells": func, "tamper_cells": tamper,
               "ranking": [{"position": i, "family": f, "baseline_pct": base.get(f)} for i, f in enumerate(order, 1)],
               "spearman": {}, "baseline_vs_other_models": {}}
    for name, g in (("full_gain_vs_baseline", g_full), ("rule_gain_vs_baseline", g_rule)):
        fs = [f for f in g if f in base]
        if len(fs) >= 3:
            summary["spearman"][name] = rho([base[f] for f in fs], [g[f] for f in fs])
    g_plac = gains(tab, 1)
    if g_plac:
        below = sum(1 for v in g_plac.values() if v < 0)
        above = sum(1 for v in g_plac.values() if v > 0)
        summary["placebo_sign"] = {"below": below, "above": above, "level": len(g_plac) - below - above,
                                   "sign_test_p": binomtest(below, below + above).pvalue if below + above else None}
    for model, data in PAPER.items():
        fs = [f for f in base if f in data]
        summary["baseline_vs_other_models"][model] = rho([base[f] for f in fs], [pct(data[f][0]) for f in fs])
        pg = {f: pct(data[f][3]) - pct(data[f][0]) for f in data}
        pb = {f: pct(data[f][0]) for f in data}
        summary["spearman"][f"paper_{model}_full_gain_vs_baseline"] = rho([pb[f] for f in data], [pg[f] for f in data])
    # Does the gain track the knowledge gap measured on *this* model or on another model?
    for model, data in PAPER.items():
        fs = [f for f in g_full if f in data]
        if len(fs) >= 3:
            summary["spearman"][f"full_gain_vs_{model}_baseline"] = rho([pct(data[f][0]) for f in fs], [g_full[f] for f in fs])

    with open(os.path.join(out_dir, "paper_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(out_dir, "PAPER_TABLE.md"), "w", encoding="utf-8") as f:
        f.write(table_md + "\n")

    if g_full:
        fig, ax = plt.subplots(figsize=(6.4, 5))
        ax.plot([0, 100], [100, 0], "--", color="grey", lw=1, label="gain = headroom")
        ax.axhline(0, color="black", lw=0.5)
        for model, data, mk, col in (("Claude Sonnet", PAPER["Claude Sonnet"], "o", "#9aa"),
                                     ("Gemini 2.5 Flash", PAPER["Gemini 2.5 Flash"], "D", "#bbb")):
            ax.scatter([pct(data[f][0]) for f in data], [pct(data[f][3]) - pct(data[f][0]) for f in data],
                       marker=mk, facecolors="none", edgecolors=col, label=f"{model} (paper)")
        fs = list(g_full)
        ax.scatter([base[f] for f in fs], [g_full[f] for f in fs], color="#c33", s=40, zorder=3, label=label)
        for f in fs:
            ax.annotate(f, (base[f], g_full[f]), fontsize=6, xytext=(3, 3), textcoords="offset points")
        ax.set_xlabel("Baseline strict-pass rate (%)")
        ax.set_ylabel("Full-handbook gain (points)")
        ax.set_xlim(-5, 105)
        ax.set_ylim(-60, 105)
        ax.legend(fontsize=7, loc="upper right")
        ax.set_title("Full-handbook gain vs baseline")
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "gain_vs_baseline.png"), dpi=150)

    print(table_md)
    print(json.dumps({k: summary[k] for k in ("spearman", "baseline_vs_other_models", "placebo_sign") if k in summary}, indent=2))


if __name__ == "__main__":
    main()
