# Stage 1 Report: One Family on Each End

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 1)
- **Date / Time:** 2026-10-26 15:06:16 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Total Attempts in Stage 1:** 128 (32 reused B0 + 96 new calls for P, R, F)
- **New Calls Billed Tokens:** Input=181,124, Output=48,334, Thinking=132,191, Total=361,649
- **Financial Cost of New Calls:** $0.0677 USD
- **Wall-Clock Duration of New Calls:** 154.4s (~2.6m)

## 1. Per-Family Summary & Gains Table

| Position | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Pos 1 | `state_transitions` | H15 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** |
| Pos 14 | `calendar_recurrence` | H05 | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | 16/16 (100.0%) | **+0.0** | **+0.0** |

## 2. Per-Task Breakdown Table

| Family | Task ID | Name | Class | B0 Pass | P Pass | R Pass | F Pass |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| `state_transitions` | 2077 | Deployment Pipeline Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2078 | Payment Escrow Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 1/4 |
| `state_transitions` | 2079 | Support Ticket Workflow | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2080 | Cloud Compute Instance Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `calendar_recurrence` | 2010 | Subscription Active Window Evaluator | `TAUGHT` | 8/8 | 7/8 | 8/8 | 8/8 |
| `calendar_recurrence` | 2012 | Audit Log Retention Window | `TAUGHT` | 8/8 | 8/8 | 8/8 | 8/8 |

## 3. Plain-Language Reading (5 Lines)

1. Unknown end (state_transitions, Pos 1): Unaided baseline B0 was 0/16 (0.0%) and Placebo P was 0/16 (0.0%).
2. Education on unknown end: Rule-only R achieved 16/16 (100.0%, gain: +100.0 pts) and Full Handbook F achieved 13/16 (81.2%, gain: +81.2 pts).
3. Ceiling end (calendar_recurrence, Pos 14): Unaided baseline B0 is already at ceiling 16/16 (100.0%).
4. Education on ceiling end: Arms P (15/16), R (16/16), and F (16/16) exhibit zero headroom with gain = +0.0 pts.
5. The hypothesis is sharply supported at the extrema: maximum gain occurs where the model lacks prior knowledge (gain +81.2 pts), while ceiling tasks yield 0.0 pts gain.

## 4. Verification Artifacts & Links

- **Raw Outputs Directory:** [`results/stage1/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage1/raw)
- **Consolidated Results:** [`results/stage1/results.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage1/results.json)
- **Schedule File:** [`results/stage1/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage1/schedule_order.json)
- **Runner Script:** [`runner/run_stage1.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage1.py)
