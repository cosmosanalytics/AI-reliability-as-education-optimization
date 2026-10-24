# Deviations and Operational Log (`DEVIATIONS.md`)

This is an append-only, timestamped log recording all operational decisions, harness adjustments, runtime anomalies, API timeouts, or reruns throughout the experimental campaign.

*Note on Timestamps:* All log entries record standard UTC ISO 8601 timestamps (`Z`). Local development machine operates on EDT (UTC-4), so 17:15Z corresponds to 13:15 EDT.

---

### [2026-10-24T17:15:00Z] Phase 0 Initialization & Brief Harmonization
- **Context:** In the initial pilot configurations, five factor-ablation briefs (`S1.md`, `B.md`, `R2.md`, `U2.md`, `P3.md`) were stored under single-letter names rather than the standard 4-digit cell naming scheme (`C0000`, `C1000`, `C1001`, `C1010`, `C1100`).
- **Action:** Created standard copies `C0000.md`, `C1000.md`, `C1001.md`, `C1010.md`, `C1100.md` in `briefs/` to ensure the runner executes across a uniform 16-cell naming convention without special branching. Documented in `briefs/DIFF.md`.
- **Impact:** Zero impact on prompt content; improves execution uniformity and prevents harness branch specializations.

### [2026-10-24T17:16:00Z] Phase 0 Token Accounting & Paper Synchronization
- **Context:** Previous manuscript draft utilized estimated token footprints ($\approx 1{,}050$ for Full Book, $\approx 380$ for Short Book, $\approx 2{,}000$ for Worked Examples).
- **Action:** Executed exact BPE tokenization using `tiktoken` (`cl100k_base` and `o200k_base`) on all brief files. The true incremental costs were measured at $+845$ tokens for Full Book ($B$), $+297$ tokens for Short Book ($S_2$), $+1{,}072$ tokens for Worked Examples ($P_3 - B$), $+103$ tokens for Test Runner ($U_2 - B$), and $+95$ tokens for Review Checklist ($R_2 - B$).
- **Impact:** Updated Section 5.2 and Section 8.4 in `designing_ai_reliability_as_an_education_optimization_problem.md`, recompiled PDF (`488 KB`), and documented in `briefs/DIFF.md`.

### [2026-10-24T17:45:00Z] Round 3 Review Fixes (Items 1–11)
- **Context:** Peer review of commit `877e2d3` identified five blocking issues (silent mock fallback, 0/1 retry parity bug, missing format instruction envelope, forced one-time tool execution, review step format loss) and six non-blocking hygiene/metadata items.
- **Action:**
  1. Completely eliminated mock fallback in `runner/agent_runner.py`; added mandatory `startup_self_check()` raising fatal `RuntimeError` on unconfigured backend.
  2. Fixed retry factor parity to $\pm 1$ sign coding: $k=1$ iff $(s+p+u+r) \% 2 == 0$. Verified orthogonal Resolution-V balance (8 $k^+$, 8 $k^-$) in `tests/test_factorial_design.py`.
  3. Added `STANDARD_TASK_ENVELOPE_HEADER` to every prompt outside the factor briefs, preventing format confounding for $S_1$.
  4. Implemented real interactive tool calling loop (`=== TOOL: pytest ===`); replaced stale `/tmp/claude-0` paths in all $u=1$ briefs; `tool_used` and `tool_call_count` derive from live calls.
  5. Updated review prompt to explicitly mandate block patch format; established clear definitions of `attempt1_strict`, `post_review_strict`, and `final_strict`.
  6. Added full turn-by-turn audit trail logging (`turn{t}_prompt.txt`, `turn{t}_resp.txt`, `tool_log.json`, `transcript.json`, all intermediate grades).
  7. Created `.gitignore` and purged `.pyc` files from git cache.
  8. Created comprehensive unit test suite in `tests/test_runner_dry_run.py` (7/7 tests passing).
- **Impact:** Runner and protocol fully conform to binding `REAL_TEST_REQUIREMENTS.md` standards.
