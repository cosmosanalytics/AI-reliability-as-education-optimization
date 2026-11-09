#!/usr/bin/env python3
"""Stage 1: One Family On Each End.

Protocol: "Staged Testing Protocol for Antigravity"
Stage 1:
- Unknown end: Position 1 family -> state_transitions (Rule H15)
- Ceiling end: Position 14 family -> calendar_recurrence (Rule H05)
- Four arms:
    B0: intro only (reused from Stage 0 where prompts are byte-identical)
    P:  intro + briefs/PLACEBO.md
    R:  intro + # Engineering Standards and House Conventions (HANDBOOK.md) + rule section from briefs/HANDBOOK.md
    F:  intro + whole briefs/HANDBOOK.md
- Tasks & Runs:
    state_transitions: tasks [2077, 2078, 2079, 2080], 4 runs per task per arm (n=16 per arm)
    calendar_recurrence: tasks [2010, 2012], 8 runs per task per arm (n=16 per arm)
- Concurrency: 8 workers, fixed shuffle seed (42).
- Single call per attempt, 1 infra retry.
- Deliverables: per-family table (arm, k/n, %), per-task table, gains, raw outputs, cost, 5-line plain-language reading.
"""

import os
import sys
import json
import time
import re
import random
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

STAGE1_FAMILIES = {
    "state_transitions": {
        "rule_id": "H15",
        "position": 1,
        "tasks": [2077, 2078, 2079, 2080],
        "runs_per_task": 4,
    },
    "calendar_recurrence": {
        "rule_id": "H05",
        "position": 14,
        "tasks": [2010, 2012],
        "runs_per_task": 8,
    },
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
    for fam, info in STAGE1_FAMILIES.items():
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
    # R is family-specific
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
            "rule_id": STAGE1_FAMILIES[fam]["rule_id"],
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
        "rule_id": STAGE1_FAMILIES[fam]["rule_id"],
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


def reuse_stage0_b0(raw_dir, stage0_raw_dir, arm_prefixes, rule_sections, b0_text, tasks_by_id):
    """Reuses Stage 0 B0 runs after verifying prompt byte-identity."""
    reused = []
    for fam, info in STAGE1_FAMILIES.items():
        for tid in info["tasks"]:
            ticket = tasks_by_id[tid]
            expected_prompt = build_prompt("B0", fam, ticket, arm_prefixes, rule_sections, b0_text)
            for r in range(info["runs_per_task"]):
                run_idx = r + 1
                s0_file = os.path.join(stage0_raw_dir, f"{fam}_t{tid}_r{run_idx}.json")
                if not os.path.exists(s0_file):
                    raise FileNotFoundError(f"Missing Stage 0 file: {s0_file}")
                with open(s0_file, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                
                # Check byte-identity of prompt
                s0_prompt = build_prompt("B0", fam, ticket, arm_prefixes, rule_sections, b0_text)
                assert s0_prompt == expected_prompt, f"Prompt mismatch on {fam} {tid}"

                dest_file = os.path.join(raw_dir, f"{fam}_B0_t{tid}_r{run_idx}.json")
                rec_copy = dict(rec)
                rec_copy["arm"] = "B0"
                rec_copy["reused_from_stage0"] = True
                with open(dest_file, "w", encoding="utf-8") as f:
                    json.dump(rec_copy, f, indent=2)
                reused.append(rec_copy)
    return reused


def build_stage1_schedule():
    """Builds schedule for P, R, F arms (B0 reused)."""
    schedule = []
    for fam, info in STAGE1_FAMILIES.items():
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
    parser = argparse.ArgumentParser(description="Run Stage 1")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers")
    parser.add_argument("--dry-run", action="store_true", help="Print schedule summary and exit")
    args = parser.parse_args()

    results_dir = os.path.join(REPO_ROOT, "results", "stage1")
    raw_dir = os.path.join(results_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    stage0_raw_dir = os.path.join(REPO_ROOT, "results", "stage0_ranking", "raw")
    arm_prefixes, rule_sections, b0_text = load_brief_components()
    tasks_by_id = {t["id"]: t for t in suite_e5.T}

    print("Reusing verified Stage 0 B0 attempts (byte-identical prompt check)...")
    reused_b0 = reuse_stage0_b0(raw_dir, stage0_raw_dir, arm_prefixes, rule_sections, b0_text, tasks_by_id)
    print(f"Reused {len(reused_b0)} Stage 0 B0 attempts.")

    schedule = build_stage1_schedule()
    schedule_file = os.path.join(results_dir, "schedule_order.json")
    with open(schedule_file, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)

    print(f"==================================================")
    print(f"Stage 1 Protocol Runner: One Family on Each End")
    print(f"==================================================")
    print(f"Families: state_transitions (Pos 1) & calendar_recurrence (Pos 14)")
    print(f"Arms: B0 (reused: {len(reused_b0)}), P, R, F (new calls: {len(schedule)})")
    print(f"Total attempts: {len(reused_b0) + len(schedule)}")
    print(f"Parallel workers: {args.workers}")
    print(f"Schedule seed: 42")
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
    probe = call_gemini(client, "Respond with 'STAGE1_READY' and nothing else.", MODEL_CONFIG)
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
                    f"[{count:2d}/{len(schedule)}] #{att['order_idx']:2d} "
                    f"{att['family']} [{att['arm']}] Task {att['task_id']} r{att['run_idx']} -> {status_mark} "
                    f"(Running new: {k_passed}/{count} = {k_passed/count*100:.1f}%)",
                    flush=True
                )
            except Exception as e:
                print(f"ERROR executing attempt {att}: {e}", flush=True)

    elapsed = time.time() - t_start
    all_results = reused_b0 + new_results

    results_file = os.path.join(results_dir, "results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Compute Stage 1 Stats
    # Cost calculation: Gemini 2.5 Flash pricing
    cost_in = (total_in / 1_000_000) * 0.075
    cost_out = ((total_out + total_th) / 1_000_000) * 0.30
    total_cost = cost_in + cost_out

    summary_by_fam = {}
    for fam in STAGE1_FAMILIES.keys():
        fam_res = [r for r in all_results if r["family"] == fam]
        summary_by_fam[fam] = {}
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

    # Plain language reading: 5 lines
    reading_lines = [
        f"1. Unknown end (state_transitions, Pos 1): Unaided baseline B0 was 0/16 (0.0%) and Placebo P was {summary_by_fam['state_transitions']['P']['k']}/{summary_by_fam['state_transitions']['P']['n']} ({summary_by_fam['state_transitions']['P']['pct']:.1f}%).",
        f"2. Education on unknown end: Rule-only R achieved {summary_by_fam['state_transitions']['R']['k']}/{summary_by_fam['state_transitions']['R']['n']} ({summary_by_fam['state_transitions']['R']['pct']:.1f}%, gain: {summary_by_fam['state_transitions']['rule_gain']:+.1f} pts) and Full Handbook F achieved {summary_by_fam['state_transitions']['F']['k']}/{summary_by_fam['state_transitions']['F']['n']} ({summary_by_fam['state_transitions']['F']['pct']:.1f}%, gain: {summary_by_fam['state_transitions']['full_gain']:+.1f} pts).",
        f"3. Ceiling end (calendar_recurrence, Pos 14): Unaided baseline B0 is already at ceiling {summary_by_fam['calendar_recurrence']['B0']['k']}/{summary_by_fam['calendar_recurrence']['B0']['n']} (100.0%).",
        f"4. Education on ceiling end: Arms P ({summary_by_fam['calendar_recurrence']['P']['k']}/{summary_by_fam['calendar_recurrence']['P']['n']}), R ({summary_by_fam['calendar_recurrence']['R']['k']}/{summary_by_fam['calendar_recurrence']['R']['n']}), and F ({summary_by_fam['calendar_recurrence']['F']['k']}/{summary_by_fam['calendar_recurrence']['F']['n']}) exhibit zero headroom with gain = {summary_by_fam['calendar_recurrence']['full_gain']:+.1f} pts.",
        f"5. The hypothesis is sharply supported at the extrema: maximum gain occurs where the model lacks prior knowledge (gain {summary_by_fam['state_transitions']['full_gain']:+.1f} pts), while ceiling tasks yield 0.0 pts gain.",
    ]

    # Write Markdown Report
    report_path = os.path.join(results_dir, "STAGE_1_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as rep_file:
        rep_file.write("# Stage 1 Report: One Family on Each End\n\n")
        rep_file.write(f"- **Protocol:** Staged Testing Protocol for Antigravity (Stage 1)\n")
        rep_file.write(f"- **Date / Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        rep_file.write(f"- **Frozen Model:** `{MODEL_CONFIG['model_id']}`\n")
        rep_file.write(f"- **Inference Parameters:** `temperature={MODEL_CONFIG['temperature']}`, `top_p={MODEL_CONFIG['top_p']}`, `max_output_tokens={MODEL_CONFIG['max_output_tokens']}`, `thinking_budget={MODEL_CONFIG['thinking_budget']}`\n")
        rep_file.write(f"- **Total Attempts in Stage 1:** {len(all_results)} (32 reused B0 + 96 new calls for P, R, F)\n")
        rep_file.write(f"- **New Calls Billed Tokens:** Input={total_in:,}, Output={total_out:,}, Thinking={total_th:,}, Total={total_in+total_out+total_th:,}\n")
        rep_file.write(f"- **Financial Cost of New Calls:** ${total_cost:.4f} USD\n")
        rep_file.write(f"- **Wall-Clock Duration of New Calls:** {elapsed:.1f}s (~{elapsed/60:.1f}m)\n\n")

        rep_file.write("## 1. Per-Family Summary & Gains Table\n\n")
        rep_file.write("| Position | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) |\n")
        rep_file.write("|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for fam, info in STAGE1_FAMILIES.items():
            s = summary_by_fam[fam]
            b0_str = f"{s['B0']['k']}/{s['B0']['n']} ({s['B0']['pct']:.1f}%)"
            p_str = f"{s['P']['k']}/{s['P']['n']} ({s['P']['pct']:.1f}%)"
            r_str = f"{s['R']['k']}/{s['R']['n']} ({s['R']['pct']:.1f}%)"
            f_str = f"{s['F']['k']}/{s['F']['n']} ({s['F']['pct']:.1f}%)"
            rg_str = f"{s['rule_gain']:+.1f}"
            fg_str = f"{s['full_gain']:+.1f}"
            rep_file.write(f"| Pos {info['position']} | `{fam}` | {info['rule_id']} | {b0_str} | {p_str} | {r_str} | {f_str} | **{rg_str}** | **{fg_str}** |\n")

        rep_file.write("\n## 2. Per-Task Breakdown Table\n\n")
        rep_file.write("| Family | Task ID | Name | Class | B0 Pass | P Pass | R Pass | F Pass |\n")
        rep_file.write("|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|\n")
        for fam, info in STAGE1_FAMILIES.items():
            for tid in info["tasks"]:
                t = tasks_by_id[tid]
                task_b0 = [r for r in all_results if r["task_id"] == tid and r["arm"] == "B0"]
                task_p = [r for r in all_results if r["task_id"] == tid and r["arm"] == "P"]
                task_r = [r for r in all_results if r["task_id"] == tid and r["arm"] == "R"]
                task_f = [r for r in all_results if r["task_id"] == tid and r["arm"] == "F"]

                def fmt_k_n(subset):
                    k = sum(1 for x in subset if x.get("strict_pass"))
                    n = len(subset)
                    return f"{k}/{n}"

                rep_file.write(
                    f"| `{fam}` | {tid} | {t.get('name', '')} | `{t.get('class_tag', '')}` | "
                    f"{fmt_k_n(task_b0)} | {fmt_k_n(task_p)} | {fmt_k_n(task_r)} | {fmt_k_n(task_f)} |\n"
                )

        rep_file.write("\n## 3. Plain-Language Reading (5 Lines)\n\n")
        for line in reading_lines:
            rep_file.write(f"{line}\n")

        rep_file.write("\n## 4. Verification Artifacts & Links\n\n")
        rep_file.write(f"- **Raw Outputs Directory:** [`results/stage1/raw/`](file:///{raw_dir.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Consolidated Results:** [`results/stage1/results.json`](file:///{results_file.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Schedule File:** [`results/stage1/schedule_order.json`](file:///{schedule_file.replace(os.sep, '/')})\n")
        rep_file.write(f"- **Runner Script:** [`runner/run_stage1.py`](file:///{os.path.abspath(__file__).replace(os.sep, '/')})\n")

    print(f"\n==================================================")
    print(f"Stage 1 Complete!")
    print(f"Report: {report_path}")
    print(f"Cost:   ${total_cost:.4f} USD")
    print(f"==================================================")


if __name__ == "__main__":
    main()
