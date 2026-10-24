# REAL_TEST_REQUIREMENTS.md: Protocol and Execution Standards for Live Agent Factorial Experiments

This document establishes the binding experimental protocol for executing the $2^{5-1}$ Resolution-V fractional factorial evaluation of AI reliability as an education optimization problem, incorporating all methodological lessons from prior iterations ($E1$–$E3c$).

---

## 1. Zero Synthetic Shortcuts Policy

1. **Live Agent Inference Only:** Every ticket patch must be synthesized via live model execution. No mock branches, hard-coded heuristics (`if r == 1: ref`), or synthetic patch generators are permitted.
2. **Preservation of Raw Generation Artifacts:** Every patch must be saved as an unedited text file (`<cell>_r<run>_t<ticket>.txt`) in the raw results directory before grading.
3. **Full Tool-Call and Execution Logging:** When tools ($u$) or bash commands are available, the harness must log the complete interaction transcript:
   - Exact command line invoked (e.g. `pytest -q tests/test_visible.py`)
   - Standard output and standard error
   - Exit code
   - Timestamps and token consumption per turn
   - Not merely a count of tool calls.

---

## 2. Environment, Model, and Code Freezing

1. **Frozen Code Repository:**
   - The evaluation harness (`harness/core.py`), benchmark suites, and grading scripts must be frozen and committed with a recorded git commit SHA before any agent runs commence.
   - Any modification to benchmark code mid-evaluation invalidates the cohort and requires a documented replication.
2. **Recorded Model Specifications:**
   - Record the exact foundation model identifier, provider API version, system prompt, temperature, and sampling parameters (e.g., `model="claude-3-5-sonnet-20241022"`, `temperature=0.0`).
   - For prior pilot runs where version metadata was omitted, document explicitly as: *"Claude Sonnet subagents (exact version not recorded)"*.
3. **Verified Pre-Flight Execution:**
   - Before launching an evaluation cohort, run pre-flight verification on all tasks:
     1. Gold reference patch passes 100% of visible and hidden tests.
     2. Unpatched baseline code fails hidden tests (100% failure rate; zero false positives).

---

## 3. The Fairness Gate: Preventing the Hard4 Trap

In $E3c$ (Hard4 first version), pass rates collapsed to $\approx 57\%$ because three tickets (`h602`, `h604`, `h605`) required unstated conventions (e.g., specific boolean strings, raising `ValueError` on unterminated quotes, wildcard `*` matching). Both the no-tool and tool arms failed identically because the required behavior was physically absent from the prompt, transforming the benchmark into a test of lucky guessing.

To ensure fair measurement:
1. **The Fairness Table:** Every task must be accompanied by a documented fairness table certifying where the agent can discover each behavior tested in the hidden suite:
   - **Column 1:** Hidden Test Assertion / Requirement
   - **Column 2:** Visible Source (Docstring, Issue Text, Visible Test, or Repository Type Signature)
   - **Column 3:** Knowledge Domain (Standard Library specification vs. Custom Business Rule)
2. **No Unstated Conventions:** Custom business conventions must be discoverable either through docstrings, existing codebase tests, or explicit issue descriptions. Hidden tests must verify generalizable compliance with stated contracts, not unstated preferences.
3. **Difficulty Target Decoupled from Guessing:** Target difficulty must be established prior to evaluation by increasing architectural complexity, multi-file coupling, and stateful invariants—never by withholding requirements. Report the empirical outcome whatever it is.

---

## 4. Single-Ticket Session Isolation ($E4$ Protocol)

In $E1$–$E3b$, agents processed batches of 12 tickets within a single shared context session, causing behavioral traits (such as appending regression tests to protected test files in Run 2) to cluster across 8–10 tickets simultaneously.

1. **Independent Session per Ticket:** Every attempt must execute in a completely fresh, isolated conversation session.
2. **Zero Memory Leakage:** No scratchpad notes, file modifications, or conversation history from Ticket $i$ may persist into Ticket $j$.
3. **Blocking Statistical Analysis:** Because attempts are session-isolated, the analysis must treat **Ticket** as a blocking factor and **Cohort Run** as a replication factor:
   $$\hat{y}_{ijk} = \mu + \text{Design}_i + \text{Ticket}_j + \text{Run}_k + \epsilon_{ijk}$$
   This accounts for task difficulty variance while preserving true degrees of freedom.

---

## 5. Specification of Educational Factors ($s, p, u, r, k$)

