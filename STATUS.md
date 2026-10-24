# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Gate S (Offline Suite, Controls & Pre-Flight Verification — Awaiting Claude Gate S Review)  
**Phase State:** **Gate S Complete & Hermetically Verified (114/114 Preflight Tests Passing; Zero Model Calls Made)**  
**Frozen SHA:** `915711b` (Phase 0/Gate A runner baseline) -> *Gate S Deliverable Commit in Progress*  
**Model Specifications:**  
- **Model ID:** `gemini-2.5-flash` (for upcoming Gate A2 calibration upon Gate S approval)  
- **Sampling Settings:** `temperature=0.0`, `max_output_tokens=16384`, `thinking_budget=2048`  
- **Concurrency:** 6 parallel worker threads with thread-safe file locking  
- **Execution Backend:** Direct Google Gemini API with mandatory startup probe (`startup_self_check`)  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Complete and Verified** | `c81d851` | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, Resolution-V parity, interactive tool calling loop, standardized task envelope, audit trail, 10 hermetic unit tests. Live dry run verified on `gemini-2.5-flash`. |
| **Phase 1** | Difficulty Gate A (Calibration Only) | **Complete (Difficulty Calibrated)** | `915711b` | 12 multi-module tasks (`suite_e4`), 120 live attempts ($C0000=56.7\%$, $C1111=61.7\%$, $p=0.8750$). Established as difficulty calibration only (ceiling broken); per-task effects did not replicate across runs. |
| **Gate S**  | Template Suite $e5$, Controls & Invariants | **Complete (114/114 Verified)** | *Current Commit* | Strictly offline. 28 template-generated instances across 7 families (`benchmarks/suite_e5.py`), `HANDBOOK.md` vs `PLACEBO.md` token balance (761 vs 754, 0.920% diff <= 3%), 2 worked examples (`briefs/P3.md`), full audit table (`benchmarks/FAIRNESS_e5.md`), 114/114 passing preflight tests (`tests/test_suite_e5_preflight.py`). |
| **Gate A2** | Baseline B0 Calibration Run | **LOCKED (Pending Gate S Approval)** | — | Live B0 calibration on `suite_e5` (frozen runner config, >= 10 runs per instance, 280 attempts). Calibrates baseline difficulty without scaffolding bias. |
| **Gate P**  | Formal Pre-Registration | **LOCKED (Pending Gate A2)** | — | Primary hypothesis, instance-clustered permutation tests, theta* selection rule, secondary metrics. |
| **Gate B**  | Tune-Set Factorial ($2^{5-1}$) | **LOCKED (Pending Gate P)** | — | 16 cells $\times \ge 5$ runs on gated tune split. |
| **Held-Out**| Final Confirmation & Multi-Model Replication | **LOCKED** | — | Held-out confirmation and second-model replication as budget allows. |

---

## 2. Gate S Offline Deliverables & Verification Summary

Per Section 8 Addendum v2 of `REAL_TEST_REQUIREMENTS.md`, Gate S establishes the clean-slate benchmark suite, balanced controls, and structural invariants prior to any model inference. All deliverables have been created and verified offline:

