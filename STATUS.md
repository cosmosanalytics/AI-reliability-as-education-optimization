# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Pilot Calibration Round 2 (Complete; Strict Stop Rule Enforced)  
**Phase State:** **Complete (168 Total Live Attempts Analyzed; All Factor Runs Locked)**  
**Frozen SHA:** *Submitting for Round 14 Review*  
**Model Specifications:**  
- **Model ID:** `gemini-2.5-flash` (for upcoming pilot calibration upon benchmark validation approval)  
- **Sampling Settings:** `temperature=0.0`, `max_output_tokens=16384`, `thinking_budget=2048`  
- **Concurrency:** 6 parallel worker threads with thread-safe file locking  
- **Execution Backend:** Direct Google Gemini API with mandatory startup probe (`startup_self_check`)  

---

## 1. Experimental Campaign Phase State Table

*Terminology Note:* Conforming to standard research protocol:
- **Benchmark validation:** fairness and construct-validity review of the task suite (formerly Gate S).
- **Pilot calibration:** difficulty, ceiling/floor check, run-to-run noise (formerly Gate A / A2).
- **Pre-registration:** hypotheses, statistical tests, $\theta^*$ selection rule, and stopping rules committed before confirmatory run (formerly Gate P).
- **Screening experiment:** 16-cell Resolution-V fractional factorial ($2^{5-1}$) on the tuning tasks (formerly Gate B).
- **Confirmatory study:** held-out task evaluation for primary hypothesis testing.
- **Replication:** confirmatory study on a second model family.
- **Agent harness:** the five factors varied ($s, p, u, r, k$).
- **Evaluation runner:** `runner/agent_runner.py` and `runner/grader.py`.

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Complete and Verified** | `c81d851` | Evaluation runner (`agent_runner.py`), grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, Resolution-V parity, interactive tool loop, standardized task envelope, audit trail, 10 hermetic unit tests. Live dry run verified on `gemini-2.5-flash`. |
| **Pilot Calibration (suite_e4)** | Difficulty Calibration Only | **Complete (Difficulty Calibrated)** | `915711b` | 12 multi-module tasks (`suite_e4`), 120 live attempts ($C0000=56.7\%$, $C1111=61.7\%$, $p=0.8750$). Established as difficulty calibration only (ceiling broken); per-task effects did not replicate across runs. |
| **Benchmark Validation (suite_e5)** | Modular Task Suite $e5$, Invariants & Preflight | **Complete (146/146 Verified)** | `e669a2e` | Strictly offline. 28 modular instances across 7 families (`benchmarks/suite_e5.py`), `HANDBOOK.md` vs `PLACEBO.md` token balance (761 vs 754, 0.920% diff $\le 3\%$), 2 worked examples (`briefs/P3.md`), per-assertion audit table (`benchmarks/FAIRNESS_e5.md`), class-stratified split (`benchmarks/splits_e5.json`: 15 Tune, 13 Held-Out), 146/146 passing preflight tests (`tests/test_suite_e5_preflight.py`). S-1..S-6, B1..B4, and C1..C2 resolved. |
| **Pilot Calibration (suite_e5)** | Baseline B0 Calibration Run | **Complete (Audited & Reported)** | *Current Commit* | Live re-run of B0 calibration on `suite_e5` under redefined B0 (full repo in context, E1) across 28 tasks: 1 run at T=0.0 (28 att, 75.0% pass) + 5 runs at T=0.7 (140 att, 69.3% pass, ICC=0.818). 8 TAUGHT tasks reclassified to STATED per C2 rule (>70% at T=0.7). Exactly 1 held-out TAUGHT remains (2003). 6 tasks in calibrated band (15-85%); E3 contingency rule triggered. All factor runs strictly locked. |
| **Pre-Registration** | Formal Pre-Registration Document | **LOCKED (Awaiting Round 13 Review)** | — | Primary hypothesis ($\Delta_{\text{TAUGHT}} > 0$), instance-clustered permutation tests, $\theta^*$ selection rule, C2 baseline-solvability relabel rule, and stopping rules to be committed before screening experiment. |
| **Screening Experiment** | Tune-Set Factorial ($2^{5-1}$) | **LOCKED (Pending Pre-Registration)** | — | 16 cells $\times \ge 5$ runs on the 15 tune tasks (`benchmarks/splits_e5.json`). |
| **Confirmatory Study** | Held-Out Confirmation & Multi-Model Replication | **LOCKED** | — | Confirmatory evaluation on 13 held-out tasks (4 TAUGHT, 3 STATED, 2 DISTRACTOR, 4 TRANSFER) and second-model replication as budget allows. |

