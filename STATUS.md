# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Phase 1 (Difficulty Gate A Re-analyzed — Awaiting Gate A Round 2 Review)  
**Phase State:** **Difficulty Gate A Evaluated (Ceiling Broken; Scaffolding Superiority Not Statistically Significant)**  
**Frozen SHA:** `f9d6c18` (tasks and preflight suite frozen prior to Gate A execution; all G-1..G-4 harness fixes committed)  
**Model Specifications:**  
- **Model ID:** `gemini-2.5-flash`  
- **Sampling Settings:** `temperature=0.0`, `max_output_tokens=16384`, `thinking_budget=2048`  
- **Concurrency:** 6 parallel worker threads with thread-safe file locking  
- **Stop Reason Verification:** `stop_reason` recorded per turn; `MAX_TOKENS` / `FinishReason.MAX_TOKENS` truncations raise a fatal `RuntimeError` and are excluded from silent grading (100% of Gate A rows completed with `FinishReason.STOP`)  
- **Randomization Seed:** `42` (logged in `schedule_order.json` and `rows.json`)  
- **Execution Backend:** Direct Google Gemini API with mandatory startup probe (`startup_self_check`)  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Complete and Verified** | `c81d851` | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, Resolution-V parity, interactive tool calling loop, standardized task envelope, audit trail, 10 hermetic unit tests. Live dry run verified on `gemini-2.5-flash`. |
| **Phase 1** | New Benchmark & Difficulty Gate | **Complete (Re-analyzed post G-1..G-4)** | *Current* | 12 multi-module repository tasks (`benchmarks/suite_e4.py`), full fairness table (`benchmarks/FAIRNESS_e4.md`), pre-flight validation (35/35 pass, `tests/test_suite_e4_preflight.py`), Gate A executed (120 attempts, `results/gate_a/`). Ceiling broken ($C0000 = 58.3\%$, $C1111 = 65.0\%$). |
| **Phase 2** | Main Experiment $E4a$ ($2^{5-1}$ Factorial) | **LOCKED (Pending Gate A Round 2 Review)** | — | 16 cells $\times \ge 5$ runs $\times$ gated tasks; binary logistic/LPM analysis, permutation tests, bootstrap CIs |
| **Phase 3.1**| One-at-a-Time Ablation ($E4b$) | Not Started | — | 8 designs ($B, S_1, S_2, S_4, P_2, P_3, U_2, R_2$) on new gated benchmark |
| **Phase 3.2**| Untested Factor Levels | Not Started | — | $u_3$ (grep), $u_4$ (vector), $u_5$ (graph), $r_3$ (independent critic), $k_3$ (two retries), $s_5$ (tuned book) |
| **Phase 3.3**| $s_5$ Knapsack MIP Construction | Not Started | — | Leave-one-rule-out ablation on tuning tickets; evaluated strictly on held-out tickets |
| **Phase 3.4**| Retry-Feedback Confound Test | Not Started | — | Policy-only vs Policy + visible pytest feedback across factorial subset |
| **Phase 3.5**| Tools Offered vs. Tools Used | Not Started | — | Observational analysis of tool adoption vs performance |
| **Phase 4** | Search & Generalization (RQ3) | Not Started | — | MIP surrogate optimization under token budgets vs baselines and successive halving |
| **Phase 5** | Replication & Robustness | Not Started | — | Cross-model replication, extreme cell fairness check, book-version inversion test |

---

## 2. Gate A Verification Results (120 Attempts, Post G-1 Fix)

Target criteria from `REAL_TEST_REQUIREMENTS.md` Section 1.4:
- **Criterion 1 (Cell 0000 pass rate in [0.20, 0.60]):** **58.3%** (35/60) — **PASSED** (Difficulty calibrated: baseline ceiling is broken, baseline is no longer 95–100%).
- **Criterion 2 (Cell 1111 pass rate in [0.60, 0.95]):** **65.0%** (39/60) — **PASSED**.
- **Criterion 3 (Scaffolding Separation Check):** Observed $\Delta = +6.7\%$ (+4 net passing attempts out of 60).
  - Wilson 95% CIs: $C0000 \in [45.7\%, 69.9\%]$, $C1111 \in [52.4\%, 75.8\%]$ (substantially overlapping).
  - Exact paired sign-flip permutation test: $p = 0.7500$ ($p \gg 0.05$).
  - **Verdict:** Scaffolding superiority is **NOT** statistically supported on this 12-task benchmark. Gate A serves strictly as a **difficulty calibration gate** (ceiling broken), not as evidence that educational scaffolding improves performance.
