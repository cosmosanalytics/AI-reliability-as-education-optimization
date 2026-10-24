# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Phase 0 (Infrastructure Revision — Round 3 Review Complete)  
**Phase State:** **Pushed, under review** (Fixes for Items 1–11 committed; ready for Claude Gate review)  
**Frozen SHA:** None (Freezing scheduled at conclusion of Phase 1 / Gate A)  
**Model Specifications:**  
- **Model ID:** `claude-3-7-sonnet-20250219` (primary target) / `claude-3-5-sonnet-20241022` / `gpt-4o`  
- **Sampling Settings:** `temperature=0.0`, `max_tokens=4096`  
- **Randomization Seed:** `42` (logged in `schedule_order.json` and rows)  
- **Execution Backend:** Pluggable direct API (`anthropic`, `openai`, `gemini`) with mandatory startup probe (`verify_backend`) and zero mock fallbacks  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Pushed, under review** | *Current* | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, retry parity fix, interactive tool calling loop, standardized task envelope, audit trail, unit tests |
| **Phase 1** | New Benchmark & Difficulty Gate | Not Started | — | Target 12 multi-module tasks, fairness tables (`FAIRNESS_<suite>.md`), pre-flight validators, Gate A verification (Cells 0000 vs 1111) |
| **Phase 2** | Main Experiment $E4a$ ($2^{5-1}$ Factorial) | Not Started | — | 16 cells $\times \ge 5$ runs $\times$ gated tasks; binary logistic/LPM analysis, permutation tests, bootstrap CIs |
| **Phase 3.1**| One-at-a-Time Ablation ($E4b$) | Not Started | — | 8 designs ($B, S_1, S_2, S_4, P_2, P_3, U_2, R_2$) on new gated benchmark |
| **Phase 3.2**| Untested Factor Levels | Not Started | — | $u_3$ (grep), $u_4$ (vector), $u_5$ (graph), $r_3$ (independent critic), $k_3$ (two retries), $s_5$ (tuned book) |
| **Phase 3.3**| $s_5$ Knapsack MIP Construction | Not Started | — | Leave-one-rule-out ablation on tuning tickets; evaluated strictly on held-out tickets |
| **Phase 3.4**| Retry-Feedback Confound Test | Not Started | — | Policy-only vs Policy + visible pytest feedback across factorial subset |
| **Phase 3.5**| Tools Offered vs. Tools Used | Not Started | — | Observational analysis of tool adoption vs performance |
| **Phase 4** | Search & Generalization (RQ3) | Not Started | — | MIP surrogate optimization under token budgets vs baselines and successive halving |
| **Phase 5** | Replication & Robustness | Not Started | — | Cross-model replication, extreme cell fairness check, book-version inversion test |

---

## 2. Responses to Claude Review Items (Round 3)

- **Item 1 (Blocking) - Silent mock fallback removed:** Fixed in `runner/agent_runner.py`. The canned response fallback was completely deleted. The runner now raises a fatal `RuntimeError` if no backend is available or if an API call fails. A mandatory `startup_self_check()` runs before any experiment.
- **Item 2 (Blocking) - Retry factor parity ($k = s \cdot p \cdot u \cdot r$):** Fixed in `runner/agent_runner.py`. Uses $\pm 1$ sign parity ($k=1$ iff $(s+p+u+r) \% 2 == 0$). Unit tests in `tests/test_factorial_design.py` verify 8 cells with $k=1$, 8 cells with $k=0$, and strict Resolution-V orthogonality across all main effects and 2FIs.
- **Item 3 (Blocking) - Missing output-format instruction envelope:** Fixed. Defined `STANDARD_TASK_ENVELOPE_HEADER` and prepended it to every ticket prompt across all cells, decoupling format knowledge from the factor briefs. Documented in `briefs/DIFF.md`.
- **Item 4 (Blocking) - Real interactive tool use:** Fixed. Replaced forced one-time pytest with an interactive tool loop (`=== TOOL: pytest ===`). Agent chooses whether, when, and how many times to call tests. Stale `/tmp/claude-0` paths removed from `briefs/U2.md` and all $u=1$ cell briefs. `tool_used` and `tool_call_count` derive strictly from actual tool invocations.
- **Item 5 (Blocking) - Review step prompt & Metric definitions:** Fixed. Review prompt explicitly instructs: `"Reply with your complete final patch in the required === FILE: path === ... === END === block format."` Defined `attempt1_strict` (pre-review/pre-retry), `post_review_strict`, and `final_strict`.
- **Item 6 - Full audit trail:** Fixed. Added saving of every turn (`turn{t}_prompt.txt`, `turn{t}_resp.txt`, `tool_log.json`, `grade_attempt1.json`, `grade_post_review.json`, `grade_final.json`, `transcript.json`).
- **Item 7 & 8 - Metadata & Models:** Fixed. Every row records `frozen_commit_sha`, `backend`, `model_id`, `temperature`, `brief_sha256`, and provider `response_id`.
- **Item 9 - Repo hygiene:** Fixed. Created `.gitignore` and removed cached `.pyc` files from git index.
- **Item 10 - RNG seed & Dry run:** Fixed. Seed `42` logged; added `tests/test_runner_dry_run.py` (7/7 tests passing).
- **Item 11 - Timestamps & Timezone:** Fixed. Documented UTC (`Z`) convention in `DEVIATIONS.md` (UTC = EDT + 4 hours).
