# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Phase 1 (Difficulty Gate A Evaluated under Unified Frozen Config — Awaiting Round 3 Review)  
**Phase State:** **Difficulty Gate A Evaluated (Ceiling Broken: C0000 = 56.7% ∈ [20%, 60%]; Scaffolding Gain Not Statistically Significant, p = 0.8750)**  
**Frozen SHA:** `915711b` (unified runner configuration frozen; 100% of Gate A rows generated under this exact SHA)  
**Model Specifications:**  
- **Model ID:** `gemini-2.5-flash`  
- **Sampling Settings:** `temperature=0.0`, `max_output_tokens=16384`, `thinking_budget=2048`  
- **Concurrency:** 6 parallel worker threads with thread-safe file locking  
- **Stop Reason Verification:** `stop_reason` recorded per turn; 120/120 attempts completed cleanly with `FinishReason.STOP` (0 truncated rows)  
- **Interactive Tool Execution:** 59/60 attempts in $C1111$ actively executed the tool runner (`tool_used=True`, 59 total pytest tool calls logged)  
- **Randomization Seed:** `42` (logged in `schedule_order.json` and `rows.json`)  
- **Execution Backend:** Direct Google Gemini API with mandatory startup probe (`startup_self_check`)  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Complete and Verified** | `c81d851` | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, Resolution-V parity, interactive tool calling loop, standardized task envelope, audit trail, 10 hermetic unit tests. Live dry run verified on `gemini-2.5-flash`. |
| **Phase 1** | New Benchmark & Difficulty Gate | **Complete (Re-run under Unified Frozen Config)** | `915711b` / *Current* | 12 multi-module repository tasks (`benchmarks/suite_e4.py`), full fairness table (`benchmarks/FAIRNESS_e4.md`), pre-flight validation (35/35 pass, `tests/test_suite_e4_preflight.py`), Gate A executed (120 attempts, `results/gate_a/`). Baseline ceiling broken ($C0000 = 56.7\% \in [20\%, 60\%]$). |
| **Phase 2** | Main Experiment $E4a$ ($2^{5-1}$ Factorial) | **LOCKED (Pending Gate A Approval & Pre-Registration Review)** | — | 16 cells $\times \ge 5$ runs $\times$ gated tasks; binary logistic/LPM analysis, permutation tests, bootstrap CIs |
| **Phase 3.1**| One-at-a-Time Ablation ($E4b$) | Not Started | — | 8 designs ($B, S_1, S_2, S_4, P_2, P_3, U_2, R_2$) on new gated benchmark |
| **Phase 3.2**| Untested Factor Levels | Not Started | — | $u_3$ (grep), $u_4$ (vector), $u_5$ (graph), $r_3$ (independent critic), $k_3$ (two retries), $s_5$ (tuned book) |
| **Phase 3.3**| $s_5$ Knapsack MIP Construction | Not Started | — | Leave-one-rule-out ablation on tuning tickets; evaluated strictly on held-out tickets |
| **Phase 3.4**| Retry-Feedback Confound Test | Not Started | — | Policy-only vs Policy + visible pytest feedback across factorial subset |
| **Phase 3.5**| Tools Offered vs. Tools Used | Not Started | — | Observational analysis of tool adoption vs performance |
| **Phase 4** | Search & Generalization (RQ3) | Not Started | — | MIP surrogate optimization under token budgets vs baselines and successive halving |
| **Phase 5** | Replication & Robustness | Not Started | — | Cross-model replication, extreme cell fairness check, book-version inversion test |

---

## 2. Gate A Verification Results (120 Fresh Attempts under SHA `915711b`)

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