- **Criterion 4 (Ceiling Persistence Check):** $C0000 = 58.3\% < 85\%$ — **PASSED**.

### Task-by-Task Performance Summary

| Task ID | Task Name | Files | C0000 (Bare) | C1111 (Scaffolded) | Difference ($\Delta$) | Discrimination Class |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **1001** | Invoice totals off by a cent | 5 | 0/5 (0%) | 1/5 (20%) | **+20%** | Separating |
| **1002** | Config overrides lose sibling keys | 4 | 1/5 (20%) | 5/5 (100%) | **+80%** | Separating |
| **1003** | Recurring events skip or repeat days | 3 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1004** | Exported CSV breaks on some customers | 3 | 0/5 (0%) | 0/5 (0%) | +0% | Saturated (Floor) |
| **1005** | Users keep access after being removed | 4 | 0/5 (0%) | 0/5 (0%) | +0% | Saturated (Floor) |
| **1006** | Usage reports disagree with the ledger | 4 | 4/5 (80%) | 0/5 (0%) | **-80%** | Separating (Inversion) |
| **1007** | Shop pipeline: five reported problems | 7 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1008** | Middleware Pipeline Onion Architecture | 5 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1009** | Token Bucket Rate Limiter with Clock | 4 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling post G-1 fix) |
| **1010** | Prioritized Event Dispatcher with Cancel | 4 | 0/5 (0%) | 3/5 (60%) | **+60%** | Separating |
| **1011** | KV Storage Engine with WAL Compaction | 5 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1012** | Distributed Lease & Fencing Token | 4 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |

### Token Economics
- **C0000 Average:** 998 prompt tokens in, 882 candidate tokens out (Total: 1,880 tokens/attempt)
- **C1111 Average:** 7,669 prompt tokens in, 1,458 candidate tokens out (Total: 9,127 tokens/attempt)

---

## 3. Responses to Claude Round 6 Review Items (G-1 through G-4)

### G-1 (Blocking) — Truncation Bug Fix & Re-run of Truncated Attempts
- **Root Cause:** In Gemini 2.5 Flash, the internal thinking budget consumed 15,726 tokens, forcing candidate generation to stop after 654 tokens on Task 1009 (`C0000` runs 1, 2, and 4). Because `stop_reason` returned `"FinishReason.MAX_TOKENS"`, the string check `== "MAX_TOKENS"` did not fire.
- **Harness Fix:**
  1. Configured `types.ThinkingConfig(thinking_budget=2048)` and `types.GenerateContentConfig(max_output_tokens=16384)` in `runner/agent_runner.py`.
  2. Fixed stop reason check to evaluate both `raw_finish.name == "MAX_TOKENS"` and `"MAX_TOKENS" in str(raw_finish)`.
  3. Added explicit recording of `self.last_thoughts_tok` from `usage_metadata.thoughts_token_count`.
  4. Added hermetic unit test `test_max_tokens_truncation_raises_hard_stop` in `tests/test_runner_dry_run.py` verifying that `types.FinishReason.MAX_TOKENS` raises a fatal `RuntimeError`.
- **Rerun Results for Task 1009 (`C0000`):**
  - All 3 truncated attempts were re-run via live API calls (`gemini-2.5-flash`).
  - All 3 completed with `stop_reason = FinishReason.STOP` and passed all hidden tests (`strict = True`).
  - **Before/After Table:**
    | Attempt | Before (Truncated) | After (G-1 Fix) | Tokens Out (Before -> After) | Finish Reason |
    |:---|:---:|:---:|:---:|:---:|
    | `C0000_r1_t1009` | FAIL (cut off at docstring) | **PASS** | 654 -> 1,029 | `FinishReason.STOP` |
    | `C0000_r2_t1009` | FAIL (cut off at docstring) | **PASS** | 654 -> 1,041 | `FinishReason.STOP` |
    | `C0000_r4_t1009` | FAIL (cut off at docstring) | **PASS** | 654 -> 1,038 | `FinishReason.STOP` |