The 16 cells of the $2^{5-1}$ resolution-V design are defined by the relation $I = s \cdot p \cdot u \cdot r \cdot k \implies k = s \cdot p \cdot u \cdot r$ in $\pm 1$ sign coding ($k=1$ if $(s+p+u+r)$ is even in $\{0,1\}$ indicator space):

| Coordinate | Negative State ($-$) | Positive State ($+$) | Operational Mechanism |
| :--- | :--- | :--- | :--- |
| **Sources ($s$)** | $s_1$: Bare task instruction (No Book). | $s_3$: Full 16-rule engineering process book (`B.md`). | Provides global invariants: W05 test protection, W08 backward compatibility, W10 path sanitization. |
| **Practice ($p$)** | $p_1$: Zero-shot (no practice tickets). | $p_3$: Two worked examples from practice suite (`P3.md`). | Demonstrates concrete architectural patterns and refactoring shims. |
| **Tools ($u$)** | $u_1$: None (static generation without tools). | $u_2$: Interactive in-turn test runner tool. | Agent is provided an interactive tool to run `pytest` against visible test files during drafting and inspect stdout/stderr before submitting. |
| **Review ($r$)** | $r_1$: None (immediate submission). | $r_2$: Structured self-review checklist (`R2.md`). | Prompts agent to verify patch against edge cases (empty collections, negative numbers, exception types). |
| **Retry ($k$)** | $k_1$: Single attempt ($k^-$). | $k_2$: Exactly one post-submission retry on automated feedback ($k^+$). | Automated harness evaluates initial patch; on policy check failure or visible test failure, returns traceback for one corrective retry turn. |

> **Pre-Registration Design Specification (Choice B):**  
> We deliberately define $u$ and $k$ as orthogonal temporal interventions:  
> - **Factor $u$ (In-Turn Interactive Exploration):** Grants active test runner access *during the authoring process* prior to final patch emission.  
> - **Factor $k$ (Post-Submission Feedback Retry):** Implements an automated CI/CD grader check *after initial submission*, returning policy error diagnostics or visible test failure tracebacks for exactly one corrective retry turn ($k_2$).  
> Cells with $u=0, k=1$ receive automated test feedback only upon failure of their initial submission, isolating the effect of reactive feedback from proactive sandbox exploration.

### Factorial Design Matrix (Resolution V)
| Cell Code | $s$ | $p$ | $u$ | $r$ | $k$ | Cell Code | $s$ | $p$ | $u$ | $r$ | $k$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| `C0000` | 0 | 0 | 0 | 0 | **1** | `C1000` | 1 | 0 | 0 | 0 | **0** |
| `C0001` | 0 | 0 | 0 | 1 | **0** | `C1001` | 1 | 0 | 0 | 1 | **1** |
| `C0010` | 0 | 0 | 1 | 0 | **0** | `C1010` | 1 | 0 | 1 | 0 | **1** |
| `C0011` | 0 | 0 | 1 | 1 | **1** | `C1011` | 1 | 0 | 1 | 1 | **0** |
| `C0100` | 0 | 1 | 0 | 0 | **0** | `C1100` | 1 | 1 | 0 | 0 | **1** |
| `C0101` | 0 | 1 | 0 | 1 | **1** | `C1101` | 1 | 1 | 0 | 1 | **0** |
| `C0110` | 0 | 1 | 1 | 0 | **1** | `C1110` | 1 | 1 | 1 | 0 | **0** |
| `C0111` | 0 | 1 | 1 | 1 | **0** | `C1111` | 1 | 1 | 1 | 1 | **1** |

---

## 6. Feedback Contracts for Review and Retry

To prevent ambiguous intervention:
1. **Self-Review Feedback ($r_2$):** Consists strictly of a standardized pre-submission prompt:
   > *"Review your unified diff against docstring contracts: (1) Did you alter any test file? (2) Are boundary values (empty, zero, negative) handled? (3) Are raised exception types exact? (4) Does the patch preserve caller backward compatibility?"*
2. **Retry Feedback ($k_2$):**
   - **On Policy Violation:** Returns exact policy error: `"Policy Check Failed: Unified diff modifies protected file: <path>. Do not modify test directory files."`
   - **On Visible Test Failure:** Returns raw pytest failure block (exit code, failure traceback, failing assertion).
   - Maximum 1 retry allowed ($k_2$). The retry attempt is audited in `_transcript.json` and evaluated in `_grade_final.json`.

