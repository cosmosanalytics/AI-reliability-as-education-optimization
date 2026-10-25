#!/usr/bin/env python3
"""Dumps dry-run prompt proof for Round 25 Review mandate.

Dumps the complete full prompt for 2 Taught tasks (2002 money_rounding and 2037 wire_envelope)
under cells C1000, C0100, and C1100, displaying exact token counts and the first 20 lines.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runner"))
sys.path.insert(0, os.path.join(REPO_ROOT, "benchmarks"))
sys.path.insert(0, os.path.join(REPO_ROOT, "harness"))

import suite_e5
from agent_runner import STANDARD_TASK_ENVELOPE_HEADER

tasks = {t["id"]: t for t in suite_e5.T}


def build_task_prompt(ticket):
    prompt_files = ticket["repo"]
    repo_listing = "".join(
        f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
        for p, c in prompt_files.items()
    )
    tb_section = ""
    if "traceback_text" in ticket and ticket["traceback_text"]:
        tb_section = f"FAILING TEST TRACEBACK:\n{ticket['traceback_text']}\n\n"

    return (
        f"{STANDARD_TASK_ENVELOPE_HEADER}\n\n"
        f"TICKET ISSUE:\n{ticket['issue']}\n\n"
        f"{tb_section}"
        f"REPOSITORY FILES:\n{repo_listing}"
    )


def dump_proof():
    output_lines = []
    for tid in [2002, 2037]:
        ticket = tasks[tid]
        output_lines.append("================================================================================")
        output_lines.append(f"TASK {tid} | Family: {ticket['family']} | Classification: TAUGHT")
        output_lines.append("================================================================================")

        for cell in ["C1000", "C0100", "C1100"]:
            brief_path = os.path.join(REPO_ROOT, "briefs", f"{cell}.md")
            brief_text = open(brief_path, "r", encoding="utf-8").read()
            user_prompt = build_task_prompt(ticket)

            # In Gemini 2.5 Flash, brief is passed as system_prompt and ticket prompt as user_prompt
            full_prompt = (
                f"=== SYSTEM PROMPT ({cell}.md) ===\n"
                f"{brief_text}\n"
                f"=== USER PROMPT (Task {tid}) ===\n"
                f"{user_prompt}"
            )

            char_count = len(full_prompt)
            word_count = len(full_prompt.split())
            approx_tokens = int(char_count / 3.8)

            output_lines.append(f"\n--- Condition {cell} (chars: {char_count:,}, words: {word_count:,}, approx tokens: ~{approx_tokens:,}) ---")
            for i, line in enumerate(full_prompt.splitlines()[:20]):
                output_lines.append(f"{i+1:2d}: {line}")
            output_lines.append("... [truncated for display]")
        output_lines.append("\n")

    return "\n".join(output_lines)


if __name__ == "__main__":
    proof = dump_proof()
    print(proof)