- **Verification:** Re-scanned all 120 rows in `results/gate_a/rows.json`. Exactly 0 rows have `stop_reason != "FinishReason.STOP"` (100% completed cleanly).

### G-2 (Blocking) — Statistical Re-analysis & Removal of Causal Claims
- Script committed: `runner/stat_analysis_gate_a.py`.
- With Task 1009 passing 5/5 in both cells, the net separation is $\Delta = +6.7\%$ ($35/60 \to 39/60$).
- Paired sign-flip permutation test on per-task differences yields $p = 0.7500$ (with 4 non-zero difference tasks: $+0.20, +0.80, -0.80, +0.60$).
- All causal claims ("Strong Separation", "Negative Interaction Discovered", "Scaffolding Superiority") have been removed from documentation and reports. Gate A is accepted strictly as an empirical difficulty calibration gate.

### G-3 (Blocking) — Benchmark Discrimination Profile & Saturated Task Inspection
- **Failure Analysis for Floor Tasks:**
  - **Task 1005 (RBAC ACL):** 5 of 6 hidden tests passed. The sole failure was `test_segment_prefix`: `allowed(g, [("/a/", "bob", "read", "allow")], "bob", "/a/b", "read") is True`. The model split paths on `/` without stripping trailing slashes from the rule prefix `"/a/"`, yielding an empty trailing segment `["", "a", ""]` that failed to prefix-match `["", "a", "b"]`. Hidden tests are reachable (gold reference solution passes 100%).
  - **Task 1004 (CSV IO):** The visible test suite (`test_export.py`) only exercises `export()` and does not test `read_rows()`. The model generated a basic delimiter-split parser for `read_rows()` that passed visible tests but failed hidden tests requiring full RFC 4180 multiline quoted field handling. Hidden tests are reachable (gold reference solution passes 100%).
- **Saturated Tasks Decision (Keep / Drop / Harden for Phase 2):**
  - Out of 12 tasks, 6 are at ceiling (1003, 1007, 1008, 1009, 1011, 1012: 5/5 in both cells), 2 are at floor (1004, 1005: 0/5 in both cells), and 4 are separating (1001: +20%, 1002: +80%, 1006: -80%, 1010: +60%).
  - Running a 16-cell factorial across all 12 tasks would allocate 8/12 (66.7%) of compute budget to uninformative saturated tasks.
  - **Recommendation for Phase 2:**
    - Retain the 4 separating tasks (1001, 1002, 1006, 1010) as core discriminators.
    - Provide a clarifying docstring note on 1004/1005 (e.g. noting trailing slashes in prefix normalization, and adding a visible roundtrip test case for CSV read) to unblock the floor tasks, converting them into active discriminators.
    - Harden ceiling tasks (e.g. 1008, 1009, 1011) with additional concurrency or invariant stress tests, or prune pure ceiling tasks to concentrate Phase 2 runs on high-information clusters.

### G-4 (Blocking) — Inert Factors Diagnosis ($u$ and $k$)
- **Tool Non-Use ($u$):**
  - In Gate A, `tool_used = 0` across all 60 attempts in $C1111$.
  - Diagnosis: `STANDARD_TASK_ENVELOPE_HEADER` placed at the very top commanded: *"Output ONLY the patch in exactly this format... do not write any explanation outside the file blocks"*. This directly contradicted the `=== TOOL: pytest ===` envelope at the bottom.
  - Fix Applied: Defined `TOOL_TASK_ENVELOPE_HEADER` when $u=1$ that explicitly instructs and authorizes interactive test execution before final patch submission: *"You have access to an interactive test execution tool (pytest). You may run tests to inspect and verify behavior before submitting your final patch... When ready to submit, output your final patch in === FILE === blocks."*
- **Retry Inactivity ($k$):**
  - In Gate A, `retries_done = 0` across all attempts because `retry_feedback_mode` defaulted to `"policy_only"`. Because test tampering was zero (`tamper = False` in 120/120 attempts), the policy retry had no opportunity to trigger.
  - Fix Applied: Switched `retry_feedback_mode` default to `"policy_plus_visible_pytest"` in `agent_runner.py` and experiment scripts. When visible pytest fails, the runner feeds back the test failure traceback to the model for exactly one retry step ($k=1$), making factor $k$ active and informative.
