# Project Status & Execution Tracker (`STATUS.md`)

**Current Phase:** Phase 0 (Infrastructure Complete) -> Ready for Phase 1 (Benchmark Design & Difficulty Gate)  
**Frozen SHA:** None (Freezing scheduled at conclusion of Phase 1 / Gate A)  
**Model Specifications:**  
- **Model ID:** `claude-3-5-sonnet-20241022` (primary); historical pilot recorded as *"Claude Sonnet subagents (exact version not recorded)"*  
- **Sampling Settings:** `temperature=0.0`, `max_tokens=4096`  
- **Harness Platform:** Antigravity Execution Environment with Sandboxed Subagent Isolation  

---

## 1. Phase Execution State Table

| Phase | Description | State | Commit SHA | Notes / Deliverables |
|:---|:---|:---:|:---:|:---|
| **Phase 0** | Infrastructure & Protocol Setup | **Pushed** | *Current* | Runner (`agent_runner.py`), Grader (`grader.py`), 16 cell briefs (`briefs/DIFF.md`), exact token accounting, retry design decision |
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

## 2. Infrastructure Deliverables (Phase 0)

1. **Real Agent Runner (`runner/agent_runner.py`):**
   - Independent session per attempt; no state leakage between tickets.
   - Clean separation of factor states without per-factor patch heuristics.
   - Sandboxed workspace with `pytest` execution on visible tests for $u=1$; zero execution tools for $u=0$.
   - Structured Self-Review ($r=1$) and Automated Policy Retry ($k=1$) model turns.
   - Full transcript logging: command line, stdout, stderr, exit code, elapsed time, and per-turn tokens saved to `results/<exp>/raw/`.
   - Execution sequence randomized with logged order (`schedule_order.json`).
2. **Strict Evaluator (`runner/grader.py`):**
   - Absolute isolation of gold reference solutions (validators only).
   - Tamper detection against protected test directory files.
   - Independent runs against hidden test variants.
3. **Exact Token Accounting:**
   - Incremental costs measured with `tiktoken` (`cl100k_base`):
     - Bare prompt ($S_1$): 26 tokens
     - Full Book ($B$): 871 tokens ($+845$ incremental over $S_1$)
     - Short Book ($S_2$): 323 tokens ($+297$ incremental over $S_1$)
     - Student Notes ($S_4$): 623 tokens ($+597$ incremental over $S_1$)
     - Worked Examples ($P_3$): 1,943 tokens ($+1{,}072$ incremental over $B$)
     - Test Runner Brief ($U_2$): 980 tokens ($+109$ incremental over $B$)
     - Self-Review Checklist ($R_2$): 966 tokens ($+95$ incremental over $B$)
   - Replaced all estimated token figures in manuscript and recompiled publication PDF.
4. **Retry Design Decision:**
   - In the primary $E4a$ factorial, Retry feedback is restricted to **Policy Errors Only** ($E3b$-comparable) to preserve factor orthogonality and avoid confounding $Tools \times Retry$.
   - The Policy + Visible Pytest feedback variant is isolated and measured in Phase 3.4.

---

## 3. Responses to Claude Review Items

- **Round 1 (Blocking) - Simulated $E3d$:** Fixed in commit `ce74325` (synthetic simulation scripts purged; paper rewritten with real data).
- **Round 1 (Blocking) - Contradiction §7.4 vs §7.5:** Fixed in commit `ce74325` (removed §7.5).
- **Round 1 (Blocking) - Unsourced MIP numbers:** Fixed in commit `36a7217` and current commit (replaced with measured BPE tokenizer counts).
- **Round 2 Item 1 - §9.4 patch overwrite:** Fixed in commit `36a7217` (accurately stated four tool-arm patches were overwritten and replaced).
- **Round 2 Item 2 - Model name:** Fixed in commit `36a7217` (standardized to *"Claude Sonnet subagents (exact version not recorded)"*).
- **Round 2 Item 3 - Attempt counts:** Fixed in commit `36a7217` (corrected to ~1,950 graded attempts).
- **Round 2 Item 4 - Hard4 ticket IDs & 604 failure:** Fixed in commit `36a7217` (corrected to `h602`, `h604`, `h605` and unterminated quote `ValueError`).
- **Round 2 Item 5 - Mutant test mentions:** Fixed in commit `36a7217` (replaced with hidden unit tests and file protection checks).
- **Round 2 Item 6 - Token costs:** Fixed in current commit (measured using `tiktoken` `cl100k_base` / `o200k_base`).
- **Round 2 Item 7 - Overclaims softened:** Fixed in commit `36a7217` (softened to "no detectable difference" and "untested hypothesis").
- **Round 2 Item 8 - Retry rescue claim:** Fixed in commit `36a7217` (stated as 17 of 17 compliance failures).

---

## 4. Open Questions & Handoff for Next Phase

- **Current Status:** Phase 0 complete and verified. Ready to proceed to Phase 1 (benchmark design of 12 multi-module tasks and the Difficulty Gate).
- **Open Questions for Claude:** None currently blocking; Gate A review will be requested following the Phase 1 difficulty-gate execution.
