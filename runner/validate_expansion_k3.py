"""Dynamic validation script for K3 expansion tasks (2085-2106)."""
import os, sys, re, shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "benchmarks")))

import grader
import expansion_tasks_k3

DESIGN_WORDS = [
    "taught", "stated", "distractor", "transfer",
    "visible_sensitive", "_visible", "_hidden"
]

def run_validation():
    tasks = expansion_tasks_k3.EXPANSION_TASKS
    print(f"Validating {len(tasks)} expansion tasks...")
    
    for t in tasks:
        tid = t["id"]
        t_name = t["name"]
        
        # 1. Non-test lines check
        non_test_files = [p for p in t["repo"] if not p.startswith("tests/")]
        total_lines = sum(len(t["repo"][p].splitlines()) for p in non_test_files)
        if not (40 <= total_lines <= 120):
            print(f"WARNING: TID {tid} has {total_lines} non-test lines (target 40-120)")
            
        # 2. Hint comments check
        for p in non_test_files:
            content = t["repo"][p]
            if re.search(r"#\s*(BUG|FIX|TODO|HACK)", content, re.IGNORECASE):
                raise ValueError(f"TID {tid} has hint comment in {p}")
                
        # 3. Design words check in tests and tracebacks
        test_files = [p for p in t["repo"] if p.startswith("tests/")] + list(t["hidden_tests"].keys())
        for p in test_files:
            content = t["repo"].get(p) or t["hidden_tests"].get(p, "")
            for dw in DESIGN_WORDS:
                if dw in content.lower():
                    raise ValueError(f"TID {tid} has design word '{dw}' in {p}")
                    
        for dw in DESIGN_WORDS:
            if dw in t["failing_traceback_excerpt"].lower():
                raise ValueError(f"TID {tid} has design word '{dw}' in traceback excerpt")
                
        # 4. Dynamic test execution: unpatched fails
        unpatched_res = grader.evaluate_patch(t["repo"], "", t["key"])
        if unpatched_res["strict_pass"]:
            raise ValueError(f"TID {tid} unpatched unexpectedly PASSED!")
            
        # 5. Gold passes
        gold_res = grader.evaluate_patch(t["repo"], t["gold_patch"], t["key"])
        if not gold_res["strict_pass"]:
            raise ValueError(f"TID {tid} gold patch FAILED! Violations: {gold_res['violations']}, Failing: {gold_res['failing_variants']}")
            
        # 6. Mutant 1 fails
        m1_res = grader.evaluate_patch(t["repo"], t["mutant_1_patch"], t["key"])
        if m1_res["strict_pass"]:
            raise ValueError(f"TID {tid} mutant 1 unexpectedly PASSED!")
            
        # 7. Mutant 2 fails
        m2_res = grader.evaluate_patch(t["repo"], t["mutant_2_patch"], t["key"])
        if m2_res["strict_pass"]:
            raise ValueError(f"TID {tid} mutant 2 unexpectedly PASSED!")
            
        print(f"  [PASS] TID {tid} ({t_name}) | lines={total_lines} | unpatched=FAIL gold=PASS m1=FAIL m2=FAIL")
        
    print("\nALL 22 EXPANSION TASKS VALIDATED 100% SUCCESSFULLY!")

if __name__ == "__main__":
    run_validation()
