# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Benchmark Validation (`suite_e5` Offline Suite, Invariants & Fairness Review — Awaiting Claude Round 10 Review)  
**Phase State:** **Benchmark Validation Complete & Hermetically Verified (143/143 Preflight Tests Passing; Zero Model Calls Made)**  
**Frozen SHA:** `915711b` (Baseline evaluation runner / pilot calibration) -> *Benchmark Validation Fixes Commit in Progress*  
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
| **Benchmark Validation (suite_e5)** | Modular Task Suite $e5$, Invariants & Preflight | **Complete (143/143 Verified)** | *Current Commit* | Strictly offline. 28 modular instances across 7 families (`benchmarks/suite_e5.py`), `HANDBOOK.md` vs `PLACEBO.md` token balance (761 vs 754, 0.920% diff $\le 3\%$), 2 worked examples (`briefs/P3.md`), per-assertion audit table (`benchmarks/FAIRNESS_e5.md`), tune/held-out split (`benchmarks/splits_e5.json`), 143/143 passing preflight tests (`tests/test_suite_e5_preflight.py`). S-1..S-6 resolved. |
| **Pilot Calibration (suite_e5)** | Baseline B0 Calibration Run | **LOCKED (Pending Benchmark Validation Approval)** | — | Live B0 calibration on `suite_e5` (frozen runner config, $\ge 10$ runs per instance on tune split). Calibrates baseline difficulty without scaffolding bias. Zero model calls until validation passes. |
| **Pre-Registration** | Formal Pre-Registration Document | **LOCKED (Pending Pilot Calibration)** | — | Primary hypothesis, instance-clustered permutation tests, $\theta^*$ selection rule, secondary metrics committed before screening experiment. |
| **Screening Experiment** | Tune-Set Factorial ($2^{5-1}$) | **LOCKED (Pending Pre-Registration)** | — | 16 cells $\times \ge 5$ runs on the 12 tune tasks (`benchmarks/splits_e5.json`). |
| **Confirmatory Study** | Held-Out Confirmation & Multi-Model Replication | **LOCKED** | — | Confirmatory evaluation on 16 held-out tasks and second-model replication as budget allows. |

---

## 2. Benchmark Validation Resolution: S-1 through S-6 Fixes

In response to Round 9 review, all six blocking construct-validity requirements have been fully addressed offline with zero model calls:

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

### S-5: Committed Tune / Held-Out Partition (`benchmarks/splits_e5.json`)
- Partitioned the 28 tasks into:
  - **12 Tune Tasks** (Screening Experiment): 2001, 2002, 2005, 2006, 2009, 2010, 2013, 2014, 2017, 2018, 2021, 2022.
  - **16 Held-Out Tasks** (Confirmatory Study): 2003, 2004, 2007, 2008, 2011, 2012, 2015, 2016, 2019, 2020, 2023, 2024, 2025, 2026, 2027, 2028.
- Partition is stratified by bug family and class tag, with 100% of `TRANSFER` tasks (2025–2028) held out for confirmatory testing.
- Committed prior to any model execution.

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
  - `test_tune_heldout_split_invariants`: PASSED (tune/held-out stratification and TRANSFER hold-out confirmed).
  - **Total:** **143 / 143 passed (100%)**.

---

## 4. Historical Reference: Pilot Calibration on suite_e4 (Difficulty Calibration Only)

- $C0000$: 34/60 (56.7%, Wilson [44.1%, 68.4%]). Baseline ceiling broken ($56.7\% \in [20\%, 60\%]$).
- $C1111$: 37/60 (61.7%, Wilson [49.0%, 72.9%]).
- $\Delta = +5.0\%$ (+3 net passes out of 60 attempts). Exact paired sign-flip permutation test: $p = 0.8750$.
- Established strictly as difficulty calibration; per-task effects did not replicate across runs.
