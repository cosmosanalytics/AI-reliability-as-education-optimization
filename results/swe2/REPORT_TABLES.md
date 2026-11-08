# SWE-2 results: ontology + knowledge harness + confidence harness

Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp, CPU). Strict pass on hidden tests.

## Arm totals

| Arm | strict pass | rate | 95% CI | gain vs B0 (pp) |
|---|---|---|---|---|
| B0 | 19/56 | 33.9% | 23-47% | +0.0 |
| PLACEBO | 10/28 | 35.7% | 21-54% | +1.8 |
| KNOW | 22/26 | 84.6% | 66-94% | +50.7 |
| SURE | 8/26 | 30.8% | 17-50% | -3.2 |
| KNOW_SURE | 23/28 | 82.1% | 64-92% | +48.2 |

## Familiarity ranking (before education) and per-family strict pass

Familiarity = mean of the ranks of closed-book quiz accuracy and B0 debugging pass rate (1 = least familiar).

| Pos | Family | Rule | Quiz acc | Quiz consistency | Quiz conf | B0 | PLACEBO | KNOW | SURE | KNOW_SURE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | service_errors | H04 | 0.40 | 0.80 | 0.92 | 0% (4) | 0% (2) | 100% (2) | 0% (2) | 100% (2) |
| 2 | config_lists | H12 | 0.60 | 0.93 | 0.94 | 0% (4) | 0% (2) | 100% (2) | 0% (2) | 100% (2) |
| 3 | idempotency_keys | H13 | 0.60 | 0.80 | 0.91 | 0% (4) | 0% (2) | 100% (1) | 0% (2) | 50% (2) |
| 4 | wire_envelope | H08 | 0.60 | 0.93 | 0.92 | 0% (4) | 0% (2) | 100% (1) | 0% (2) | 100% (2) |
| 5 | csv_roundtrip | H10 | 0.00 | 1.00 | 0.95 | 50% (4) | 0% (2) | 100% (2) | 0% (2) | 100% (2) |
| 6 | metric_percentiles | H14 | 0.27 | 0.87 | 0.92 | 75% (4) | 0% (2) | 100% (2) | 50% (2) | 100% (2) |
| 7 | event_ordering | H07 | 0.47 | 0.80 | 0.85 | 50% (4) | 50% (2) | 100% (2) | 50% (2) | 50% (2) |
| 8 | money_rounding | H02 | 0.60 | 0.67 | 0.97 | 25% (4) | 50% (2) | 50% (2) | 50% (2) | 50% (2) |
| 9 | timestamp_iso | H09 | 0.60 | 0.73 | 0.92 | 25% (4) | 100% (2) | 100% (2) | 0% (1) | 100% (2) |
| 10 | config_merge | H03 | 0.73 | 0.87 | 0.95 | 0% (4) | 50% (2) | 0% (2) | 50% (2) | 50% (2) |
| 11 | state_transitions | H15 | 0.73 | 0.93 | 0.94 | 0% (4) | 0% (2) | 100% (2) | 0% (2) | 100% (2) |
| 12 | cache_ttl | H11 | 0.67 | 0.67 | 0.94 | 100% (4) | 100% (2) | 100% (2) | 100% (2) | 100% (2) |
| 13 | calendar_recurrence | H05 | 0.67 | 1.00 | 0.95 | 100% (4) | 100% (2) | 100% (2) | 100% (1) | 100% (2) |
| 14 | permission_prefix | H06 | 0.87 | 0.87 | 0.93 | 50% (4) | 50% (2) | 50% (2) | 50% (2) | 50% (2) |

## Familiarity vs gain (Spearman rho across families, permutation p)

Quiz accuracy is the primary predictor: it is measured independently of debugging. B0 pass rate (and the composite) shares B0 sampling noise with the gain (arm - B0), which biases rho negative (regression to the mean).

| Gain of arm over B0 | vs quiz accuracy | vs B0 pass rate | vs composite familiarity | vs quiz consistency |
|---|---|---|---|---|
| PLACEBO (n=14) | +0.47 (p=0.089) | -0.34 (p=0.235) | +0.25 (p=0.383) | -0.48 (p=0.087) |
| KNOW (n=14) | -0.38 (p=0.185) | -0.72 (p=0.005) | -0.80 (p=0.001) | +0.11 (p=0.700) |
| SURE (n=14) | +0.56 (p=0.038) | -0.36 (p=0.210) | +0.21 (p=0.475) | -0.24 (p=0.399) |
| KNOW_SURE (n=14) | -0.17 (p=0.545) | -0.84 (p=0.001) | -0.64 (p=0.018) | +0.24 (p=0.410) |
| KNOW - PLACEBO (n=14) | | | -0.76 (p=0.003) | |
| KNOW_SURE - KNOW (n=14) | | | +0.33 (p=0.264) | |
| SURE - B0 (n=14) | | | +0.21 (p=0.475) | |

## Harness diagnostics

- PLACEBO: retrieval contained the family's rule in 0% of attempts; `know` tool used in 0%.
- KNOW: retrieval contained the family's rule in 100% of attempts; `know` tool used in 8%.
- KNOW_SURE: retrieval contained the family's rule in 100% of attempts; `know` tool used in 54%.
- SURE: revised 26/26 (conflict 2); revision fixed 1, broke 0; first-draft pass 7/26 -> final 8/26.
- KNOW_SURE: revised 28/28 (conflict 1); revision fixed 2, broke 1; first-draft pass 22/28 -> final 23/28.
- B0 stated confidence (post-hoc probe) mean 0.94 vs actual pass 0.34 (n=56).
- Attempts using at least one tool: 97/164; tampering: 0.
