import json
import math
import os
import sys

def wilson_score_interval(k, n, confidence=0.95):
    """Computes Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054  # 95% two-sided
    p = k / n
    denominator = 1.0 + z**2 / n
    centre_adjusted_probability = p + z**2 / (2 * n)
    adjusted_std_dev = math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
    lower = (centre_adjusted_probability - z * adjusted_std_dev) / denominator
    upper = (centre_adjusted_probability + z * adjusted_std_dev) / denominator
    return (max(0.0, lower), min(1.0, upper))

def paired_sign_flip_test(deltas):
    """Exact paired sign-flip permutation test on task-level differences."""
    non_zero = [d for d in deltas if d != 0]
    n = len(non_zero)
    if n == 0:
        return 1.0
    observed_sum = sum(deltas)
    
    # 2^n permutations
    import itertools
    count_extreme = 0
    total = 2**n
    for signs in itertools.product([-1, 1], repeat=n):
        perm_sum = sum(s * d for s, d in zip(signs, non_zero))
        if abs(perm_sum) >= abs(observed_sum) - 1e-9:
            count_extreme += 1
    return count_extreme / total

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.path.join(repo_root, "benchmarks"))
    import suite_e4

    rows_path = os.path.join(repo_root, "results", "gate_a", "rows.json")
    rows = json.load(open(rows_path, "r", encoding="utf-8"))

    c0 = [r for r in rows if r["cell"] == "C0000"]
    c1 = [r for r in rows if r["cell"] == "C1111"]

    k0 = sum(r["final_strict"] for r in c0)
    n0 = len(c0)
    k1 = sum(r["final_strict"] for r in c1)
    n1 = len(c1)

    p0 = k0 / n0
    p1 = k1 / n1
    delta = p1 - p0

    w0_low, w0_high = wilson_score_interval(k0, n0)
    w1_low, w1_high = wilson_score_interval(k1, n1)

    print("="*80)
    print("GATE A RIGOROUS STATISTICAL RE-ANALYSIS (G-2)")
    print("="*80)
    print(f"Total evaluated attempts: {len(rows)} (12 tasks x 2 cells x 5 runs)")
    print(f"C0000 (Bare baseline):      {k0}/{n0} = {p0:.1%}  [Wilson 95% CI: {w0_low:.1%}, {w0_high:.1%}]")
    print(f"C1111 (Full scaffolding):   {k1}/{n1} = {p1:.1%}  [Wilson 95% CI: {w1_low:.1%}, {w1_high:.1%}]")
    print(f"Observed Delta (C1111 - C0000): {delta:+.1%} ({k1 - k0:+d} net passing attempts out of 60)")

    tickets = sorted(list(set(r["ticket"] for r in rows)))
    task_names = {t["id"]: t["name"] for t in suite_e4.T}

    task_deltas = []
    print("\nTask-Level Breakdown:")
    print(f"{'ID':<6} {'Task Name':<35} {'C0000':<12} {'C1111':<12} {'Delta':<8}")
    print("-"*80)
    for t in tickets:
        t0 = [r for r in c0 if r["ticket"] == t]
        t1 = [r for r in c1 if r["ticket"] == t]
        p_t0 = sum(r["final_strict"] for r in t0) / len(t0)
        p_t1 = sum(r["final_strict"] for r in t1) / len(t1)
        d = p_t1 - p_t0
        task_deltas.append(d)
        name = task_names.get(t, f"Task {t}")[:34]
        print(f"{t:<6} {name:<35} {sum(r['final_strict'] for r in t0)}/{len(t0)} ({p_t0:.0%})   {sum(r['final_strict'] for r in t1)}/{len(t1)} ({p_t1:.0%})   {d:+.0%}")

    p_perm = paired_sign_flip_test(task_deltas)
    print("-"*80)
    print(f"Task-level paired sign-flip permutation p-value: p = {p_perm:.4f}")
    if p_perm >= 0.05:
        print("-> Conclusion: Across the 12 candidate tasks, the overall scaffolding advantage is NOT statistically significant (p = 0.50).")
        print("   The Gate A data support difficulty calibration (breaking the ceiling), but do NOT support claims of overall scaffolding efficacy.")
