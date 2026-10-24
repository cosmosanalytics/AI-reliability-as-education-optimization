# Deviations and Operational Log (`DEVIATIONS.md`)

This is an append-only, timestamped log recording all operational decisions, harness adjustments, runtime anomalies, API timeouts, or reruns throughout the experimental campaign.

---

### [2026-10-24T17:15:00Z] Phase 0 Initialization & Brief Harmonization
- **Context:** In the initial pilot configurations, five factor-ablation briefs (`S1.md`, `B.md`, `R2.md`, `U2.md`, `P3.md`) were stored under single-letter names rather than the standard 4-digit cell naming scheme (`C0000`, `C1000`, `C1001`, `C1010`, `C1100`).
- **Action:** Created standard copies `C0000.md`, `C1000.md`, `C1001.md`, `C1010.md`, `C1100.md` in `briefs/` to ensure the runner executes across a uniform 16-cell naming convention without special branching. Documented in `briefs/DIFF.md`.
- **Impact:** Zero impact on prompt content; improves execution uniformity and prevents harness branch specializations.

### [2026-10-24T17:16:00Z] Phase 0 Token Accounting & Paper Synchronization
- **Context:** Previous manuscript draft utilized estimated token footprints ($\approx 1{,}050$ for Full Book, $\approx 380$ for Short Book, $\approx 2{,}000$ for Worked Examples).
- **Action:** Executed exact BPE tokenization using `tiktoken` (`cl100k_base` and `o200k_base`) on all brief files. The true incremental costs were measured at $+845$ tokens for Full Book ($B$), $+297$ tokens for Short Book ($S_2$), $+1{,}072$ tokens for Worked Examples ($P_3 - B$), $+109$ tokens for Test Runner ($U_2 - B$), and $+95$ tokens for Review Checklist ($R_2 - B$).
- **Impact:** Updated Section 5.2 and Section 8.4 in `designing_ai_reliability_as_an_education_optimization_problem.md`, recompiled PDF (`488 KB`), and documented in `briefs/DIFF.md`.