---

## 7. Analysis Plan and Deviations Log

1. **Pre-Registered Analysis:**
   - Fit Ordinary Least Squares (OLS) regression on run-level and ticket-blocked outcomes:
     $$\hat{y} = \beta_0 + \sum_{i} \beta_i x_i + \sum_{i<j} \beta_{ij} x_i x_j + \gamma_{\text{ticket}}$$
   - Report effect sizes ($\beta$), standard errors, $t$-statistics, exact $p$-values, and Wilson score intervals ($\alpha = 0.05$).
2. **Deviations File (`DEVIATIONS.md`):**
   - Any runtime failure, API timeout, workspace overwrite, or manual intervention must be logged immediately with timestamp, ticket ID, and corrective action taken.

---

## 8. Addendum v2 (binding from Round 8): Baseline, Suite e5, Controls and Gates

This section supersedes any conflicting earlier text for NEW experiments (suite_e5 onward). suite_e4 is a calibration/pilot suite only.

### 8.0 Round 8 rulings
- Gate A (suite_e4) = difficulty calibration only. Reported result: baseline 56.7%, full scaffolding 61.7%, difference not detected (p = 0.875), ~5.6x billed tokens; per-task effects did not replicate across two runs. No claim of scaffolding benefit may be made from suite_e4.
- R8-1: Task 1005 is unfair as written (trailing-slash prefix behavior unstated). Fix or remove; correct FAIRNESS_e4.md; audit 1010.
- R8-2: u = mandated in-turn test run (proactive); k = reactive feedback retry. They overlap in information; their interaction is estimated, never assumed absent. State the mandated turn-1 test instruction as part of the u=1 treatment.
- Selection rule: tasks are kept or edited using BASELINE pass rate and fairness evidence only, never scaffolding gain.
- Use >= 10 runs per cell/instance for confirmation; repeat a subset of cells to estimate run-to-run noise.

Purpose: make the factors separable. Scaffolding can only help where it supplies something the baseline lacks AND the task needs. All rules in REAL_TEST_REQUIREMENTS.md still apply (live runs only, no simulation, audit trail, review gates).
Sequencing: finish the Round 7 items on the Gemini Gate A set first (H-1..H-4). This spec applies to the NEW suite (suite_e5). Do not edit suite_e4 to look like it.

### 8.1. Terminology
- Agent harness = the 5 factors (s,p,u,r,k) we vary. Evaluation runner = agent_runner.py/grader.py (measurement code). Use these terms in code comments and the paper.

### 8.2. Baseline B0 (cell 00000-equivalent; identical in every cell except through the factors)
Task input in EVERY cell: (a) ticket text; (b) the failing traceback or failing-behavior excerpt; (c) ONLY the file(s) named in the traceback (not the whole repo); (d) the standard output-format envelope (identical text in all cells).
Baseline has: no handbook, no examples, no visible tests, no tools, no review turn, no retry. One call.
Record per task the "context package" hash so it is provably identical across cells.

### 8.3. Education arms (what each factor adds)
| Factor | Level 1 content |
| s sources | HANDBOOK.md: the house conventions (rounding, error types, immutability, ordering, boundary rules, "never edit tests"). Real version. |
| p practice | 2 worked examples (ticket -> patch -> why) from the SAME bug family but a DIFFERENT instance than any evaluated task. |
| u tools | Native function calling (Gemini and Claude both support it): read_file(path), grep(pattern), run_tests(paths). Whole repo becomes explorable. Log every call (name, args, result). |
| r review | One extra turn with the review checklist; reply must be a complete patch. |
| k retry | Exactly one retry with visible-test output when visible tests fail OR a protected file was modified. DEFINE k this way in the protocol and paper (k = feedback retry). |
Controls (new, mandatory):
- PLACEBO handbook: same token length (+/-3%), same format, irrelevant but plausible rules (style, naming, logging). Cell pair s=1 vs s=placebo run on the held-out set. A gain not present with placebo is attributed to content, not tokens.
- Tool-use accounting: report tools OFFERED vs USED per cell; analyze u on the subset where the tool was used.

