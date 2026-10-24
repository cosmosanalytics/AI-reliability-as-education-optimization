import os
import sys
import json

repo_root = "C:/Users/richa/ai-engineering/repo_push"
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))
import suite_e4
import agent_runner

client = agent_runner.LiveModelBackend(
    model_id="gemini-2.5-flash", temperature=0.0, backend="gemini"
)

# Test updated TOOL_INSTRUCTION_ENVELOPE
MANDATORY_TOOL_ENVELOPE = (
    "\n\nINTERACTIVE TEST RUNNER TOOL:\n"
    "You have access to an interactive test execution tool in your workspace.\n"
    "WORKFLOW REQUIREMENT:\n"
    "In your first turn, you must invoke the test runner to observe test behavior in the repository by outputting:\n"
    "=== TOOL: pytest ===\n"
    "tests/\n"
    "=== END_TOOL ===\n"
    "You will receive the test execution exit code and traceback in the next turn.\n"
    "When you are finished testing and ready to submit your final patch, output ONLY the patch in the standard format:\n"
    "=== FILE: path/to/file ===\n"
    "... complete file content ...\n"
    "=== END ===\n"
    "Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."
)

tasks_to_test = [t for t in suite_e4.T if t["id"] in [1001, 1002, 1006]]
probe_dir = os.path.join(repo_root, "results", "probe_u_mandatory")
os.makedirs(probe_dir, exist_ok=True)

# Temporarily patch TOOL_INSTRUCTION_ENVELOPE in agent_runner
agent_runner.TOOL_INSTRUCTION_ENVELOPE = MANDATORY_TOOL_ENVELOPE

for ticket in tasks_to_test:
    t_id = ticket["id"]
    print(f"\n--- Testing Mandatory Tool Workflow on Task {t_id}: {ticket['name']} ---")
    res = agent_runner.run_single_attempt(
        cell_code="C1111",
        s_val=1,
        p_val=1,
        u_val=1,
        r_val=1,
        k_val=1,
        run_idx=101,
        ticket=ticket,
        brief_text="You are a careful senior software engineer who ships small, correct, well-scoped patches.",
        backend_client=client,
        frozen_commit_sha="probe_v2",
        retry_feedback_mode="policy_plus_visible_pytest",
        raw_dir=probe_dir,
    )
    print(f"Task {t_id} result:")
    print(f"  tool_used: {res['tool_used']}")
    print(f"  tool_call_count: {res['tool_call_count']}")
    print(f"  strict_pass: {res['final_strict']}")

    tool_log_file = os.path.join(probe_dir, f"C1111_r101_t{t_id}_tool_log.json")
    if os.path.exists(tool_log_file):
        tool_log = json.load(open(tool_log_file, encoding="utf-8"))
        print(f"  tool_log entries: {len(tool_log)}")
        for entry in tool_log:
            print(f"    call {entry.get('call_idx')}: cmd='{entry.get('cmd')}', exit code {entry.get('exit_code')}")
            print(f"    output excerpt:\n{entry.get('output', '')[:200]}")
