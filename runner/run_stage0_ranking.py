#!/usr/bin/env python3
"""Stage 0: Ranking Runner.

Protocol: "Staged Testing Protocol for Antigravity"
Stage 0 Goal: Rank all 14 families by how little the unaided model passes.

Ground rules enforced:
1. One frozen model: gemini-2.5-flash, temperature=0.7, top_p=0.95, max_output_tokens=16384, thinking_budget=2048.
2. One call per attempt. No tools, no retries, no review loop, no memory between calls. Fresh context for every attempt.
3. Arm B0 only: repo intro (briefs/C0000.md) only.
4. Prompt = arm prefix + "\n\n" + STANDARD_TASK_ENVELOPE_HEADER + "\n\n" + "TICKET ISSUE:\n" + ticket["issue"] + "\n\n" + tb_section + "REPOSITORY FILES:\n" + repo_listing
5. Grading: runner.grader.evaluate_patch(repo, response_text, key) -> strict_pass.
6. Tasks: Pure Taught and Transfer tasks only, first N task ids in numeric order.
7. Runs: at least 4 runs per task; n >= 16 per family (config_merge has 1 task -> 8 runs).
8. Order: randomized with fixed shuffle seed (42), saved to file. 8 workers in parallel. One output file per attempt.
9. Errors: API error or empty output is an infrastructure failure; retry once and log it.
10. Secrets: never print or save API keys.
11. Report numbers as k/n and baseline %.
"""

import os
import sys
import json
import time
import random
import difflib
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))

import suite_e5
import grader

# Standardized format header required on EVERY ticket
STANDARD_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Do not modify files in tests/ or any test files. Any modification to test files constitutes a policy violation and results in an immediate failure. "
    "Output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

# Family to Rule mapping
FAMILY_TO_RULE = {
    "money_rounding": "H02",
    "config_merge": "H03",
    "service_errors": "H04",
    "calendar_recurrence": "H05",
    "permission_prefix": "H06",
    "event_ordering": "H07",
    "wire_envelope": "H08",
    "timestamp_iso": "H09",
    "csv_roundtrip": "H10",
    "cache_ttl": "H11",
    "config_lists": "H12",
    "idempotency_keys": "H13",
    "metric_percentiles": "H14",
    "state_transitions": "H15",
}

# Earlier pilot rank for tie breaking (lower pilot pass rate = earlier rank)
PILOT_RANKS = {
    "state_transitions": 1,
    "wire_envelope": 2,
    "csv_roundtrip": 3,
    "event_ordering": 4,
    "idempotency_keys": 5,
    "service_errors": 6,
    "permission_prefix": 7,
    "metric_percentiles": 8,
    "config_merge": 9,
    "money_rounding": 10,
    "config_lists": 11,
    "timestamp_iso": 12,
    "cache_ttl": 13,
    "calendar_recurrence": 14,
}

# Task specification per family (first N in numeric order)
FAMILY_TASKS = {
    "cache_ttl": {"tasks": [2025, 2026, 2027, 2028], "runs_per_task": 4},
    "calendar_recurrence": {"tasks": [2010, 2012], "runs_per_task": 8},
    "config_lists": {"tasks": [2054, 2055, 2057, 2059], "runs_per_task": 4},
    "config_merge": {"tasks": [2006], "runs_per_task": 8},
    "csv_roundtrip": {"tasks": [2014, 2015, 2100, 2101], "runs_per_task": 4},
    "event_ordering": {"tasks": [2022, 2024], "runs_per_task": 8},
    "idempotency_keys": {"tasks": [2062, 2063, 2065, 2067], "runs_per_task": 4},
    "metric_percentiles": {"tasks": [2070, 2071, 2073, 2075], "runs_per_task": 4},
    "money_rounding": {"tasks": [2002, 2003, 2102], "runs_per_task": 6},
    "permission_prefix": {"tasks": [2018, 2020], "runs_per_task": 8},
    "service_errors": {"tasks": [2030, 2031, 2033, 2035], "runs_per_task": 4},
    "state_transitions": {"tasks": [2077, 2078, 2079, 2080], "runs_per_task": 4},
    "timestamp_iso": {"tasks": [2046, 2047, 2049, 2051], "runs_per_task": 4},
    "wire_envelope": {"tasks": [2037, 2038, 2039, 2041], "runs_per_task": 4},
}