---

## 2. Benchmark Validation Resolution: S-1..S-6, B1..B4, and C1..C2 Fixes

In response to Round 9, Round 10, and Round 11 reviews, all construct-validity requirements have been fully addressed offline with zero model calls:

### C1: Class-Stratified Partition & Confirmatory Statistical Power
- **Root Cause:** The previous partition was stratified solely by family, resulting in an artifact where the Held-Out set contained only 1 `TAUGHT` task (and 4 `STATED`), rendering the confirmatory test of the primary research hypothesis anecdotal.
- **Resolution:** Replaced family-stride selection with strict class-stratified sampling across all 28 tasks committed in `benchmarks/splits_e5.json`:
  - **Tune Set (15 instances = 53.6%):** 2001, 2002, 2005, 2006, 2008, 2009, 2012, 2013, 2014, 2017, 2018, 2020, 2021, 2023, 2024.
    - Class Composition: **7 TAUGHT**, **7 STATED**, **1 DISTRACTOR** (2008), 0 TRANSFER.
    - Guarantees $\ge 4$ tasks per class needed to estimate factor main effects and interactions in the Screening Experiment ($2^{5-1}$).
  - **Held-Out Set (13 instances = 46.4%):** 2003, 2004, 2007, 2010, 2011, 2015, 2016, 2019, 2022, 2025, 2026, 2027, 2028.
    - Class Composition: **4 TAUGHT**, **3 STATED**, **2 DISTRACTOR** (2004, 2016), **4 TRANSFER** (100% held out).
    - Statistical Power: 4 distinct TAUGHT tasks (2003, 2010, 2015, 2022) across 4 different families provide robust statistical power for the primary confirmatory hypothesis ($\Delta_{\text{TAUGHT}} = \bar{Y}_{\theta^*} - \bar{Y}_0 > 0$).
  - Added CI invariant check in `test_splits_e5_stratification` enforcing per-class minimums for both sets.

### C2: Pre-Registration Relabel Rule (Objective Baseline Solvability)
- **Criterion:** To prevent circularity or subjective label bias, class labels will not be trusted on intuition alone.
- **Rule Committed:** During Pilot Calibration ($B_0$, repeated runs on the tune set), any task currently designated `TAUGHT` where the empirical baseline pass rate exceeds **70.0%** will be automatically reclassified as `STATED` prior to the Screening Experiment and dropped from the confirmatory `TAUGHT` count.
- Class membership is governed strictly by empirical baseline solvability before factorial screening begins, and NEVER adjusted post-hoc based on handbook gain.

### B1: Design Word Leakage Elimination
- Replaced all test IDs, function names, and filenames containing design tags (`taught`, `stated`, `distractor`, `transfer`, `visible_sensitive`, `_visible`, `_hidden`) with neutral domain-specific names (`test_case_1` style or domain-neutral function names such as `test_quote_escaping`, `test_sibling_path_boundary`).
- Test filenames renamed from `*_hidden.py` to neutral `test_*_cases.py`.
- Added automated preflight test `test_no_design_words_in_tests_or_traces` scanning visible tests, hidden tests, and failure traceback excerpts across all 28 tasks to ensure zero leakage of design vocabulary to the model.

