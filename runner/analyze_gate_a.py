import json
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))
import suite_e4

rows_path = os.path.join(repo_root, "results", "gate_a", "rows.json")
rows = json.load(open(rows_path, "r", encoding="utf-8"))

print(f"Total rows loaded: {len(rows)}")

c0000 = [r for r in rows if r["cell"] == "C0000"]
c1111 = [r for r in rows if r["cell"] == "C1111"]

s0 = sum(r["final_strict"] for r in c0000)
s1 = sum(r["final_strict"] for r in c1111)

p0 = s0 / len(c0000) if c0000 else 0
p1 = s1 / len(c1111) if c1111 else 0

print(f"C0000 overall: {s0}/{len(c0000)} = {p0:.1%}")
print(f"C1111 overall: {s1}/{len(c1111)} = {p1:.1%}")
print(f"Overall Delta: {p1 - p0:+.1%}")

task_names = {t["id"]: t["name"] for t in suite_e4.T}
tickets = sorted(list(set(r["ticket"] for r in rows)))

print("\n" + "="*80)
print(f"{'ID':<6} {'Task Name':<35} {'C0000':<14} {'C1111':<14} {'Delta':<8}")
print("="*80)

sep_count = 0
for t in tickets:
    t_c0 = [r for r in c0000 if r["ticket"] == t]
    t_c1 = [r for r in c1111 if r["ticket"] == t]
    t_s0 = sum(r["final_strict"] for r in t_c0)
    t_s1 = sum(r["final_strict"] for r in t_c1)
    p_c0 = t_s0 / len(t_c0) if t_c0 else 0
    p_c1 = t_s1 / len(t_c1) if t_c1 else 0
    d = p_c1 - p_c0
    if d >= 0.20:
        sep_count += 1
    name = task_names.get(t, f"Task {t}")[:34]
    print(f"{t:<6} {name:<35} {t_s0}/{len(t_c0)} ({p_c0:.0%})     {t_s1}/{len(t_c1)} ({p_c1:.0%})     {d:+.0%}")

print("="*80)
print(f"Tasks with Delta >= +20%: {sep_count}/{len(tickets)}")

# Token usage summary
tok_in_0 = sum(r["tokens_in"] for r in c0000) / len(c0000)
tok_out_0 = sum(r["tokens_out"] for r in c0000) / len(c0000)
tok_in_1 = sum(r["tokens_in"] for r in c1111) / len(c1111)
tok_out_1 = sum(r["tokens_out"] for r in c1111) / len(c1111)

print(f"\nAverage Tokens per attempt:")
print(f"C0000: {tok_in_0:.0f} in, {tok_out_0:.0f} out (Total: {tok_in_0 + tok_out_0:.0f})")
print(f"C1111: {tok_in_1:.0f} in, {tok_out_1:.0f} out (Total: {tok_in_1 + tok_out_1:.0f})")
print(f"Incremental cost of full scaffolding: +{tok_in_1 - tok_in_0:.0f} in, +{tok_out_1 - tok_out_0:.0f} out")
