# SWE-2 results: ontology + knowledge harness + confidence harness

Model: Qwen3.6-35B-A3B (UD-Q4_K_M, llama.cpp, CPU). Strict pass on hidden tests.

Education arms restricted to balanced rounds 1-3 (B0: all attempts).

## Arm totals

| Arm | strict pass | rate | 95% CI | gain vs B0 (pp) |
|---|---|---|---|---|
| B0 | 19/56 | 33.9% | 23-47% | +0.0 |
| PLACEBO | 16/42 | 38.1% | 25-53% | +4.2 |
| KNOW | 35/42 | 83.3% | 69-92% | +49.4 |
| SURE | 17/42 | 40.5% | 27-56% | +6.5 |
| KNOW_SURE | 35/42 | 83.3% | 69-92% | +49.4 |

## Familiarity ranking (before education) and per-family strict pass

Familiarity = mean of the ranks of closed-book quiz accuracy and B0 debugging pass rate (1 = least familiar).

| Pos | Family | Rule | Quiz acc | Quiz consistency | Quiz conf | B0 | PLACEBO | KNOW | SURE | KNOW_SURE |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | service_errors | H04 | 0.40 | 0.80 | 0.92 | 0% (4) | 0% (3) | 100% (3) | 0% (3) | 100% (3) |
| 2 | config_lists | H12 | 0.60 | 0.93 | 0.94 | 0% (4) | 0% (3) | 100% (3) | 0% (3) | 100% (3) |
| 3 | idempotency_keys | H13 | 0.60 | 0.80 | 0.91 | 0% (4) | 0% (3) | 100% (3) | 0% (3) | 67% (3) |
| 4 | wire_envelope | H08 | 0.60 | 0.93 | 0.92 | 0% (4) | 0% (3) | 100% (3) | 0% (3) | 100% (3) |
| 5 | csv_roundtrip | H10 | 0.00 | 1.00 | 0.95 | 50% (4) | 33% (3) | 67% (3) | 33% (3) | 100% (3) |
| 6 | metric_percentiles | H14 | 0.27 | 0.87 | 0.92 | 75% (4) | 33% (3) | 100% (3) | 67% (3) | 100% (3) |
| 7 | event_ordering | H07 | 0.47 | 0.80 | 0.85 | 50% (4) | 67% (3) | 100% (3) | 67% (3) | 67% (3) |
| 8 | money_rounding | H02 | 0.60 | 0.67 | 0.97 | 25% (4) | 67% (3) | 67% (3) | 67% (3) | 33% (3) |
| 9 | timestamp_iso | H09 | 0.60 | 0.73 | 0.92 | 25% (4) | 67% (3) | 67% (3) | 67% (3) | 100% (3) |
| 10 | config_merge | H03 | 0.73 | 0.87 | 0.95 | 0% (4) | 33% (3) | 33% (3) | 33% (3) | 67% (3) |
| 11 | state_transitions | H15 | 0.73 | 0.93 | 0.94 | 0% (4) | 0% (3) | 100% (3) | 0% (3) | 100% (3) |
| 12 | cache_ttl | H11 | 0.67 | 0.67 | 0.94 | 100% (4) | 100% (3) | 100% (3) | 100% (3) | 100% (3) |
| 13 | calendar_recurrence | H05 | 0.67 | 1.00 | 0.95 | 100% (4) | 100% (3) | 100% (3) | 100% (3) | 100% (3) |
| 14 | permission_prefix | H06 | 0.87 | 0.87 | 0.93 | 50% (4) | 33% (3) | 33% (3) | 33% (3) | 33% (3) |

## Familiarity vs gain (Spearman rho across families, permutation p)

Quiz accuracy is the primary predictor: it is measured independently of debugging. B0 pass rate (and the composite) shares B0 sampling noise with the gain (arm - B0), which biases rho negative (regression to the mean).

| Gain of arm over B0 | vs quiz accuracy | vs B0 pass rate | vs composite familiarity | vs quiz consistency |
|---|---|---|---|---|
| PLACEBO (n=14) | +0.18 (p=0.533) | -0.29 (p=0.302) | +0.08 (p=0.786) | -0.52 (p=0.062) |
| KNOW (n=14) | -0.24 (p=0.397) | -0.83 (p=0.001) | -0.74 (p=0.004) | -0.02 (p=0.934) |
| SURE (n=14) | +0.13 (p=0.660) | -0.27 (p=0.338) | +0.05 (p=0.850) | -0.54 (p=0.049) |
| KNOW_SURE (n=14) | -0.23 (p=0.433) | -0.83 (p=0.000) | -0.68 (p=0.011) | +0.21 (p=0.462) |
| KNOW - PLACEBO (n=14) | | | -0.77 (p=0.002) | |
| KNOW_SURE - KNOW (n=14) | | | +0.16 (p=0.586) | |
| SURE - B0 (n=14) | | | +0.05 (p=0.850) | |

## Harness diagnostics

- PLACEBO: retrieval contained the family's rule in 0% of attempts; `know` tool used in 0%.
- KNOW: retrieval contained the family's rule in 100% of attempts; `know` tool used in 7%.
- KNOW_SURE: retrieval contained the family's rule in 100% of attempts; `know` tool used in 60%.
- SURE: revised 42/42 (conflict 3); revision fixed 1, broke 0; first-draft pass 16/42 -> final 17/42.
- KNOW_SURE: revised 42/42 (conflict 1); revision fixed 3, broke 1; first-draft pass 33/42 -> final 35/42.
- B0 stated confidence (post-hoc probe) mean 0.94 vs actual pass 0.34 (n=56).
- Attempts using at least one tool: 135/224; tampering: 0.
