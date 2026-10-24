# REAL_TEST_REQUIREMENTS.md: Protocol for Live Agent Factorial Experiments

This document defines the strict experimental and execution requirements for running the $2^{5-1}$ Resolution-V fractional factorial experiment ($E3$) with real AI agents, avoiding the ceiling effects and simulation shortcuts diagnosed in earlier iterations.

---

## 1. Zero Synthetic Shortcuts Policy
1. **Live Agent Inference Only:** Every patch must be synthesized by a live model call (e.g. Anthropic Claude 3.5 Sonnet subagent or API completion). No deterministic helper functions, heuristic fallbacks, or conditional mock branches (`if r == 1: ref`) are permitted.
2. **Raw Patch Artifacts Preserved:** All outputs must be saved to disk as unedited raw text files (`<design>_r<run>_t<ticket>.txt`) with full generation timestamps and token accounting metadata before grading.
3. **External Grader Isolation:** The grading harness (`harness/core.py`) must evaluate patches blindly in isolated temporary environments without passing information to the agent during single-pass arms.

---

## 2. Benchmark Difficulty: Breaking the Prompt-Contained Ceiling
The primary finding from $E1$–$E3c$ (>2,300 attempts) is that **tasks that fit within the LLM prompt context hit a 95–100% functional ceiling**, preventing separation of educational components ($s, p, u, r, k$).

A valid separating benchmark must meet the following criteria:
1. **Non-Trivial Repository Footprint:** The codebase must contain multiple modules and exceeds 10,000 tokens of source code, making it impossible to paste the entire repository into a zero-shot prompt.
2. **Active Specification Discovery:** The required behavior must not be summarized in a one-paragraph prompt. The agent must search the repository, read interface contracts, and trace existing tests to deduce requirements.
3. **Complex Invariants:** Problems must feature stateful invariants, concurrency controls, or non-obvious boundary conditions where static first drafts have an expected failure rate of 40–60%.
4. **Distinction Between Compliance and Capability:**
   - Policy checks (tamper detection) must be isolated from functional test execution.
   - Test files must be protected at the filesystem permission level (or via git diff isolation).

---

## 3. Session Isolation Protocol ($E4$ Protocol)
To eliminate run-level behavioral clustering (where a model's stylistic preference in Run 2 moved 8 tickets simultaneously):
1. **One Agent per Ticket:** Each ticket attempt must be executed in a completely fresh, isolated conversation session.
2. **No Shared In-Context Memory:** No history from prior ticket attempts may leak into subsequent tickets.
3. **Permuted Ticket Order:** If cohort batches are evaluated, ticket sequences must be randomized across seeds.
4. **Effective Sample Size:** Hypothesis testing must be calculated on independent runs ($N_{\text{eff}} = \text{runs}$), with degrees of freedom reflecting true session independence.

---

## 4. Execution Matrix: 16-Cell Fractional Factorial ($2^{5-1}$)

Defining relation: $I = s \cdot p \cdot u \cdot r \cdot k \implies k = s \cdot p \cdot u \cdot r$.

| Cell | $s$ (Sources) | $p$ (Practice) | $u$ (Tools) | $r$ (Review) | $k$ (Retry) | Execution Brief |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0000** | None | None | None | None | Retries ($k^+$) | Bare prompt + policy/test retry loop |
| **0001** | None | None | None | Checklist | Single-pass ($k^-$) | Bare prompt + self-review reflection |
| **0010** | None | None | Test Runner | None | Single-pass ($k^-$) | Interactive pytest bash tool |
| **0011** | None | None | Test Runner | Checklist | Retries ($k^+$) | Pytest tool + review + retry loop |
| **0100** | None | Examples | None | None | Single-pass ($k^-$) | 2 worked examples in prompt |
| **0101** | None | Examples | None | Checklist | Retries ($k^+$) | Examples + review + retry loop |
| **0110** | None | Examples | Test Runner | None | Retries ($k^+$) | Examples + test runner + retry loop |
| **0111** | None | Examples | Test Runner | Checklist | Single-pass ($k^-$) | Examples + test runner + review |
| **1000** | Full Book | None | None | None | Single-pass ($k^-$) | Baseline $B$ (16-rule process book) |
| **1001** | Full Book | None | None | Checklist | Retries ($k^+$) | Full Book + review + retry loop |
| **1010** | Full Book | None | Test Runner | None | Retries ($k^+$) | Full Book + test runner + retry loop |
| **1011** | Full Book | None | Test Runner | Checklist | Single-pass ($k^-$) | Full Book + test runner + review |
| **1100** | Full Book | Examples | None | None | Retries ($k^+$) | Full Book + examples + retry loop |
| **1101** | Full Book | Examples | None | Checklist | Single-pass ($k^-$) | Full Book + examples + review |
| **1110** | Full Book | Examples | Test Runner | None | Single-pass ($k^-$) | Full Book + examples + test runner |
| **1111** | Full Book | Examples | Test Runner | Checklist | Retries ($k^+$) | Full curriculum enabled |

---

## 5. Token & Cost Accounting Standards
For every attempt, the test harness must record:
1. `prompt_tokens`: exact input token count including brief, repository files, and conversation turns.
2. `completion_tokens`: exact output token count generated by the model.
3. `tool_calls_count`: number of bash / pytest / grep invocations executed.
4. `retries_triggered`: number of resubmission cycles triggered by failed checks (capped at 2).
5. `wall_clock_time`: latency per attempt from prompt presentation to final patch verdict.

These logged quantities provide the ground-truth cost coefficients ($c_i$) for parameterizing the knapsack MIP surrogate.