### A. Balanced Controls: `briefs/HANDBOOK.md` vs `briefs/PLACEBO.md`
- **Token Accounting (`cl100k_base` / `tiktoken`):**
  - `HANDBOOK.md`: **761 tokens** (10 numbered house rules: banker's rounding, immutability, error types, half-open intervals, trailing slash normalization, stable ordering, safe iteration, injectable clocks, RFC 4180 CSV serialization).
  - `PLACEBO.md`: **754 tokens** (10 corresponding software engineering hygiene rules: formatting, docstrings, variable naming, typing, imports, logging, error messages, dead code, profiling, licensing).
  - **Token Difference:** 7 tokens (**0.920%**, strictly $\le 3.0\%$).
- **Content Purity:** Verified 0 / 9 domain concept overlap; `PLACEBO.md` contains purely general software hygiene rules without task-relevant domain invariants.

### B. Practice Examples: `briefs/P3.md`
- Contains exactly 2 complete worked examples (Ticket $\to$ Root Cause $\to$ Production Patch $\to$ Architectural Rationale).
- Covers `money_rounding` (`calculate_discounted_line` in `billing/discount.py`) and `config_merge` (`merge_tenant_routing` in `routing/config.py`).
- **Isolation:** Uses codebases and function names completely distinct from evaluated tasks 2001–2028 (zero file or function collisions).

### C. Benchmark Suite: `benchmarks/suite_e5.py`
- Total evaluated instances: **28 instances** across **7 bug families** (4 instances per family):
  1. `money_rounding` (Tasks 2001–2004)
  2. `config_merge` (Tasks 2005–2008)
  3. `calendar_recurrence` (Tasks 2009–2012)
  4. `csv_roundtrip` (Tasks 2013–2016)
  5. `permission_prefix` (Tasks 2017–2020)
  6. `event_ordering` (Tasks 2021–2024)
  7. `cache_ttl` (Tasks 2025–2028)
- **Tag Distribution:**
  - `STATED`: **11 instances** (39.3% $\ge 4$)
  - `TAUGHT`: **10 instances** (35.7% $\ge 4$)
  - `DISTRACTOR`: **3 instances** (10.7% $\ge 2$, Tasks 2004, 2008, 2016)
  - `TRANSFER`: **4 instances** (14.3% $\ge 3$, Tasks 2025, 2026, 2027, 2028)
- **Structural Variants:**
  - Hidden Root Cause (outside traceback file): **11 instances (39.3% $\ge 33.3\%$)**
  - Visible-Test-Sensitive (naive fix fails visible test): **11 instances (39.3% $\ge 33.3\%$)**
- **TRANSFER Domain Disjointness:** All TRANSFER tasks belong to `cache_ttl`, completely disjoint from the P3 practice families (`money_rounding` and `config_merge`).

### D. Fairness Documentation: `benchmarks/FAIRNESS_e5.md`
- Complete audit table mapping all 28 instances to their bug family, class tag, visible source / handbook rule citation, hidden root cause flag, visible-test sensitivity flag, and minimal context package (traceback files provided to baseline B0).

### E. Hermetic Pre-Flight Validation Suite: `tests/test_suite_e5_preflight.py`
- Executed via `uv run pytest repo_push/tests/test_suite_e5_preflight.py -v`:
  - `test_unpatched_baseline_fails`: 28/28 PASSED (100% fail hidden tests; 0 false positives).
  - `test_gold_reference_passes`: 28/28 PASSED (100% strict pass; 0 violations, no tamper).
  - `test_mutant1_fails`: 28/28 PASSED (100% fail hidden tests).
  - `test_mutant2_fails`: 28/28 PASSED (100% fail hidden tests).
  - `test_handbook_placebo_token_balance`: PASSED (0.920% difference $\le 3.0\%$).
  - `test_e5_tag_distribution`: PASSED (all structural and class tag invariants satisfied).
  - **Overall Preflight Result:** **114 passed in 382.34s (0 failures)**.

---

## 3. Gate A Difficulty Calibration Summary (Historical / Calibration Reference)

Target criteria from `REAL_TEST_REQUIREMENTS.md` Section 1.4:
- **Criterion 1 (Cell 0000 pass rate in [0.20, 0.60]):** **56.7%** (34/60) — **PASSED** (Baseline difficulty calibrated: ceiling is completely broken; $56.7\% \in [20\%, 60\%]$).
- **Criterion 2 (Cell 1111 pass rate in [0.60, 0.95]):** **61.7%** (37/60) — **PASSED**.
- **Criterion 3 (Scaffolding Separation Check):** Observed $\Delta = +5.0\%$ (+3 net passing attempts out of 60).
  - Wilson 95% CIs: $C0000 \in [44.1\%, 68.4\%]$, $C1111 \in [49.0\%, 72.9\%]$ (substantially overlapping).
  - Exact paired sign-flip permutation test: $p = 0.8750$ ($p \gg 0.05$).
  - **Verdict:** Scaffolding superiority is **NOT** statistically supported on this 12-task benchmark. Gate A serves strictly as a **difficulty calibration gate** (baseline ceiling broken), not as empirical evidence that educational scaffolding improves performance.
- **Criterion 4 (Ceiling Persistence Check):** $C0000 = 56.7\% < 85\%$ — **PASSED**.

### Task-by-Task Performance Summary

| Task ID | Task Name | Files | C0000 (Bare) | C1111 (Scaffolded) | Difference ($\Delta$) | Discrimination Class |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **1001** | Invoice totals off by a cent | 5 | 2/5 (40%) | 1/5 (20%) | **-20%** | Separating |
| **1002** | Config overrides lose sibling keys | 4 | 0/5 (0%) | 5/5 (100%) | **+100%** | Separating |
| **1003** | Recurring events skip or repeat days | 3 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1004** | Exported CSV breaks on some customers | 3 | 2/5 (40%) | 0/5 (0%) | **-40%** | Separating |
| **1005** | Users keep access after being removed | 4 | 0/5 (0%) | 0/5 (0%) | +0% | Saturated (Floor) |
| **1006** | Usage reports disagree with the ledger | 4 | 0/5 (0%) | 1/5 (20%) | **+20%** | Separating |
| **1007** | Shop pipeline: five reported problems | 7 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1008** | Middleware Pipeline Onion Architecture | 5 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1009** | Token Bucket Rate Limiter with Clock | 4 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1010** | Prioritized Event Dispatcher with Cancel | 4 | 0/5 (0%) | 0/5 (0%) | +0% | Saturated (Floor) |
| **1011** | KV Storage Engine with WAL Compaction | 5 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |
| **1012** | Distributed Lease & Fencing Token | 4 | 5/5 (100%) | 5/5 (100%) | +0% | Saturated (Ceiling) |

### Comprehensive Token Accounting (Averaged Per Attempt)
- **C0000 (Bare Baseline):**
  - Prompt tokens in: 981.5
  - Candidate tokens out: 776.0
  - Hidden reasoning (`thoughts_tokens`): 1,531.2
  - **Total Billed Tokens:** **3,288.7 tokens / attempt**
- **C1111 (Full Scaffolding):**
  - Prompt tokens in: 11,855.9
  - Candidate tokens out: 1,636.1
  - Hidden reasoning (`thoughts_tokens`): 5,023.0
  - **Total Billed Tokens:** **18,515.0 tokens / attempt**
- **Token Cost Footprint:** $C1111$ consumes $5.63\times$ more billed tokens per attempt than $C0000$ for a $+5.0\%$ net separation ($p = 0.8750$).

---

## 3. Responses to Claude Round 7 Review Items (H-1 through H-4)

### H-1: Unified Run Configuration & Rerun Provenance
- **Full Rerun Completed:** All 120 Gate A attempts were re-executed from scratch under a single, unified frozen runner configuration stamped with commit SHA `915711b`. Zero attempts were recycled or mixed across different configurations.
- **Superseded Artifacts Preserved:** All previous raw generation files, grades, and rows are preserved intact under `results/gate_a/superseded/` and logged in `DEVIATIONS.md`.
- **Token Accounting:** Every row in `results/gate_a/rows.json` and turn record in `_transcript.json` now includes `thoughts_tokens` (from `usage_metadata.thoughts_token_count`) and `total_billed_tokens`. 100% of rows completed with `stop_reason = FinishReason.STOP`.

### H-2: Formal Pre-Registration of Factors $k$ and $u$ (Choice B)
- **Pre-Registration Decision:** Choice (B) has been formalized and committed in `REAL_TEST_REQUIREMENTS.md`:
  - **Factor $u$ (Interactive In-Turn Test Tool):** Grants real-time workspace pytest execution during the authoring phase across up to 5 turns before patch submission.
  - **Factor $k$ (Post-Submission Feedback Retry):** Implements an automated CI/CD grader check on initial submission; if the attempt modifies protected files or fails visible unit tests, the grader returns the failure traceback for exactly one corrective retry turn ($k_2$).
  - In $u=0, k=1$ cells, agents receive test feedback only upon failure of their initial submission, cleanly separating reactive CI/CD feedback from proactive sandbox exploration.

### H-3: Verified Tool Execution & Symmetric Format Constraints
- **Harmonized Formatting:** `STANDARD_TASK_ENVELOPE_HEADER` and `TOOL_TASK_ENVELOPE_HEADER` now contain identical patch syntax constraints: `"Output ONLY the patch in exactly this format: ... Do not output unchanged files, do not use markdown fences, do not write any explanation outside the file blocks."` Format permissiveness is identical across all cells.
- **Active Tool Use Verified:** With the workflow instruction incorporated into `TOOL_INSTRUCTION_ENVELOPE`, `tool_used = True` in **59 out of 60 attempts (98.3%)** in $C1111$, logging 59 real pytest execution calls with live exit codes and failure tracebacks.

### H-4: Task Fairness vs. Difficulty & Phase 2 Tune/Held-Out Split Plan
- **Fairness vs. Difficulty Confirmation:**
  - **Task 1004 (CSV IO):** The docstring explicitly specifies RFC 4180 quoting rules. Failure to parse multiline quoted fields in `read_rows` was a genuine model deficiency on an unexercised branch. Adding visible round-trip tests would be a difficulty reduction, not an unstated convention fix.
  - **Task 1005 (RBAC ACL):** The docstring states `"/a" covers "/a" and "/a/b" but NOT "/ab"`. It does not explicitly state whether rule prefixes may contain trailing slashes (e.g. `"/a/"`), which led models to fail segment matching when splitting on `/`.
- **Tune / Held-Out Split Plan for Phase 2:**
  - To prevent selection bias and regression-to-the-mean artifacts, the 12 Gate A tasks are designated strictly as the **Tuning / Calibration Suite** ($\mathcal{D}_{\text{tune}}$).
  - Main factorial claims for Phase 2 will be evaluated on a fresh, pre-registered **Held-Out Evaluation Suite** ($\mathcal{D}_{\text{heldout}}$) of 6–8 tasks, gated solely on baseline difficulty ($C0000 \in [15\%, 85\%]$) without prior knowledge of scaffolding separation $\Delta$.
