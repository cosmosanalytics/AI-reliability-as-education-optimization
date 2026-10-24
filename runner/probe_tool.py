import os
import sys

repo_root = "C:/Users/richa/ai-engineering/repo_push"
sys.path.insert(0, os.path.join(repo_root, "runner"))
sys.path.insert(0, os.path.join(repo_root, "benchmarks"))
import suite_e4
import agent_runner
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
t1002 = [t for t in suite_e4.T if t["id"] == 1002][0]
repo_listing = "".join(
    f"=== FILE: {p} ===\n{c.rstrip()}\n=== END ===\n"
    for p, c in t1002["repo"].items()
)

print("--- EXPERIMENT 1: Explicit Workflow Prompting for Text Protocol ---")
prompt_text = f"""Resolve this ticket. First read the whole ticket and every repository file below.

TICKET ISSUE:
{t1002['issue']}

REPOSITORY FILES:
{repo_listing}

WORKFLOW REQUIREMENT:
You have access to an interactive test execution tool.
Before outputting any patch, you MUST run the test suite by outputting:
=== TOOL: pytest ===
tests/
=== END_TOOL ===
Do not output any FILE blocks until you have run the tests."""

res1 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_text,
    config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=2048,
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
    ),
)
resp1 = res1.text or ""
print("Experiment 1 text match:", bool(agent_runner.TOOL_BLOCK_REGEX.search(resp1)))
print("Experiment 1 output:\n", resp1[:400])

print("\n--- EXPERIMENT 2: Native Tool / Function Calling ---")
def run_pytest(test_path: str = "tests/") -> str:
    """Executes pytest on the test suite in the workspace sandbox."""
    return "test output"

res2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Resolve this ticket: {t1002['issue']}\nRun tests to verify.",
    config=types.GenerateContentConfig(
        temperature=0.0,
        tools=[run_pytest],
        max_output_tokens=2048,
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
    ),
)

has_func_call = False
if res2.candidates and res2.candidates[0].content.parts:
    for part in res2.candidates[0].content.parts:
        if getattr(part, "function_call", None):
            has_func_call = True
            print("Native Function Call Detected:", part.function_call.name, part.function_call.args)

print("Experiment 2 native function call triggered?", has_func_call)
