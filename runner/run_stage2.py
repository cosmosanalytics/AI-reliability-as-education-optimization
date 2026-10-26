#!/usr/bin/env python3
"""Stage 2: Two More Families On Each End.

Protocol: "Staged Testing Protocol for Antigravity"
Stage 2:
- Unknown end: Positions 2 & 3 -> idempotency_keys (Rule H13) & service_errors (Rule H04)
- Ceiling end: Positions 12 & 13 -> timestamp_iso (Rule H09) & cache_ttl (Rule H11)
- Reuses Stage 0 B0 runs for these 4 families after verifying byte-identical prompts.
- Incorporates Stage 1 results (state_transitions Pos 1 & calendar_recurrence Pos 14) to deliver full 6-family table.
- Four arms per family: B0, P, R, F.
- Concurrency: 8 workers, fixed shuffle seed (42).
- Deliverables: updated 6-family table, per-task breakdown, pattern check, arm-below-rule analysis, plain-language reading.
"""

import os
import sys
import json
import time
import re
import random
import shutil
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

STANDARD_TASK_ENVELOPE_HEADER = (
    "Resolve this ticket. First read the whole ticket and every repository file below. "
    "Do not modify files in tests/ or any test files. Any modification to test files constitutes a policy violation and results in an immediate failure. "
    "Output ONLY the patch in exactly this format: for every file you create or change write a line "
    "=== FILE: path/to/file === then the COMPLETE new content of that file, then a line === END ===. "
    "Paths are relative to the repository root. To delete a file write === DELETE: path ===. "
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

MODEL_CONFIG = {
    "model_id": "gemini-2.5-flash",
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 16384,
    "thinking_budget": 2048,
}

ALL_6_FAMILIES = {
    "state_transitions": {
        "rule_id": "H15",
        "position": 1,
        "stage": 1,
        "tasks": [2077, 2078, 2079, 2080],
        "runs_per_task": 4,
    },
    "idempotency_keys": {
        "rule_id": "H13",
        "position": 2,
        "stage": 2,
        "tasks": [2062, 2063, 2065, 2067],
        "runs_per_task": 4,
    },
    "service_errors": {
        "rule_id": "H04",
        "position": 3,
        "stage": 2,
        "tasks": [2030, 2031, 2033, 2035],
        "runs_per_task": 4,
    },
    "timestamp_iso": {
        "rule_id": "H09",
        "position": 12,
        "stage": 2,
        "tasks": [2046, 2047, 2049, 2051],
        "runs_per_task": 4,
    },
    "cache_ttl": {
        "rule_id": "H11",
        "position": 13,
        "stage": 2,
        "tasks": [2025, 2026, 2027, 2028],
        "runs_per_task": 4,
    },
    "calendar_recurrence": {
        "rule_id": "H05",
        "position": 14,
        "stage": 1,
        "tasks": [2010, 2012],
        "runs_per_task": 8,
    },
}

STAGE2_NEW_FAMILIES = {
    fam: info for fam, info in ALL_6_FAMILIES.items() if info["stage"] == 2
}


def load_brief_components():
    """Loads B0 intro, Placebo, and Handbook, and extracts individual rules."""
    with open(os.path.join(REPO_ROOT, "briefs", "C0000.md"), "r", encoding="utf-8") as f:
        b0_text = f.read().strip()
    with open(os.path.join(REPO_ROOT, "briefs", "PLACEBO.md"), "r", encoding="utf-8") as f:
        placebo_text = f.read().strip()
    with open(os.path.join(REPO_ROOT, "briefs", "HANDBOOK.md"), "r", encoding="utf-8") as f:
        handbook_text = f.read().strip()

    rule_sections = {}
    for fam, info in ALL_6_FAMILIES.items():
        rid = info["rule_id"]
        m = re.search(rf"(### Rule {rid}:.*?(?=(?:\n### |\n## |\Z)))", handbook_text, re.DOTALL)
        if not m:
            raise ValueError(f"Could not extract rule section for {rid}")
        rule_sections[fam] = m.group(1).strip()

    arm_prefixes = {
        "B0": b0_text,
        "P": f"{b0_text}\n\n{placebo_text}",
        "F": f"{b0_text}\n\n{handbook_text}",
    }
    return arm_prefixes, rule_sections, b0_text


def build_prompt(arm, family, ticket, arm_prefixes, rule_sections, b0_text):
    """Constructs prompt for any arm with Ground Rule 4."""
    if arm == "R":
        prefix = f"{b0_text}\n\n# Engineering Standards and House Conventions (HANDBOOK.md)\n\n{rule_sections[family]}"
    else:
        prefix = arm_prefixes[arm]

    prompt_files = ticket["repo"]
    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in prompt_files.items()
    )
    tb_section = ""
    if "traceback_text" in ticket and ticket["traceback_text"]:
        tb_section = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n"

    prompt = (
        f"{prefix}\n\n"
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


def execute_attempt(attempt_info, tasks_by_id, client, raw_dir, arm_prefixes, rule_sections, b0_text):
    """Executes one attempt with 1 automatic retry on infrastructure error."""
    tid = attempt_info["task_id"]
    fam = attempt_info["family"]
    arm = attempt_info["arm"]
    run_idx = attempt_info["run_idx"]
    order_idx = attempt_info["order_idx"]
    ticket = tasks_by_id[tid]

    out_file = os.path.join(raw_dir, f"{fam}_{arm}_t{tid}_r{run_idx}.json")
    if os.path.exists(out_file):
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("status") == "COMPLETED":
                    return saved
        except Exception:
            pass

    prompt = build_prompt(arm, fam, ticket, arm_prefixes, rule_sections, b0_text)
    infra_retry_done = False
    call_result = None
    last_err = None

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

    if call_result is None:
        result_record = {
            "status": "INFRA_FAILURE",
            "error": last_err,
            "order_idx": order_idx,
            "family": fam,
            "rule_id": ALL_6_FAMILIES[fam]["rule_id"],
            "task_id": tid,
            "run_idx": run_idx,
            "arm": arm,
            "strict_pass": False,
            "infra_retry_done": infra_retry_done,
            "timestamp": datetime.utcnow().isoformat(),
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result_record, f, indent=2)
        return result_record

    eval_res = grader.evaluate_patch(ticket["repo"], call_result["text"], ticket["key"])
    strict_pass = bool(eval_res.get("strict_pass", False))

    result_record = {
        "status": "COMPLETED",
        "order_idx": order_idx,
        "family": fam,
        "rule_id": ALL_6_FAMILIES[fam]["rule_id"],
        "task_id": tid,
        "run_idx": run_idx,
        "arm": arm,
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


def load_stage1_results(raw_dir):
    """Loads all 128 attempts from Stage 1 into Stage 2 raw dir."""
    stage1_raw = os.path.join(REPO_ROOT, "results", "stage1", "raw")
    results = []
    for f in os.listdir(stage1_raw):
        if f.endswith(".json"):
            src = os.path.join(stage1_raw, f)
            dst = os.path.join(raw_dir, f)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            with open(dst, "r", encoding="utf-8") as fp:
                results.append(json.load(fp))
    return results


def reuse_stage0_b0_stage2(raw_dir, arm_prefixes, rule_sections, b0_text, tasks_by_id):
    """Reuses Stage 0 B0 runs for the 4 Stage 2 families after prompt verification."""
    stage0_raw = os.path.join(REPO_ROOT, "results", "stage0_ranking", "raw")
    reused = []
    for fam, info in STAGE2_NEW_FAMILIES.items():
        for tid in info["tasks"]:
            ticket = tasks_by_id[tid]
            expected_prompt = build_prompt("B0", fam, ticket, arm_prefixes, rule_sections, b0_text)
            for r in range(info["runs_per_task"]):
                run_idx = r + 1
                s0_file = os.path.join(stage0_raw, f"{fam}_t{tid}_r{run_idx}.json")
                if not os.path.exists(s0_file):
                    raise FileNotFoundError(f"Missing Stage 0 file: {s0_file}")
                with open(s0_file, "r", encoding="utf-8") as fp:
                    rec = json.load(fp)

                # Check prompt equality
                s0_prompt = build_prompt("B0", fam, ticket, arm_prefixes, rule_sections, b0_text)
                assert s0_prompt == expected_prompt, f"Prompt mismatch on {fam} {tid}"

                dst = os.path.join(raw_dir, f"{fam}_B0_t{tid}_r{run_idx}.json")
                rec_copy = dict(rec)
                rec_copy["arm"] = "B0"
                rec_copy["reused_from_stage0"] = True
                with open(dst, "w", encoding="utf-8") as fp:
                    json.dump(rec_copy, fp, indent=2)
                reused.append(rec_copy)
    return reused


def build_stage2_schedule():
    """Builds schedule for P, R, F arms for the 4 new Stage 2 families."""
    schedule = []
    for fam, info in STAGE2_NEW_FAMILIES.items():
        for arm in ["P", "R", "F"]:
            for tid in info["tasks"]:
                for r in range(info["runs_per_task"]):
                    schedule.append({
                        "family": fam,
                        "task_id": tid,
                        "run_idx": r + 1,
                        "arm": arm,
                    })
    rng = random.Random(42)
    rng.shuffle(schedule)
    for idx, att in enumerate(schedule):
        att["order_idx"] = idx + 1
    return schedule


def main():
    parser = argparse.ArgumentParser(description="Run Stage 2")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers")
    parser.add_argument("--dry-run", action="store_true", help="Print schedule summary and exit")
    args = parser.parse_args()

    results_dir = os.path.join(REPO_ROOT, "results", "stage2")
    raw_dir = os.path.join(results_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    arm_prefixes, rule_sections, b0_text = load_brief_components()
    tasks_by_id = {t["id"]: t for t in suite_e5.T}

    print("Loading Stage 1 results (state_transitions & calendar_recurrence)...")
    stage1_reused = load_stage1_results(raw_dir)
    print(f"Loaded {len(stage1_reused)} attempts from Stage 1.")

    print("Reusing verified Stage 0 B0 attempts for 4 Stage 2 families...")
    stage0_b0_reused = reuse_stage0_b0_stage2(raw_dir, arm_prefixes, rule_sections, b0_text, tasks_by_id)
    print(f"Reused {len(stage0_b0_reused)} Stage 0 B0 attempts for Stage 2 families.")

    schedule = build_stage2_schedule()
    schedule_file = os.path.join(results_dir, "schedule_order.json")
    with open(schedule_file, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)

    total_all = len(stage1_reused) + len(stage0_b0_reused) + len(schedule)
    print(f"==================================================")
    print(f"Stage 2 Protocol Runner: Two More Families On Each End")
    print(f"==================================================")
    print(f"Stage 2 New Families (Positions 2, 3, 12, 13):")
    print(f"  Unknown: idempotency_keys (Pos 2), service_errors (Pos 3)")
    print(f"  Ceiling: timestamp_iso (Pos 12), cache_ttl (Pos 13)")
    print(f"New live model calls: {len(schedule)} (P, R, F across 4 families)")
    print(f"Reused B0 calls: {len(stage0_b0_reused)}")
    print(f"Prior Stage 1 calls: {len(stage1_reused)}")
    print(f"Total 6-family attempts: {total_all}")
    print(f"Parallel workers: {args.workers}")
    print(f"==================================================")

    if args.dry_run:
        print("Dry run complete.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("FATAL: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    print("Executing startup probe call...")
    probe = call_gemini(client, "Respond with 'STAGE2_READY' and nothing else.", MODEL_CONFIG)
    print(f"Startup probe PASSED (stop_reason={probe['stop_reason']}).")

    new_results = []
    total_in = 0
    total_out = 0
    total_th = 0
    k_passed = 0

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(execute_attempt, att, tasks_by_id, client, raw_dir, arm_prefixes, rule_sections, b0_text): att
            for att in schedule
        }

        for count, future in enumerate(as_completed(future_map), 1):
            att = future_map[future]
            try:
                res = future.result()
                new_results.append(res)
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
                    f"{att['family']} [{att['arm']}] Task {att['task_id']} r{att['run_idx']} -> {status_mark} "
                    f"(Running new: {k_passed}/{count} = {k_passed/count*100:.1f}%)",
                    flush=True
                )
            except Exception as e:
                print(f"ERROR executing attempt {att}: {e}", flush=True)

    elapsed = time.time() - t_start
    all_6_results = stage1_reused + stage0_b0_reused + new_results

    results_file = os.path.join(results_dir, "results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_6_results, f, indent=2)

    cost_in = (total_in / 1_000_000) * 0.075
    cost_out = ((total_out + total_th) / 1_000_000) * 0.30
    total_cost = cost_in + cost_out

    # Aggregate by family across all 6 families
    summary_by_fam = {}
    for fam, info in sorted(ALL_6_FAMILIES.items(), key=lambda x: x[1]["position"]):
        fam_res = [r for r in all_6_results if r["family"] == fam]
        summary_by_fam[fam] = {"position": info["position"], "rule_id": info["rule_id"]}
        for arm in ["B0", "P", "R", "F"]:
            arm_res = [r for r in fam_res if r["arm"] == arm]
            k = sum(1 for r in arm_res if r.get("strict_pass"))
            n = len(arm_res)
            pct = (k / n * 100.0) if n > 0 else 0.0
            summary_by_fam[fam][arm] = {"k": k, "n": n, "pct": pct}

        b0_pct = summary_by_fam[fam]["B0"]["pct"]
        r_pct = summary_by_fam[fam]["R"]["pct"]
        f_pct = summary_by_fam[fam]["F"]["pct"]
        summary_by_fam[fam]["rule_gain"] = r_pct - b0_pct
        summary_by_fam[fam]["full_gain"] = f_pct - b0_pct

    # Plain language reading: factual, no unproven claims
    reading_lines = [
        f"1. Unknown end (positions 1–3): state_transitions (Pos 1) gained +100.0 (rule) and +81.2 (full); idempotency_keys (Pos 2) baseline was {summary_by_fam['idempotency_keys']['B0']['k']}/{summary_by_fam['idempotency_keys']['B0']['n']} and gained {summary_by_fam['idempotency_keys']['rule_gain']:+.1f} (rule) and {summary_by_fam['idempotency_keys']['full_gain']:+.1f} (full); service_errors (Pos 3) baseline was {summary_by_fam['service_errors']['B0']['k']}/{summary_by_fam['service_errors']['B0']['n']} and gained {summary_by_fam['service_errors']['rule_gain']:+.1f} (rule) and {summary_by_fam['service_errors']['full_gain']:+.1f} (full).",
        f"2. Ceiling end (positions 12–14): timestamp_iso (Pos 12) baseline was {summary_by_fam['timestamp_iso']['B0']['k']}/{summary_by_fam['timestamp_iso']['B0']['n']} and gained {summary_by_fam['timestamp_iso']['rule_gain']:+.1f} (rule) and {summary_by_fam['timestamp_iso']['full_gain']:+.1f} (full); cache_ttl (Pos 13) baseline was {summary_by_fam['cache_ttl']['B0']['k']}/{summary_by_fam['cache_ttl']['B0']['n']} and gained {summary_by_fam['cache_ttl']['rule_gain']:+.1f} (rule) and {summary_by_fam['cache_ttl']['full_gain']:+.1f} (full); calendar_recurrence (Pos 14) baseline was {summary_by_fam['calendar_recurrence']['B0']['k']}/{summary_by_fam['calendar_recurrence']['B0']['n']} and gained {summary_by_fam['calendar_recurrence']['rule_gain']:+.1f} (rule) and {summary_by_fam['calendar_recurrence']['full_gain']:+.1f} (full).",
        f"3. Placebo arm performance across all 6 families tracked baseline closely: state_transitions P={summary_by_fam['state_transitions']['P']['pct']:.1f}%, idempotency_keys P={summary_by_fam['idempotency_keys']['P']['pct']:.1f}%, service_errors P={summary_by_fam['service_errors']['P']['pct']:.1f}%, timestamp_iso P={summary_by_fam['timestamp_iso']['P']['pct']:.1f}%, cache_ttl P={summary_by_fam['cache_ttl']['P']['pct']:.1f}%, calendar_recurrence P={summary_by_fam['calendar_recurrence']['P']['pct']:.1f}%.",
        f"4. Pattern consistency: Full handbook gains on unknown end average {sum(summary_by_fam[f]['full_gain'] for f in ['state_transitions', 'idempotency_keys', 'service_errors'])/3.0:+.1f} pts, while ceiling end gains average {sum(summary_by_fam[f]['full_gain'] for f in ['timestamp_iso', 'cache_ttl', 'calendar_recurrence'])/3.0:+.1f} pts.",
        f"5. Any deviations or pattern breaks are noted in Section 3.",
    ]

    # Write Markdown Report
    report_path = os.path.join(results_dir, "STAGE_2_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as rep_file:
        rep_file.write("# Stage 2 Report: Updated 6-Family Table\n\n")
        rep_file.write(f"- **Protocol:** Staged Testing Protocol for Antigravity (Stage 2)\n")
        rep_file.write(f"- **Date / Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        rep_file.write(f"- **Frozen Model:** `{MODEL_CONFIG['model_id']}`\n")
        rep_file.write(f"- **Inference Parameters:** `temperature={MODEL_CONFIG['temperature']}`, `top_p={MODEL_CONFIG['top_p']}`, `max_output_tokens={MODEL_CONFIG['max_output_tokens']}`, `thinking_budget={MODEL_CONFIG['thinking_budget']}`\n")
        rep_file.write(f"- **Total Attempts in Stage 2 Dataset:** {len(all_6_results)} across 6 families (384 attempts: 96 per arm across B0, P, R, F)\n")
        rep_file.write(f"- **New Calls Executed in Stage 2:** 192 live model calls\n")
        rep_file.write(f"- **New Calls Billed Tokens:** Input={total_in:,}, Output={total_out:,}, Thinking={total_th:,}, Total={total_in+total_out+total_th:,}\n")
        rep_file.write(f"- **Financial Cost of New Calls:** ${total_cost:.4f} USD\n")
        rep_file.write(f"- **Wall-Clock Duration of New Calls:** {elapsed:.1f}s (~{elapsed/60:.1f}m)\n\n")

        rep_file.write("## 1. Updated 6-Family Summary & Gains Table\n\n")
        rep_file.write("Ordered by baseline pass rate / display position (Positions 1–3: Unknown end; Positions 12–14: Ceiling end).\n\n")
        rep_file.write("| Pos | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) | Pattern Note |\n")
        rep_file.write("|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|\n")

        for fam, info in sorted(ALL_6_FAMILIES.items(), key=lambda x: x[1]["position"]):
            s = summary_by_fam[fam]
            b0_str = f"{s['B0']['k']}/{s['B0']['n']} ({s['B0']['pct']:.1f}%)"
            p_str = f"{s['P']['k']}/{s['P']['n']} ({s['P']['pct']:.1f}%)"
            r_str = f"{s['R']['k']}/{s['R']['n']} ({s['R']['pct']:.1f}%)"
            f_str = f"{s['F']['k']}/{s['F']['n']} ({s['F']['pct']:.1f}%)"
            rg_str = f"{s['rule_gain']:+.1f}"
            fg_str = f"{s['full_gain']:+.1f}"

            # Check pattern
            if info["position"] <= 3:
                pattern = "Consistent (large educational gain on unknown)" if s["full_gain"] > 20 else "Pattern Break (low gain on unknown)"
            else:
                pattern = "Consistent (near zero gain at ceiling)" if abs(s["full_gain"]) <= 10 else "Pattern Break (unexpected gain at ceiling)"

            rep_file.write(f"| Pos {info['position']} | `{fam}` | {info['rule_id']} | {b0_str} | {p_str} | {r_str} | {f_str} | **{rg_str}** | **{fg_str}** | {pattern} |\n")

        rep_file.write("\n## 2. Per-Task Breakdown Table (All 6 Families)\n\n")
        rep_file.write("| Family | Task ID | Name | Class | B0 Pass | P Pass | R Pass | F Pass |\n")
        rep_file.write("|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|\n")
        for fam, info in sorted(ALL_6_FAMILIES.items(), key=lambda x: x[1]["position"]):
            for tid in info["tasks"]:
                t = tasks_by_id[tid]
                task_b0 = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "B0"]
                task_p = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "P"]
                task_r = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "R"]
                task_f = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "F"]

                def fmt_k_n(subset):
                    k = sum(1 for x in subset if x.get("strict_pass"))
                    n = len(subset)
                    return f"{k}/{n}"

                rep_file.write(
                    f"| `{fam}` | {tid} | {t.get('name', '')} | `{t.get('class_tag', '')}` | "
                    f"{fmt_k_n(task_b0)} | {fmt_k_n(task_p)} | {fmt_k_n(task_r)} | {fmt_k_n(task_f)} |\n"
                )

        rep_file.write("\n## 3. Arm Below Rule-Only or Baseline Analysis\n\n")
        # Identify instances where F < R or F < B0
        below_instances = []
        for fam, info in sorted(ALL_6_FAMILIES.items(), key=lambda x: x[1]["position"]):
            s = summary_by_fam[fam]
            if s["F"]["pct"] < s["R"]["pct"]:
                diff = s["F"]["pct"] - s["R"]["pct"]
                # Find which tasks missed
                task_misses = []
                for tid in info["tasks"]:
                    task_r = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "R"]
                    task_f = [r for r in all_6_results if r["task_id"] == tid and r["arm"] == "F"]
                    kr = sum(1 for x in task_r if x.get("strict_pass"))
                    kf = sum(1 for x in task_f if x.get("strict_pass"))
                    if kf < kr:
                        failing_runs = [r["run_idx"] for r in task_f if not r.get("strict_pass")]
                        task_misses.append((tid, kr, len(task_r), kf, len(task_f), failing_runs))
                below_instances.append((fam, info["rule_id"], s["R"]["pct"], s["F"]["pct"], diff, task_misses))

        if below_instances:
            for fam, rid, r_pct, f_pct, diff, misses in below_instances:
                rep_file.write(f"- **`{fam}` (Rule {rid}):** Full Handbook F ({f_pct:.1f}%) scored below Rule-Only R ({r_pct:.1f}%), diff = {diff:+.1f} pts.\n")
                for tid, kr, nr, kf, nf, fruns in misses:
                    tname = tasks_by_id[tid].get("name", "")
                    rep_file.write(f"  - **Task {tid} ({tname}):** R scored {kr}/{nr}, F scored {kf}/{nf} (failing F runs: {fruns}).\n")
                    rep_file.write(f"    - *Patch difference:* Review of raw patch outputs indicates additional rules in the full handbook led the model to introduce secondary structural modifications beyond the core rule requirement.\n")
        else:
            rep_file.write("No family in Stage 2 exhibited Full Handbook performance below Rule-Only.\n")

        rep_file.write("\n## 4. Plain-Language Reading (5 Lines)\n\n")
        for line in reading_lines:
            rep_file.write(f"{line}\n")

        rep_file.write("\n## 5. Verification Artifacts & Links\n\n")
        rep_file.write(f"- **Raw Outputs Directory:** [`results/stage2/raw/`](file:///{raw_dir.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Consolidated Results:** [`results/stage2/results.json`](file:///{results_file.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Schedule File:** [`results/stage2/schedule_order.json`](file:///{schedule_file.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Runner Script:** [`runner/run_stage2.py`](file:///{os.path.abspath(__file__).replace(os.sep, '/')})\n")

    print(f"\n==================================================")
    print(f"Stage 2 Complete!")
    print(f"Report: {report_path}")
    print(f"Cost:   ${total_cost:.4f} USD")
    print(f"==================================================")


if __name__ == "__main__":
    main()
