#!/usr/bin/env python3
"""Preflight verification of hidden tests: reference solutions must pass, mutants must fail."""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))

import suite_e5
import grader

TASKS_PER_FAMILY = {
    "cache_ttl": [2025, 2026, 2027, 2028],
    "calendar_recurrence": [2010, 2012],
    "config_lists": [2054, 2055, 2057, 2059],
    "config_merge": [2006],
    "csv_roundtrip": [2014, 2015, 2100, 2101],
    "event_ordering": [2022, 2024],
    "idempotency_keys": [2062, 2063, 2065, 2067],
    "metric_percentiles": [2070, 2071, 2073, 2075],
    "money_rounding": [2002, 2003, 2102],
    "permission_prefix": [2018, 2020],
    "service_errors": [2030, 2031, 2033, 2035],
    "state_transitions": [2077, 2078, 2079, 2080],
    "timestamp_iso": [2046, 2047, 2049, 2051],
    "wire_envelope": [2037, 2038, 2039, 2041],
}


def verify_all():
    tasks_by_id = {t["id"]: t for t in suite_e5.T}
    all_passed = True
    checked = 0
    ref_passes = 0
    mutants_checked = 0
    mutants_rejected = 0

    print("Verifying hidden tests and mutant rejection across all 46 protocol tasks...")
    for fam, tids in sorted(TASKS_PER_FAMILY.items()):
        for tid in tids:
            t = tasks_by_id[tid]
            checked += 1

            # 1. Reference solution verification
            ref_blocks = "".join(f"=== FILE: {p} ===\n{c}\n=== END ===\n" for p, c in t["ref"].items())
            res_ref = grader.evaluate_patch(t["repo"], ref_blocks, t["key"])
            if res_ref["strict_pass"]:
                ref_passes += 1
            else:
                print(f"  [FAIL] Task {tid} ({fam}) reference solution FAILED strict_pass! Output:\n{res_ref.get('visible_output')}")
                all_passed = False

            # 2. Mutant rejection verification
            for m_key in ["mutant1", "mutant2"]:
                if m_key in t and t[m_key]:
                    mutants_checked += 1
                    m_blocks = "".join(f"=== FILE: {p} ===\n{c}\n=== END ===\n" for p, c in t[m_key].items())
                    res_m = grader.evaluate_patch(t["repo"], m_blocks, t["key"])
                    if not res_m["strict_pass"]:
                        mutants_rejected += 1
                    else:
                        print(f"  [FAIL] Task {tid} ({fam}) {m_key} PASSED strict_pass (should fail)!")
                        all_passed = False

    print(f"\nVerification Summary:", flush=True)
    print(f"  Tasks Checked: {checked}/46", flush=True)
    print(f"  Reference Passes: {ref_passes}/{checked}", flush=True)
    print(f"  Mutants Rejected: {mutants_rejected}/{mutants_checked}", flush=True)
    print(f"  Status: {'PASSED' if all_passed else 'FAILED'}", flush=True)
    return all_passed


if __name__ == "__main__":
    ok = verify_all()
    sys.exit(0 if ok else 1)
