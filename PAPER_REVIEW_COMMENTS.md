# Review Tracker: "Designing AI Reliability as an Education Optimization Problem"

This document tracks all external peer-review feedback, reviewer recommendations, and their verified resolutions in the repository and manuscript.

---

## Round 1 Review (Blocking)

### 1. Simulated Experiment $E3d$ Presented as Real Data
- **Reviewer Note:** Blocking. $E3d$ is a simulation, presented as an experiment. `benchmarks/run_factorial_sep.py::generate_patch()` hard-codes the patch per factor (task 802: `if r == 1: reference solution`; 801: `u == 1 or r == 1`; 803: `s == 1`; 804: `s == 1 or p == 1`; tamper: `s == 0 and p == 0 and run == 2`). No agent runs. The regression recovers those `if` statements; $SE = 0.0070$ / $R^2 = 0.982$ / $t$ up to 28 follow from identical runs within a cell.
- **Affected:** Abstract ranking, contributions 3 and 4, Sec 7.5 (Tables 2–3), Sec 8 (hierarchy, interactions, MIP), Sec 10, README table.
- **Action Taken & Verified:**
  - Completely purged all synthetic simulation code: deleted `benchmarks/run_factorial_sep.py`, `benchmarks/sep_tasks.py`, `benchmarks/validate_sep.py`, and `results/rows_sep_factorial.json`.
  - Removed Section 7.5 from the manuscript.
  - Rewrote the Abstract, Contributions, Section 8, and Section 10 to strictly present the genuine empirical findings from ~1,950 graded Claude Sonnet attempts.
  - Replaced the simulation claims with a formal protocol for future live agent factorial runs (`REAL_TEST_REQUIREMENTS.md`).

### 2. Contradiction between §7.4 and §7.5
- **Reviewer Note:** §7.4 says the ceiling persists through Hard4; §7.5 says a new suite breaks it. The only support for §7.5 is item 1.
- **Action Taken & Verified:**
  - Removed §7.5 entirely. §7.4 now stands as the concluding subsection of Section 7, documenting the ceiling effect across all 5 hardening tiers.

### 3. Mixed Integer Program (MIP) Numbers Unsourced
- **Reviewer Note:** MIP numbers in §8.3 are unsourced (token costs $c_s \sim 1{,}200$, $c_p \sim 2{,}400$, $c_r \sim 350$, $c_k \sim 800$; "100.0% clean pass rates"). Use logged token counts and measured gains only.
- **Action Taken & Verified:**
  - Removed unsourced synthetic token parameters.
  - Explicitly labeled all token counts as unverified estimates based on file character counts and pilot averages.
  - Grounded optimization recommendations in measured empirical gains ($Y = C \cdot (1 - T)$) and verified retry dynamics.

---

## Round 2 Review (Paper & Protocol Rigor)

### Verified Valid in Codebase
- The E1/E2 inversion, the E3a table, 936/960 with 17/17 retry rescues, the §7.4 table, and the "tool use in 2 runs" note match what was run.
- The attempt-level $p < 0.001$ for $S_4$ vs. $B$ holds (Fisher exact $p = 1.7 \times 10^{-6}$), against the run-level permutation $p = 0.167$.

### Revisions Completed in Manuscript

| # | Reviewer Comment | Location in Paper | Resolution & Wording |
|---|-------------------|-------------------|----------------------|
| **1** | **§9.4 is false.** Stated regenerated Hard4 patches "matched original output distribution". The originals were overwritten, so no comparison was possible. | §9.4 | Updated to state accurately: *"the tool-arm patches for four tickets were overwritten and lost, and were subsequently replaced by fresh runs."* |
| **2** | **"Claude 3.5 Sonnet" is still in two places.** Exact model was never recorded. | Abstract, §1, §9.2 | Replaced with *"Claude Sonnet subagents (exact version not recorded)"*. |
| **3** | **"Over 2,300 graded attempts" is wrong.** Total across E1, E2, E3a, E3b, E3c is ~1,950. | Abstract, §1, §6, §10 | Corrected to *"approximately 1,950 graded attempts"*. |
| **4** | **Task IDs in §7.4 are wrong.** Ticket IDs are 602, 604, 605, not 202, 204, 205. 604 failure was missing `ValueError` on unterminated quote, not leading apostrophe. | §7.4 | Corrected ticket IDs to `h602`, `h604`, and `h605`. Corrected `h604` failure description to missing `ValueError` on unterminated quote. |
| **5** | **"Mutant test suites" and "mutant verification"** appear in text, but `evaluate()` has no mutant check. | Abstract, §1, §2.2, §4.2 heading | Replaced all references with *"hidden unit test suites and file-protection checks"*. Section 4.2 heading updated to *"Tamper Isolation and Hidden Test Verification"*. |
| **6** | **§5.2 and §8.4 token costs** have no measurement script or log in repo. | §5.2, §8.4 | Added explicit disclaimers: character count breakdowns provided for brief files; token values labeled as unverified estimates based on pilot averages. |
| **7** | **§7.4 overclaims.** "Runtime feedback provides zero marginal accuracy gain" rests on 21 attempts per arm over 3 runs. §8.3 claims retrieval tools become "non-optional" on large repos. | §7.4, §8.3 | §7.4 softened to *"showed no detectable difference on this sample (21 attempts per arm across 3 runs)"*. §8.3 labeled explicitly as an *"untested hypothesis"*. |
| **8** | **Conclusion retry claim** and E3c suite unification. | §10, §6 | Clarified retry rescue rate as *"17 of 17 compliance failures"* (100% of the observed retry cell failures). Unified E3c description to consistently reference five hardening suites (Hard1–Hard4, where Hard4 has two revisions). |

---

## Protocol Improvements (`REAL_TEST_REQUIREMENTS.md`)

- **Environment & Code Freezing:** Harness code, benchmarks, and commit hash must be frozen prior to evaluation.
- **Model Metadata:** Record exact model version, API parameters, and sampling temperature.
- **Pre-Flight Gates:** Verify reference solutions pass 100% and unpatched repositories fail 100% of hidden tests.
- **The Fairness Gate:** Explicit fairness table certifying where each hidden requirement is documented in visible context. Custom conventions must not be hidden; difficulty must be decoupled from guessing.
- **Statistical Analysis Plan:** Ticket treated as a blocking factor; cluster-robust standard errors and run-level permutations enforced to avoid false confidence from pooled attempt $p$-values. Full command-line logs, exit codes, and timestamps required for tool calls.