### 8.4. Task suite (suite_e5): template-generated, >= 24 evaluated instances
Build 6-8 bug FAMILIES, each with a generator that yields >= 4 distinct instances (different names, numbers, module layout), 2-4 coupled files each.
Suggested families (adapt): (1) money/rounding conversion; (2) nested config merge without aliasing; (3) calendar/recurrence boundaries; (4) CSV/escape round trip; (5) permission/prefix normalization; (6) event ordering with mutation during iteration; (7) cache/TTL with injectable clock; (8) ledger/period half-open intervals.
Each task has a CLASS tag:
- STATED: every hidden-test behavior is in ticket text or docstrings of files provided to ALL cells.
- TAUGHT: some hidden-test behaviors are house conventions that appear ONLY in HANDBOOK.md (and the placebo does not contain them). Fairness for TAUGHT: the convention must be (i) written in the handbook sentence-for-sentence, (ii) not guessable as the only reasonable behavior (test that two reasonable alternative implementations exist), (iii) tagged in FAIRNESS_e5.md with its handbook line.
- DISTRACTOR (>= 2 instances): a handbook rule that is correct in general but must NOT be applied here (the Task-1006 lesson). Tests whether scaffolding can hurt.
- TRANSFER (>= 3 instances, new family not in practice examples): measures whether teaching generalizes.
Each task also has: hidden-root-cause variant where the buggy module is NOT the one in the traceback (explorable only with u=1) in >= 1/3 of tasks, and a visible-test-sensitive variant where the first obvious fix fails a visible test in >= 1/3 of tasks.
Mandatory per task before any model run: gold solution passes; unpatched fails; two plausible-wrong fixes each fail (mutation check); FAIRNESS_e5.md row for every hidden assertion with its visible source and class.

### 8.5. Calibration gate (baseline-only; never use scaffolding gain to select tasks)
Run B0 (5 runs/instance) and the full-scaffolding cell (5 runs/instance) on every instance with the frozen config.
Keep an instance for the factorial only if baseline pass rate is in [15%, 85%]. Target: suite-level baseline 30-50%, full cell 75-90%. Drop or revise by BASELINE rate and fairness evidence only. Log every drop/edit in DEVIATIONS.md (task id, reason, baseline rate that triggered it).
Then FREEZE: task list, handbook, placebo, examples, runner config, thinking/reasoning budget, max_output_tokens, commit SHA. After freeze no edits.

### 8.6. Splits
- TUNE set (about 2/3 of instances, whole families kept together where possible): used for the 16-cell factorial and for choosing theta*.
- HELD-OUT set (about 1/3, includes all TRANSFER and some instances of every other family): never run before the pre-registration is committed. Run only: B0, theta*, theta* with placebo in place of s, full scaffolding. >= 10 runs per instance.
- Clustering: analyze with instance and family as clusters (mixed model or cluster bootstrap); report run-level and instance-level uncertainty. Permutation tests on instance-level rates.

### 8.7. Pre-registration (commit PREREGISTRATION.md BEFORE the held-out run; Claude reviews it)
Primary hypothesis and test (theta* vs B0 on held-out, instance-clustered, one-sided or two-sided stated), primary metric (strict pass at final), secondary metrics (attempt-1 strict, cost per pass in billed tokens incl. reasoning tokens), exclusion rules (infrastructure errors only, rerun and logged, never outcome-based), how theta* is chosen from the factorial (predefined rule, e.g. best cell by tune-set strict pass with ties broken by cost), multiple-comparison handling, and the stopping rule. Report null results.

### 8.8. Runner requirements
- Same frozen config for ALL rows of a given experiment; sha stamped per row; every row has provider response ids, input/output/reasoning/total billed tokens, stop_reason per turn, tools offered/used, per-turn audit files.
- Native function calling for u=1; fatal on missing/unrecognized stop_reason handling; unit tests for truncation and tool-loop exhaustion.
- Cost report after each phase (billed tokens x list price) so the credit budget is tracked.

### 8.9. Deliverables and gates
1. suite_e5 + FAIRNESS_e5.md + validators + placebo + handbook (offline, no model calls). -> Claude reviews (Gate S).
2. Calibration run (section 5) with frozen config. -> Claude reviews (Gate A2). Factorial stays locked until pass.
3. Pre-registration. -> Claude reviews (Gate P).
4. Tune-set factorial (16 cells x >= 5 runs). -> Claude reviews (Gate B).
5. Held-out confirmation, then second model (Claude) replication of steps 2-5 as budget allows.
File ownership: antigravity writes code/results/STATUS/DEVIATIONS; Claude writes only review files. No simulated or hand-assembled results, ever.