### B2: Symptom-Only Traceback Assertions & Solvability
- Removed rule-revealing error messages (e.g. "embedded quote not escaped via RFC 4180 standard", "sibling path permitted by unsegmented prefix match", naming banker's rounding) from assertion statements and tracebacks.
- All failure tracebacks strictly exhibit pure value mismatches (`AssertionError: assert actual == expected`), preventing any prompt leakage that would compromise the `TAUGHT` class construct validity.

### B3: Tune / Held-Out Partition Rebalance (18 Tune / 10 Held-Out)
- Rebalanced task partitioning from 12/16 to **18 Tune (64.3%) / 10 Held-Out (35.7%)** committed in `benchmarks/splits_e5.json`:
  - **Tune Tasks (18):** 2001, 2002, 2004, 2005, 2006, 2008, 2009, 2010, 2012, 2013, 2014, 2016, 2017, 2018, 2020, 2021, 2022, 2024. Includes 2 `DISTRACTOR` tasks (2004, 2008) to ensure screening across all primary task modalities.
  - **Held-Out Tasks (10):** 2003, 2007, 2011, 2015, 2019, 2023, 2025, 2026, 2027, 2028.
  - Stratified across all 7 families: 100% of `TRANSFER` tasks (Family 7: `cache_ttl`, Tasks 2025–2028) are held out for confirmatory domain generalization evaluation.
  - Preflight verification test `test_splits_e5_stratification` confirms exact counts and stratification rules.

### B4: Root-Cause Reachability & Elimination of Decoy Files
- Verified that all helper/support files in every task repository are actively imported and invoked along the real call graph (e.g. input validators, data models, formatters). Decoys = 0 across all 28 tasks.
- For all 12 Hidden Root Cause tasks, the root-cause file is strictly imported by the traceback entrypoint file.
- Added automated preflight tests `test_root_cause_reachability` and `test_zero_unimported_decoy_files` enforcing 100% import reachability.

### S-1: Hint Comment Elimination & Invariant Enforcement
- Removed every `# BUG:`, `# FIX:`, `# TODO:`, and `# HACK:` comment across all 28 task repositories.
- Implemented automated preflight test `test_no_hint_comments_in_provided_files` parameterized across all 28 tasks asserting zero matches for `/#\s*(BUG|FIX|TODO|HACK)/i` in any provided non-test source file.

### S-2: Realistic Codebases & Symptom-Level Tickets
- Expanded repositories from minimal stubs to realistic modular systems (40–120 non-test lines across 2–4 files per task).
- All tickets are written strictly as user-visible incident reports (e.g. billing discrepancies, cache staleness under concurrency, CSV export corruption, privilege bypass), completely free of root-cause disclosures.
- Sanitized all traceback outputs to eliminate expected value giveaways.

### S-3: Rigorous Audit of TAUGHT Class
- Re-audited all tasks to ensure strict construct validity:
  - **11 true `TAUGHT` tasks** (Target $\ge 8$: 2002, 2003, 2006, 2010, 2012, 2014, 2015, 2018, 2020, 2022, 2024). In every TAUGHT task, hidden assertions enforce house handbook conventions (e.g. banker's rounding on half-cents, shallow vs deep immutability, half-open interval boundaries, RFC-4180 quote doubling, prefix trailing slash normalization, stable sequence tie-breaking) against plausible competing alternatives that models would naturally choose, and neither the docstrings nor tickets reveal the rule.
  - **10 `STATED` tasks**: the convention or specification is explicitly documented in the docstring or visible interface.
  - **3 `DISTRACTOR` tasks** (2004, 2008, 2016): handbook mentions a rule or principle, but the task requires the opposite or a local exception clearly noted in the repo context.
  - **4 `TRANSFER` tasks** (2025, 2026, 2027, 2028): testing generalisation to the cache domain where the handbook provides general architectural principles without an explicit rule recipe.

### S-4: Per-Assertion Fairness Table (`benchmarks/FAIRNESS_e5.md`)
- Authored a comprehensive per-assertion audit table mapping every hidden assertion to:
  - Task ID & Bug Family
  - Assertion Name
  - Visible Source (ticket sentence / docstring / handbook rule)
  - Derivable Without Handbook (Y/N)
  - Class Tag (`TAUGHT`, `STATED`, `DISTRACTOR`, `TRANSFER`)
  - Hidden Root Cause Flag
  - Root Cause Only With Exploration Flag
  - Measured Baseline Pass Rate (Pilot Calibration) column (stamped `Pending Pilot Calibration`)

### S-5: Committed Tune / Held-Out Partition (`benchmarks/splits_e5.json`)
- Partitioned into 18 Tune / 10 Held-Out, committed prior to any model execution.

### S-6: Root-Cause Exploration & Factor $u$ Definition
- For all 12 Hidden Root Cause tasks (42.9%), the defect resides outside the traceback file. A symptom-level patch in the traceback file fails core module assertions.
- All 12 tasks are tagged `root_cause_only_with_exploration = True`.
- Factor $u$ is explicitly defined and evaluated as "repository exploration + test running".

---

## 3. Modular Architecture & Preflight Test Status

- **Modular Generator Architecture:** Decomposed into dedicated modules in `runner/`:
  - `runner/family1_money.py` (Tasks 2001–2004)
  - `runner/family2_config.py` (Tasks 2005–2008)
  - `runner/family3_calendar.py` (Tasks 2009–2012)
  - `runner/family4_csv.py` (Tasks 2013–2016)
  - `runner/family5_permission.py` (Tasks 2017–2020)
  - `runner/family6_ordering.py` (Tasks 2021–2024)
  - `runner/family7_cache.py` (Tasks 2025–2028)
  - Orchestrated deterministically by `runner/build_complete_suite_e5.py`.
- **Preflight Test Results (`tests/test_suite_e5_preflight.py`):**
  - `test_unpatched_baseline_fails`: 28/28 PASSED (100% failure rate; 0 false positives).
  - `test_gold_reference_passes`: 28/28 PASSED (100% strict pass; 0 violations).
  - `test_mutant1_fails`: 28/28 PASSED (100% failure rate).
  - `test_mutant2_fails`: 28/28 PASSED (100% failure rate).
  - `test_no_hint_comments_in_provided_files`: 28/28 PASSED (0 hint regex matches).
  - `test_handbook_placebo_token_balance`: PASSED (0.920% difference $\le 3.0\%$).
  - `test_e5_tag_distribution`: PASSED (all structural and class tag invariants satisfied).
  - `test_splits_e5_stratification`: PASSED (class-stratified partition: Held-out TAUGHT >= 4, STATED >= 3, DISTRACTOR >= 2, TRANSFER == 4; Tune TAUGHT >= 4, STATED >= 4, DISTRACTOR >= 1, TRANSFER == 0).
  - `test_no_design_words_in_tests_or_traces`: PASSED (zero design words in visible tests, hidden tests, or tracebacks).
  - `test_root_cause_reachability`: PASSED (root cause file imported by entrypoint in all 12 HRC tasks).
  - `test_zero_unimported_decoy_files`: PASSED (all non-test files actively called on execution path; decoys = 0).
  - **Total:** **146 / 146 passed (100%)**.

---

## 4. Pilot Calibration on suite_e5 (Baseline B0 Empirical Findings)

- **Total Attempts:** 140 / 140 (28 tasks $\times$ 5 runs, `gemini-2.5-flash`, `temperature=0.0`, single call B0).
- **Overall Strict Pass Rate:** 62 / 140 (**44.3%**, Wilson 95% CI: [36.3%, 52.6%]).
  - **Tune Split (15 tasks):** 37 / 75 (**49.3%**, Wilson [38.3%, 60.4%]).
  - **Held-Out Split (13 tasks):** 25 / 65 (**38.5%**, Wilson [27.6%, 50.6%]).
- **By Task Class:**
  - `STATED`: 32 / 50 (**64.0%**, Wilson [50.1%, 75.9%]).
  - `TAUGHT`: 15 / 55 (**27.3%**, Wilson [17.3%, 40.2%]).
  - `DISTRACTOR`: 5 / 15 (**33.3%**, Wilson [15.2%, 58.3%]).
  - `TRANSFER`: 10 / 20 (**50.0%**, Wilson [29.9%, 70.1%]).
- **Noise Analysis:**
  - Between-task variance: `0.2470`
  - Mean within-task variance across repeats: `0.0086`
  - Intraclass Correlation (ICC): **`0.966`** (96.6% between tasks, 3.4% run-to-run noise).
  - Recommended runs per cell/task for 15-pt diff at 80% power: **$n \ge 6$**.
- **C2 Pre-Registered Relabeling Audit:**
  - Tasks exceeding 70% baseline solvability: **Task 2014** (100%), **Task 2018** (100%), **Task 2022** (100%).
  - Action: Tasks 2014, 2018, 2022 automatically reclassified from `TAUGHT` to `STATED`.
  - Resulting Held-Out `TAUGHT` count: **3 tasks** (2003, 2010, 2015) $\ge 3$ threshold -> **CONFIRMATORY_VALID**.
- **Execution Integrity:** 0 truncations, 0 API errors, 0 retries, 0 protected file modifications.
- **Resource Usage:** 284,629 billed tokens; total cost = **$0.0725 USD**.
- **Report & Raw Logs:** [`PILOT_CALIBRATION_REPORT.md`](file:///c:/Users/richa/ai-engineering/repo_push/PILOT_CALIBRATION_REPORT.md) and [`results/pilot_calibration/rows.jsonl`](file:///c:/Users/richa/ai-engineering/repo_push/results/pilot_calibration/rows.jsonl).

---

## 5. Historical Reference: Pilot Calibration on suite_e4 (Difficulty Calibration Only)

- $C0000$: 34/60 (56.7%, Wilson [44.1%, 68.4%]). Baseline ceiling broken ($56.7\% \in [20\%, 60\%]$).
- $C1111$: 37/60 (61.7%, Wilson [49.0%, 72.9%]).
- $\Delta = +5.0\%$ (+3 net passes out of 60 attempts). Exact paired sign-flip permutation test: $p = 0.8750$.
- Established strictly as difficulty calibration; per-task effects did not replicate across runs.
