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

The 16 cells of the $2^{5-1}$ resolution-V design are defined by the relation $I = s \cdot p \cdot u \cdot r \cdot k \implies k = s \cdot p \cdot u \cdot r$:

| Coordinate | Negative State ($-$) | Positive State ($+$) | Operational Mechanism |
| :--- | :--- | :--- | :--- |
| **Sources ($s$)** | $s_1$: Bare task instruction (No Book). | $s_3$: Full 16-rule engineering process book (`B.md`). | Provides global invariants: W05 test protection, W08 backward compatibility, W10 path sanitization. |
| **Practice ($p$)** | $p_1$: Zero-shot (no practice tickets). | $p_3$: Two worked examples from practice suite (`P3.md`). | Demonstrates concrete architectural patterns and refactoring shims. |
| **Tools ($u$)** | $u_1$: None (static diff generation only). | $u_2$: Interactive bash test runner. | Agent is provided a tool to run `pytest` against visible test files and inspect stdout/stderr. |
| **Review ($r$)** | $r_1$: None (immediate submission). | $r_2$: Structured self-review checklist (`R2.md`). | Prompts agent to verify patch against edge cases (empty collections, negative numbers, exception types). |
| **Retry ($k$)** | $k_1$: Single attempt ($k^-$). | $k_2$: Up to 2 retries on automated feedback ($k^+$). | Automated harness returns policy check failure or visible test traceback; agent resubmits fix. |

---

## 6. Feedback Contracts for Review and Retry

To prevent ambiguous intervention:
1. **Self-Review Feedback ($r_2$):** Consists strictly of a standardized pre-submission prompt:
   > *"Review your unified diff against docstring contracts: (1) Did you alter any test file? (2) Are boundary values (empty, zero, negative) handled? (3) Are raised exception types exact? (4) Does the patch preserve caller backward compatibility?"*
2. **Retry Feedback ($k_2$):**
   - **On Policy Violation:** Returns exact policy error: `"Policy Check Failed: Unified diff modifies protected file: <path>. Do not modify test directory files."`
   - **On Visible Test Failure:** Returns raw pytest failure block (exit code, failure traceback, failing assertion).
   - Maximum 2 retries allowed. All retry attempts must be logged separately as `_retry1.txt` and `_retry2.txt`.

---

## 7. Analysis Plan and Deviations Log

1. **Pre-Registered Analysis:**
   - Fit Ordinary Least Squares (OLS) regression on run-level and ticket-blocked outcomes:
     $$\hat{y} = \beta_0 + \sum_{i} \beta_i x_i + \sum_{i<j} \beta_{ij} x_i x_j + \gamma_{\text{ticket}}$$
   - Report effect sizes ($\beta$), standard errors, $t$-statistics, exact $p$-values, and Wilson score intervals ($\alpha = 0.05$).
2. **Deviations File (`DEVIATIONS.md`):**
   - Any runtime failure, API timeout, workspace overwrite, or manual intervention must be logged immediately with timestamp, ticket ID, and corrective action taken.
