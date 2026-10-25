# Screening B Empirical Smoke Test & Budget Extrapolation Report

**Generated:** 2026-10-25 23:09:46 UTC  
**Git Commit:** `ba3e729`  
**Model:** `gemini-2.5-flash` (T=0.7, top_p=0.95, thinking=2048, max_output=16384)  
**Purpose:** Preflight verification of rebuilt briefs with frozen `HANDBOOK.md` and `P3.md`, and empirical budget extrapolation for the 1,656 attempts of Screening B.

---

## 1. Measured 9-Attempt Smoke Test Results

| Cell | Configuration | Parity ($k$) | Attempts | Strict Pass | Mean Tokens In | Mean Tokens Out | Mean Thinking | Mean Billed | Mean Calls | Mean Cost ($) | Mean Time (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C0000** | s=0, p=0, u=0, r=0 | k=1 | 3 | 1/3 | 961 | 448 | 1,454 | 2,864 | 1.0 | **$0.00504** | 12.4s |
| **C1001** | s=1, p=0, u=0, r=1 | k=1 | 3 | 1/3 | 7,265 | 1,713 | 3,275 | 12,253 | 1.0 | **$0.01465** | 31.6s |
| **C1111** | s=1, p=1, u=1, r=1 | k=1 | 3 | 2/3 | 15,226 | 1,755 | 5,923 | 22,904 | 1.0 | **$0.02376** | 46.3s |

### Key Empirical Invariant Checks:
1. **Brief Delivery Verification:** Verified that `C1001` and `C1111` briefs contained `briefs/HANDBOOK.md` verbatim (including Rules H01–H16). Verified that `C1111` contained `briefs/P3.md`. Verified that `C0000` contained zero handbook rules.
2. **Total Smoke Test Spend:** **$0.1304 USD** across all 9 attempts.
3. **Execution Integrity:** Exactly **0** provider errors, **0** `MAX_TOKENS` truncations, 100% `FinishReason.STOP`.

---

## 2. Empirical Budget Extrapolation for Screening B (1,656 Attempts)

- **Preserved Invariant Cells (Screening A):** 4 cells (`C0000`, `C0001`, `C0010`, `C0011`, $s=0, p=0$) with **552 attempts** are 100% byte-identical and preserved.
- **Scope to Re-Run:** 12 cells ($s=1$ or $p=1$) $	imes$ 46 Tune tasks $	imes$ 3 runs = **1,656 scheduled attempts**.
- **Measured Mid-Cell Unit Cost (`C1001`):** $0.01465 USD / attempt
- **Measured Heavy-Cell Unit Cost (`C1111`):** $0.02376 USD / attempt
- **Weighted Mean Unit Cost across 12 Re-Run Cells:** **$0.01921 USD** / attempt
- **Projected Baseline Spend (1,656 attempts):** **$31.81 USD**
- **Proposed Hard-Stop Cost Cap ($1.5\times$):** **$47.71 USD**

---
*Smoke test completed in isolated test directory `results/smoke_test_screening_b/`.*