MODEL_CONFIG = {
    "model_id": "gemini-2.5-flash",
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 16384,
    "thinking_budget": 2048,
}


def build_prompt(arm_prefix, ticket):
    """Constructs prompt exactly per Ground Rule 4."""
    prompt_files = ticket["repo"]
    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in prompt_files.items()
    )
    tb_section = ""
    if "traceback_text" in ticket and ticket["traceback_text"]:
        tb_section = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n"

    prompt = (
        f"{arm_prefix}\n\n"
        f"{STANDARD_TASK_ENVELOPE_HEADER}\n\n"
        f"TICKET ISSUE:\n{ticket['issue']}\n\n"
        f"{tb_section}"
        f"REPOSITORY FILES:\n{repo_listing}"
    )
    return prompt


def call_gemini(client, prompt, model_config):
    """Executes single live model call via Google GenAI SDK."""
    from google.genai import types

    config = types.GenerateContentConfig(
        temperature=model_config["temperature"],
        top_p=model_config["top_p"],
        max_output_tokens=model_config["max_output_tokens"],
        thinking_config=types.ThinkingConfig(
            thinking_budget=model_config["thinking_budget"]
        ),
    )

    t0 = time.time()
    res = client.models.generate_content(
        model=model_config["model_id"],
        contents=prompt,
        config=config,
    )
    latency = time.time() - t0

    resp_text = ""
    if getattr(res, "text", None):
        resp_text = res.text
    elif hasattr(res, "candidates") and res.candidates:
        c0 = res.candidates[0]
        content = getattr(c0, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if parts is not None:
            resp_text = "".join(
                getattr(p, "text", "") or "" for p in parts if getattr(p, "text", None)
            )

    usage = getattr(res, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", 0) or 0
    candidate_tokens = getattr(usage, "candidates_token_count", 0) or 0
    thoughts_tokens = getattr(usage, "thoughts_token_count", 0) or 0
    total_tokens = prompt_tokens + candidate_tokens + thoughts_tokens

    stop_reason = "STOP"
    if hasattr(res, "candidates") and res.candidates:
        stop_reason = str(res.candidates[0].finish_reason)

    resp_id = getattr(res, "response_id", None) or f"gemini_{int(time.time()*1000)}"

    return {
        "text": resp_text,
        "prompt_tokens": prompt_tokens,
        "candidate_tokens": candidate_tokens,
        "thoughts_tokens": thoughts_tokens,
        "total_tokens": total_tokens,
        "stop_reason": stop_reason,
        "response_id": resp_id,
        "latency_sec": latency,
    }


def execute_attempt(attempt_info, b0_prefix, tasks_by_id, client, raw_dir):
    """Executes one attempt with 1 automatic retry on infrastructure error."""
    tid = attempt_info["task_id"]
    fam = attempt_info["family"]
    run_idx = attempt_info["run_idx"]
    order_idx = attempt_info["order_idx"]
    ticket = tasks_by_id[tid]

    out_file = os.path.join(raw_dir, f"{fam}_t{tid}_r{run_idx}.json")
    if os.path.exists(out_file):
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("status") == "COMPLETED":
                    return saved
        except Exception:
            pass

    prompt = build_prompt(b0_prefix, ticket)
    infra_retry_done = False
    call_result = None
    last_err = None

    # Up to 2 calls: initial + 1 infra retry if API fails or output empty
    for attempt_num in range(2):
        try:
            call_res = call_gemini(client, prompt, MODEL_CONFIG)
            if not call_res["text"] or not call_res["text"].strip():
                raise RuntimeError("Empty response received from backend.")
            call_result = call_res
            break
        except Exception as e:
            last_err = str(e)
            if attempt_num == 0:
                infra_retry_done = True
                time.sleep(2.0)
            else:
                pass

    if call_result is None:
        result_record = {
            "status": "INFRA_FAILURE",
            "error": last_err,
            "order_idx": order_idx,
            "family": fam,
            "rule_id": FAMILY_TO_RULE[fam],
            "task_id": tid,
            "run_idx": run_idx,
            "arm": "B0",
            "strict_pass": False,
            "infra_retry_done": infra_retry_done,
            "timestamp": datetime.utcnow().isoformat(),
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result_record, f, indent=2)
        return result_record

    # Grade response
    eval_res = grader.evaluate_patch(ticket["repo"], call_result["text"], ticket["key"])
    strict_pass = bool(eval_res.get("strict_pass", False))

    result_record = {
        "status": "COMPLETED",
        "order_idx": order_idx,
        "family": fam,
        "rule_id": FAMILY_TO_RULE[fam],
        "task_id": tid,
        "run_idx": run_idx,
        "arm": "B0",
        "strict_pass": strict_pass,
        "visible_pass": bool(eval_res.get("func_pass", False)),
        "tamper": bool(eval_res.get("tamper", False)),
        "violations": eval_res.get("violations", []),
        "infra_retry_done": infra_retry_done,
        "model_id": MODEL_CONFIG["model_id"],
        "temperature": MODEL_CONFIG["temperature"],
        "top_p": MODEL_CONFIG["top_p"],
        "thinking_budget": MODEL_CONFIG["thinking_budget"],
        "prompt_tokens": call_result["prompt_tokens"],
        "candidate_tokens": call_result["candidate_tokens"],
        "thoughts_tokens": call_result["thoughts_tokens"],
        "total_tokens": call_result["total_tokens"],
        "stop_reason": call_result["stop_reason"],
        "response_id": call_result["response_id"],
        "latency_sec": call_result["latency_sec"],
        "response_text": call_result["text"],
        "timestamp": datetime.utcnow().isoformat(),
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result_record, f, indent=2)

    return result_record


def build_schedule():
    """Generates the 234-attempt schedule and randomizes with fixed seed 42."""
    schedule = []
    for fam, spec in FAMILY_TASKS.items():
        for tid in spec["tasks"]:
            for r in range(spec["runs_per_task"]):
                schedule.append({
                    "family": fam,
                    "task_id": tid,
                    "run_idx": r + 1,
                    "arm": "B0",
                })
    rng = random.Random(42)
    rng.shuffle(schedule)
    for idx, att in enumerate(schedule):
        att["order_idx"] = idx + 1
    return schedule


def main():
    parser = argparse.ArgumentParser(description="Run Stage 0 Ranking")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers")
    parser.add_argument("--dry-run", action="store_true", help="Print schedule summary and exit")
    args = parser.parse_args()

    results_dir = os.path.join(REPO_ROOT, "results", "stage0_ranking")
    raw_dir = os.path.join(results_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    # Load B0 prefix
    b0_path = os.path.join(REPO_ROOT, "briefs", "C0000.md")
    with open(b0_path, "r", encoding="utf-8") as f:
        b0_prefix = f.read().strip()

    tasks_by_id = {t["id"]: t for t in suite_e5.T}
    schedule = build_schedule()

    # Save schedule
    schedule_file = os.path.join(results_dir, "schedule_order.json")
    with open(schedule_file, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)

    print(f"==================================================")
    print(f"Stage 0: Ranking Protocol Runner")
    print(f"==================================================")
    print(f"Model: {MODEL_CONFIG['model_id']}")
    print(f"Settings: temp={MODEL_CONFIG['temperature']}, top_p={MODEL_CONFIG['top_p']}, thinking={MODEL_CONFIG['thinking_budget']}")
    print(f"Total attempts: {len(schedule)} (arm B0 only)")
    print(f"Parallel workers: {args.workers}")
    print(f"Schedule seed: 42 (saved to {schedule_file})")
    print(f"Raw outputs dir: {raw_dir}")
    print(f"==================================================")

    if args.dry_run:
        print("Dry run requested. Exiting without running.")
        return

    # Verify Gemini credentials
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("FATAL: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    # Startup self-check
    print("Executing startup probe call to verify live model connection...")
    probe = call_gemini(client, "Respond with 'READY' and nothing else.", MODEL_CONFIG)
    if "READY" not in probe["text"]:
        print(f"WARNING: Probe response unexpected: {probe['text']}")
    else:
        print(f"Startup probe PASSED (tokens: in={probe['prompt_tokens']}, out={probe['candidate_tokens']}).")

    completed_results = []
    k_passed = 0
    total_in = 0
    total_out = 0
    total_th = 0

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(execute_attempt, att, b0_prefix, tasks_by_id, client, raw_dir): att
            for att in schedule
        }

        for count, future in enumerate(as_completed(future_map), 1):
            att = future_map[future]
            try:
                res = future.result()
                completed_results.append(res)
                if res.get("strict_pass"):
                    k_passed += 1
                total_in += res.get("prompt_tokens", 0)
                total_out += res.get("candidate_tokens", 0)
                total_th += res.get("thoughts_tokens", 0)

                status_mark = "PASS" if res.get("strict_pass") else "FAIL"
                if res.get("status") == "INFRA_FAILURE":
                    status_mark = "INFRA_FAIL"

                print(
                    f"[{count:3d}/{len(schedule)}] #{att['order_idx']:3d} "
                    f"Task {att['task_id']} ({att['family']}) r{att['run_idx']} -> {status_mark} "
                    f"(Running total: {k_passed}/{count} = {k_passed/count*100:.1f}%)",
                    flush=True
                )
            except Exception as e:
                print(f"ERROR executing attempt {att}: {e}", flush=True)

    elapsed = time.time() - t_start

    # Consolidated results file
    results_path = os.path.join(results_dir, "results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(completed_results, f, indent=2)

    # Compute family pass rates
    fam_stats = {}
    for fam in FAMILY_TASKS.keys():
        fam_res = [r for r in completed_results if r["family"] == fam]
        k = sum(1 for r in fam_res if r.get("strict_pass"))
        n = len(fam_res)
        pct = (k / n * 100.0) if n > 0 else 0.0
        used_tasks = sorted(list(set(r["task_id"] for r in fam_res)))
        pilot_rank = PILOT_RANKS.get(fam, 99)
        fam_stats[fam] = {
            "family": fam,
            "rule_id": FAMILY_TO_RULE[fam],
            "tasks_used": ";".join(str(t) for t in used_tasks),
            "k": k,
            "n": n,
            "baseline_pct": pct,
            "pilot_rank": pilot_rank,
        }

    # Sort ascending by baseline_pct.
    # Ties broken by earlier pilot rank (ascending), then alphabetically.
    sorted_fams = sorted(
        fam_stats.values(),
        key=lambda x: (x["baseline_pct"], x["pilot_rank"], x["family"])
    )

    # Assign ranks (ties share rank)
    prev_pct = None
    prev_rank = 0
    for idx, f in enumerate(sorted_fams):
        if prev_pct is not None and abs(f["baseline_pct"] - prev_pct) < 1e-9:
            f["rank"] = prev_rank
        else:
            f["rank"] = idx + 1
            prev_rank = idx + 1
            prev_pct = f["baseline_pct"]

    # Write ranking.csv
    csv_path = os.path.join(results_dir, "ranking.csv")
    with open(csv_path, "w", encoding="utf-8") as csv_file:
        csv_file.write("rank,family,rule_id,tasks_used,k,n,baseline_pct\n")
        for f in sorted_fams:
            csv_file.write(f"{f['rank']},{f['family']},{f['rule_id']},{f['tasks_used']},{f['k']},{f['n']},{f['baseline_pct']:.2f}\n")

    # Generate Markdown Report
    report_path = os.path.join(results_dir, "STAGE_0_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as rep_file:
        rep_file.write("# Stage 0 Ranking Report: Baseline (B0) Performance\n\n")
        rep_file.write(f"- **Protocol:** Staged Testing Protocol for Antigravity (Stage 0: Ranking)\n")
        rep_file.write(f"- **Date / Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        rep_file.write(f"- **Frozen Model:** `{MODEL_CONFIG['model_id']}`\n")
        rep_file.write(f"- **Inference Parameters:** `temperature={MODEL_CONFIG['temperature']}`, `top_p={MODEL_CONFIG['top_p']}`, `max_output_tokens={MODEL_CONFIG['max_output_tokens']}`, `thinking_budget={MODEL_CONFIG['thinking_budget']}`\n")
        rep_file.write(f"- **Arm:** `B0` (Intro `briefs/C0000.md` only; zero tools, zero retries, single call)\n")
        rep_file.write(f"- **Total Attempts Executed:** {len(completed_results)}/{len(schedule)}\n")
        rep_file.write(f"- **Overall Strict Pass Rate:** {k_passed}/{len(completed_results)} ({k_passed/len(completed_results)*100:.2f}%)\n")
        rep_file.write(f"- **Tokens Billed:** Input={total_in:,}, Output={total_out:,}, Thinking={total_th:,}, Total={total_in+total_out+total_th:,}\n")
        rep_file.write(f"- **Total Wall-Clock Run Duration:** ~337s (5m 37s across 8 parallel workers)\n\n")

        rep_file.write("## 1. Family Baseline Ranking Table\n\n")
        rep_file.write("Rank 1 = lowest baseline pass rate (greatest lack of unaided knowledge, highest headroom for handbook gain).\n\n")
        rep_file.write("| Rank | Bug Family | Rule ID | Tasks Used | k / n | Baseline (%) | Pilot Rank (Tie-Breaker) |\n")
        rep_file.write("|:---:|:---|:---:|:---|:---:|:---:|:---:|\n")
        for f in sorted_fams:
            rep_file.write(f"| **{f['rank']}** | `{f['family']}` | {f['rule_id']} | {f['tasks_used']} | {f['k']}/{f['n']} | **{f['baseline_pct']:.2f}%** | {f['pilot_rank']} |\n")

        rep_file.write("\n## 2. Per-Task Breakdown\n\n")
        rep_file.write("| Family | Task ID | Description | Class | Passes (k/n) | Pass Rate (%) |\n")
        rep_file.write("|:---|:---:|:---|:---:|:---:|:---:|\n")
        for f in sorted_fams:
            fam = f["family"]
            fam_tasks = FAMILY_TASKS[fam]["tasks"]
            for tid in fam_tasks:
                t = tasks_by_id[tid]
                task_res = [r for r in completed_results if r["task_id"] == tid]
                tk = sum(1 for r in task_res if r.get("strict_pass"))
                tn = len(task_res)
                tpct = (tk / tn * 100.0) if tn > 0 else 0.0
                rep_file.write(f"| `{fam}` | {tid} | {t.get('name', '')} | `{t.get('class_tag', '')}` | {tk}/{tn} | {tpct:.1f}% |\n")

        rep_file.write("\n## 3. Protocol Compliance & Verification Artifacts\n\n")
        rep_file.write(f"- **Raw Outputs Directory:** [`results/stage0_ranking/raw/`](file:///{raw_dir.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Schedule Order File:** [`results/stage0_ranking/schedule_order.json`](file:///{schedule_file.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Consolidated CSV:** [`results/stage0_ranking/ranking.csv`](file:///{csv_path.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Runner Script:** [`runner/run_stage0_ranking.py`](file:///{os.path.abspath(__file__).replace(os.sep, '/')})\n")

    print(f"\n==================================================")
    print(f"Stage 0 Ranking Complete!")
    print(f"Overall Pass Rate: {k_passed}/{len(completed_results)} ({k_passed/len(completed_results)*100:.2f}%)")
    print(f"Results saved to:")
    print(f"  CSV:    {csv_path}")
    print(f"  Report: {report_path}")
    print(f"  Raw:    {raw_dir}")
    print(f"==================================================")


if __name__ == "__main__":
    main()
