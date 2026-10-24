# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Phase 0 (Infrastructure Complete & Verified — Ready for Phase 1)  
**Phase State:** **Complete and Verified**  
**Frozen SHA:** None (Freezing scheduled at conclusion of Phase 1 / Gate A)  
**Model Specifications:**  
- **Model ID:** `gemini-2.5-flash` (tested and verified in live dry run); support configured for `claude-3-7-sonnet-20250219`, `gpt-4o`, `gemini-2.5-flash`  
- **Sampling Settings:** `temperature=0.0`, `max_tokens=16384`  
- **Stop Reason Verification:** `stop_reason` recorded per turn; `max_tokens` / `length` truncations raise a fatal `RuntimeError` and are never silently graded (R4-B)  
- **Randomization Seed:** `42` (logged in `schedule_order.json` and rows)  
- **Execution Backend:** Pluggable direct API (`gemini`, `anthropic`, `openai`) with mandatory live startup probe (`startup_self_check`) and zero mock fallbacks  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Complete and Verified** | *Current* | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, Resolution-V parity, interactive tool calling loop, standardized task envelope, audit trail, 10 hermetic unit tests. Live dry run executed natively against Google Gemini API (`gemini-2.5-flash`) across cells `C0000`, `C1111`, `C0010`, `C0001` with complete raw audit files in `results/dry_run/`. |
| **Phase 1** | New Benchmark & Difficulty Gate | In Progress | — | Target 12 multi-module tasks, fairness tables (`FAIRNESS_<suite>.md`), pre-flight validators, Gate A verification (Cells 0000 vs 1111) |
| **Phase 2** | Main Experiment $E4a$ ($2^{5-1}$ Factorial) | Not Started | — | 16 cells $\times \ge 5$ runs $\times$ gated tasks; binary logistic/LPM analysis, permutation tests, bootstrap CIs |
| **Phase 3.1**| One-at-a-Time Ablation ($E4b$) | Not Started | — | 8 designs ($B, S_1, S_2, S_4, P_2, P_3, U_2, R_2$) on new gated benchmark |
| **Phase 3.2**| Untested Factor Levels | Not Started | — | $u_3$ (grep), $u_4$ (vector), $u_5$ (graph), $r_3$ (independent critic), $k_3$ (two retries), $s_5$ (tuned book) |
| **Phase 3.3**| $s_5$ Knapsack MIP Construction | Not Started | — | Leave-one-rule-out ablation on tuning tickets; evaluated strictly on held-out tickets |
| **Phase 3.4**| Retry-Feedback Confound Test | Not Started | — | Policy-only vs Policy + visible pytest feedback across factorial subset |
| **Phase 3.5**| Tools Offered vs. Tools Used | Not Started | — | Observational analysis of tool adoption vs performance |
| **Phase 4** | Search & Generalization (RQ3) | Not Started | — | MIP surrogate optimization under token budgets vs baselines and successive halving |
| **Phase 5** | Replication & Robustness | Not Started | — | Cross-model replication, extreme cell fairness check, book-version inversion test |

---

## 2. Responses to Claude Review Items (Round 4)

- **R4-A (Blocking) - Real-model dry run committed:** Executed 1 ticket (Ticket 2, mutable default argument) across 4 cells (`C0000`, `C1111`, `C0010`, `C0001`) via `runner/agent_runner.py` directly against the Google Gemini API (`gemini-2.5-flash`). All turn prompts/responses, tool logs, grades, `schedule_order.json`, and `rows.json` written directly by the runner under `results/dry_run/`.
  - Self-check probe line: `Startup self-check PASSED: response_id=F_rcaq3OL6OtuMYP3sC-qAs, stop_reason=FinishReason.STOP, tokens=(28 in, 2 out)`.
  - Cell token counts & response IDs:
    - `C0010`: tokens_in=561, tokens_out=138, response_id=`GPrcas-ZHdmZo_UP1fi4oQM`, finish_reason=`FinishReason.STOP`.
    - `C0001`: tokens_in=1080, tokens_out=276, response_id=`KPrcasSgIcOgytMPnujTqAs`, finish_reason=`FinishReason.STOP` (turn 1 + review turn 2).
    - `C1111`: tokens_in=5811, tokens_out=278, response_id=`O_rcaufpB7mqxdIP5MHxiAw`, finish_reason=`FinishReason.STOP` (turn 1 + review turn 2 with full book brief).
    - `C0000`: tokens_in=334, tokens_out=139, response_id=`RvrcaoC6DuGOytMPht7YmAI`, finish_reason=`FinishReason.STOP`.
- **R4-B (Blocking) - `max_tokens` raised & `stop_reason` checked:** Raised `max_tokens` to `16384` across all backends. Added explicit check on `stop_reason`: any truncation (`max_tokens`, `length`, `MAX_TOKENS`) raises a fatal `RuntimeError` and is excluded from silent grading.
- **R4-C (Blocking) - Stale path in `briefs/P2.md`:** Fixed. Rewrote `briefs/P2.md` to remove `/tmp/claude-0/...` and replaced with an in-context review step. Added CI test `test_no_tmp_paths_in_briefs` asserting 0 `/tmp` paths across all briefs.
- **R4-D (Non-blocking) - Tool loop exit & final patch comparison:** Added forced submission turn if `max_tool_turns` is reached while a tool block is present; records `tool_budget_exhausted` and `patch_differs_from_tool_test`.
- **R4-E (Non-blocking) - Safe tool arguments:** Sanitized pytest arguments in `ToolSandbox.run_pytest_command()`: rejects CLI flags (`-`) and path traversals (`..`), restricting execution to relative visible test paths.
- **R4-F (Non-blocking) - Single retry for $k_2$:** Restricted retry loop for $k=1$ to exactly one attempt (`retry_num in [1]`). Two retries ($k_3$) is reserved for Phase 3.2.
- **R4-G (Non-blocking) - Hermetic tests & scripted backend test:** Made token counting lazy with an offline fallback so `test_no_silent_mock_fallback` runs without network; added `test_run_single_attempt_full_flow` using a scripted test probe backend in `tests/test_runner_dry_run.py`. All 10 unit tests pass hermetically.
- **R4-H (Minor) - Anthropic / Gemini turn formatting:** Anthropic handler concatenates all text blocks; Gemini multi-turn role flattening noted in `DEVIATIONS.md`.
- **R4-I - Verification:** Confirmed UTC timestamping and local tiktoken BPE token counts.
