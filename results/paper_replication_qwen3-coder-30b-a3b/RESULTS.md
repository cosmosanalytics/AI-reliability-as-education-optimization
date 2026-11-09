# Paper replication: Qwen3-Coder-30B-A3B-Instruct (local, CPU)

This reruns the diagnose-then-teach experiment from "Instruction Gains Track the Knowledge Gap" with an open-source model, served locally.

## Setup

- **Model:** `unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF`, file `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`. It is a mixture-of-experts model with about 3B active parameters.
- **Serving:** llama.cpp `llama-server` with `-c 49152 --parallel 4 --jinja`, on a CPU-only VM with 8 cores and 31 GB RAM.
- **Sampling:** same as the paper: T=0.7, top-p 0.95.
- **Protocol:** the paper's prompts, grader and per-family sample allocation, with `runner/run_dimensions.py --backend local`.
- **Strict pass:** the hidden tests pass *and* the patch modifies no protected test file.
- **Stages:**
  - Stage 0: B0 baseline on all 14 families (218 attempts), which gives the familiarity ranking.
  - Then Placebo, Rule-only and Full handbook on the extremes (positions 1–5 and 10–14, 456 attempts) and the middle (positions 6–9, 198 attempts).
  - 872 attempts in total. Wall time 28.6 h: 5.6 h, then 11.1 h, then 11.8 h.
- **Grading check:** all 872 records were re-graded with the repo's Python 3.12 environment, and none changed.
- **Analysis:** `runner/analyze_paper_replication.py paper_replication_qwen3-coder-30b-a3b`. It writes `PAPER_TABLE.md`, `paper_summary.json` and `gain_vs_baseline.png`.

## Familiarity ranking and education gains (strict pass)

| Pos | Family | Rule | Baseline | Placebo | Rule only | Full handbook | Rule gain | Full gain |
|:-:|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | `config_lists` | H12 | 0/16 | 0/16 | 5/16 | 4/16 | +31 | +25 |
| 2 | `config_merge` | H03 | 0/8 | 0/8 | 0/8 | 0/8 | +0 | +0 |
| 3 | `csv_roundtrip` | H10 | 0/16 | 0/16 | 0/16 | 0/16 | +0 | +0 |
| 4 | `event_ordering` | H07 | 0/16 | 0/16 | 6/16 | 2/16 | +38 | +12 |
| 5 | `idempotency_keys` | H13 | 0/16 | 0/16 | 0/16 | 0/16 | +0 | +0 |
| 6 | `money_rounding` | H02 | 0/18 | 0/18 | 5/18 | 5/18 | +28 | +28 |
| 7 | `permission_prefix` | H06 | 0/16 | 1/16 | 0/16 | 1/16 | +0 | +6 |
| 8 | `service_errors` | H04 | 0/16 | 0/16 | 7/16 | 8/16 | +44 | +50 |
| 9 | `state_transitions` | H15 | 0/16 | 0/16 | 8/16 | 15/16 | +50 | +94 |
| 10 | `timestamp_iso` | H09 | 0/16 | 0/16 | 0/16 | 0/16 | +0 | +0 |
| 11 | `wire_envelope` | H08 | 0/16 | 0/16 | 0/16 | 0/16 | +0 | +0 |
| 12 | `metric_percentiles` | H14 | 4/16 | 0/16 | 1/16 | 0/16 | -19 | -25 |
| 13 | `cache_ttl` | H11 | 10/16 | 6/16 | 4/16 | 8/16 | -38 | -12 |
| 14 | `calendar_recurrence` | H05 | 11/16 | 9/16 | 6/16 | 13/16 | -31 | +12 |
| | **All** | | 25/218 | 16/218 | 42/218 | 56/218 | +8 | +14 |

Positions 1–11 are tied at 0% baseline. Within the tie, families are ordered alphabetically.

## Correlation: gain vs baseline familiarity (Spearman, 14 families)

| Model | Full handbook rho | Rule only rho |
|---|---|---|
| Claude Sonnet (paper) | -0.82 | – |
| Gemini 2.5 Flash (paper) | -0.91 | – |
| **Qwen3-Coder-30B-A3B (this run)** | **-0.39** (p = 0.17) | **-0.74** (p = 0.002) |

Placebo: rho = -0.88, but it is not evidence of an effect:
- 10 of 14 families are level, 3 fall and 1 rises (sign test p = 0.63).
- Families at 0% cannot fall, so only the 3 familiar families can move, and they dropped.
- That floor makes rho strongly negative even for random noise.

Gains also track this model's own baseline better than other models' baselines:
- Full gain against the Claude baseline gives rho = -0.11; against the Gemini baseline, -0.27; against its own baseline, -0.39.
- This model's familiarity ranking correlates only weakly with Claude's (rho = 0.29) and moderately with Gemini's (0.61).

## Strict vs functional pass, and protected-file tampering

| Arm | Strict pass | Functional pass (hidden tests only) | Modified a protected test file |
|---|---|---|---|
| Baseline | 25/218 | 34/218 | 105/218 |
| Placebo | 16/218 | 26/218 | 136/218 |
| Rule only | 42/218 | **139/218** | 149/218 |
| Full handbook | 56/218 | 105/218 | 115/218 |

Per-family functional pass, Rule only:
- `wire_envelope` 15/16, `service_errors` 16/16, `state_transitions` 16/16, `metric_percentiles` 14/16, `config_lists` 13/16, `money_rounding` 12/18.
- With `wire_envelope`, every Rule-only attempt also edited `tests/` (16/16 tamper), so strict pass stays at 0/16.

## Findings

1. **Education helps most where the model knows least, but the effect is weaker than in the paper.**
   - Rule-only gain correlates with baseline at rho = -0.74, close to the paper's models.
   - Full-handbook gain correlates at -0.39, which is not significant with 14 families.
2. **The targeted rule teaches the fix more reliably than the full handbook.**
   - Functional pass with Rule only is 139/218, against 105/218 with the Full handbook.
   - But the Full handbook wins on strict pass (56 vs 42), because it tampers less (115 vs 149). It includes rule H01 (Test Directory Protection: never modify files under `tests/`), which the single-rule arm does not.
3. **Protected-test tampering is the main obstacle for this model.**
   - About half of all attempts edit a protected test file.
   - Many strict-pass zeros are attempts with a correct fix and an edited test.
   - The baseline brief (`briefs/B.md`, W13) asks for a regression test in the existing test file, and this model usually complies by editing a protected test file.
   - The paper does not report tamper rates for Claude or Gemini, so this comparison is not available. Strict-pass gains here are a lower bound on how much the handbook teaches the semantics.
4. **Some families are not learned at all.** `config_merge`, `timestamp_iso` and `csv_roundtrip` stay at or near 0% functional pass in every arm. With a 3B-active-parameter model at Q4, instruction alone does not close every gap.
5. **Familiar families lose under Placebo and Rule only.** `cache_ttl` and `metric_percentiles` drop under both arms. For the families this model already handles, extra context appears to add noise rather than knowledge.

## Limitations

- **Ties.** 11 of 14 families are tied at 0% baseline, so the ranking separates only 3 tiers and Spearman handles the rest as ties. A larger B0 sample would not break the ties, since the model never passed them.
- **Model setup.** Single model, single quantization (Q4_K_M), CPU inference. Throughput varied from 0.4 to 1.8 tok/s with host CPU steal.
- **Grading bug, fixed.** The first 84 Placebo records were graded with the system Python, which has no pytest. They were re-graded from the saved patches. See the regrade check above.
