# Stage 3 Report: Updated 10-Family Table

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 3)
- **Date / Time:** 2026-10-26 17:59:04 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Total Attempts in Stage 3 Dataset:** 616 across 10 families
- **New Calls Executed in Stage 3:** 174 live model calls
- **New Calls Billed Tokens:** Input=320,332, Output=117,659, Thinking=255,985, Total=693,976
- **Financial Cost of New Calls:** $0.1361 USD
- **Wall-Clock Duration of New Calls:** 293.4s (~4.9m across 8 parallel workers)

## 1. Updated 10-Family Summary & Gains Table

Ordered by baseline pass rate / display position (Positions 1–5: Unknown end; Positions 10–14: Ceiling end).

| Pos | Bug Family | Rule ID | B0 (Baseline) | P (Placebo) | R (Rule Only) | F (Full Handbook) | Rule Gain (pts) | Full Gain (pts) | Confidence / Pattern Note |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| Pos 1 | `state_transitions` | H15 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Consistent (unknown end) |
| Pos 2 | `idempotency_keys` | H13 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 13/16 (81.2%) | **+100.0** | **+81.2** | Consistent (unknown end) |
| Pos 3 | `service_errors` | H04 | 0/16 (0.0%) | 0/16 (0.0%) | 16/16 (100.0%) | 16/16 (100.0%) | **+100.0** | **+100.0** | Consistent (unknown end) |
| Pos 4 | `config_merge` | H03 | 1/8 (12.5%) | 5/8 (62.5%) | 1/8 (12.5%) | 4/8 (50.0%) | **+0.0** | **+37.5** | **Low Confidence** (1 task, n=8; P is noise check) |
| Pos 5 | `event_ordering` | H07 | 4/16 (25.0%) | 4/16 (25.0%) | 16/16 (100.0%) | 16/16 (100.0%) | **+75.0** | **+75.0** | Consistent (unknown end) |
| Pos 10 | `money_rounding` | H02 | 11/18 (61.1%) | 8/18 (44.4%) | 12/18 (66.7%) | 12/18 (66.7%) | **+5.6** | **+5.6** | Consistent (ceiling end) |
| Pos 11 | `config_lists` | H12 | 10/16 (62.5%) | 6/16 (37.5%) | 16/16 (100.0%) | 14/16 (87.5%) | **+37.5** | **+25.0** | Consistent (ceiling end) |
| Pos 12 | `timestamp_iso` | H09 | 15/16 (93.8%) | 12/16 (75.0%) | 16/16 (100.0%) | 14/16 (87.5%) | **+6.2** | **-6.2** | Consistent (ceiling end) |
| Pos 13 | `cache_ttl` | H11 | 16/16 (100.0%) | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | **-6.2** | **+0.0** | Consistent (ceiling end) |
| Pos 14 | `calendar_recurrence` | H05 | 16/16 (100.0%) | 15/16 (93.8%) | 16/16 (100.0%) | 16/16 (100.0%) | **+0.0** | **+0.0** | Consistent (ceiling end) |

*Pattern verdict: Unknown end families (Pos 1–5) exhibit large educational gains under the full handbook (mean +75.0 pts, range +37.5 to +100.0 pts), whereas ceiling end families (Pos 10–14) exhibit limited headroom (mean +4.9 pts, range -6.2 to +25.0 pts).*

## 2. Per-Task Breakdown Table (All 10 Families)

| Family | Task ID | Name | Class | B0 Pass | P Pass | R Pass | F Pass |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| `state_transitions` | 2077 | Deployment Pipeline Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2078 | Payment Escrow Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 1/4 |
| `state_transitions` | 2079 | Support Ticket Workflow | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `state_transitions` | 2080 | Cloud Compute Instance Lifecycle | `TRANSFER` | 0/4 | 0/4 | 4/4 | 4/4 |
| `idempotency_keys` | 2062 | Order Fulfillment RPC Client | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `idempotency_keys` | 2063 | Subscription Recurring Charge Request | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `idempotency_keys` | 2065 | Customer Refund Dispatcher | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `idempotency_keys` | 2067 | Cloud Virtual Machine Provisioning RPC | `TAUGHT` | 0/4 | 0/4 | 4/4 | 3/4 |
| `service_errors` | 2030 | Tenant Scope Authorization Guard | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2031 | Payload Schema Validation Pipeline | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2033 | Concurrent Document Lock Manager | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `service_errors` | 2035 | Burst Quota Throttling Guard | `TAUGHT` | 0/4 | 0/4 | 4/4 | 4/4 |
| `config_merge` | 2006 | Database Pool Settings | `TAUGHT` | 1/8 | 5/8 | 1/8 | 4/8 |
| `event_ordering` | 2022 | Notification Batch Sorter | `TAUGHT` | 4/8 | 3/8 | 8/8 | 8/8 |
| `event_ordering` | 2024 | Event Stream Ingestion Sequencer | `TAUGHT` | 0/8 | 1/8 | 8/8 | 8/8 |
| `money_rounding` | 2002 | Invoice Discount Allocation | `TAUGHT` | 0/6 | 0/6 | 0/6 | 0/6 |
| `money_rounding` | 2003 | Multi-Currency Fee Conversion | `TAUGHT` | 5/6 | 3/6 | 6/6 | 6/6 |
| `money_rounding` | 2102 | Merchant Settlement Fee Calculator | `TAUGHT` | 6/6 | 5/6 | 6/6 | 6/6 |
| `config_lists` | 2054 | Cloud Infrastructure Cluster Specification Merge | `TAUGHT` | 3/4 | 1/4 | 4/4 | 4/4 |
| `config_lists` | 2055 | CI/CD Pipeline Step Arguments Merger | `TAUGHT` | 1/4 | 1/4 | 4/4 | 2/4 |
| `config_lists` | 2057 | Application Feature Gate Setting Aggregator | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
| `config_lists` | 2059 | Service Mesh Route Matcher Configurator | `TAUGHT` | 3/4 | 2/4 | 4/4 | 4/4 |
| `timestamp_iso` | 2046 | Telemetry Log Serializer | `TAUGHT` | 4/4 | 4/4 | 4/4 | 4/4 |
| `timestamp_iso` | 2047 | Webhook Delivery Envelope | `TAUGHT` | 4/4 | 2/4 | 4/4 | 3/4 |
| `timestamp_iso` | 2049 | Database Snapshot Metadata Generator | `TAUGHT` | 4/4 | 3/4 | 4/4 | 3/4 |
| `timestamp_iso` | 2051 | Security Token Exchange Ledger | `TAUGHT` | 3/4 | 3/4 | 4/4 | 4/4 |
| `cache_ttl` | 2025 | In-Memory Token Cache | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `cache_ttl` | 2026 | API Rate Limit Session Store | `TRANSFER` | 4/4 | 4/4 | 3/4 | 4/4 |
| `cache_ttl` | 2027 | Distributed Lease Expiry Guard | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `cache_ttl` | 2028 | DNS Cache TTL Resolver | `TRANSFER` | 4/4 | 4/4 | 4/4 | 4/4 |
| `calendar_recurrence` | 2010 | Subscription Active Window Evaluator | `TAUGHT` | 8/8 | 7/8 | 8/8 | 8/8 |
| `calendar_recurrence` | 2012 | Audit Log Retention Window | `TAUGHT` | 8/8 | 8/8 | 8/8 | 8/8 |

## 3. Arm Below Rule-Only or Baseline Analysis (Patch-Level Verification)

Every instance where arm F or R scored below B0 or below R-only is categorized into real failure, interference, or noise:

1. **`config_lists` (Rule H12): Full Handbook F (14/16, 87.5%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Task 2055 (CI/CD Pipeline Step Arguments Merger):** R scored 4/4, F scored 2/4 (failing F runs: `r1`, `r4`).
   - **Patch Verification:** In both failing runs, the model correctly implemented Rule H12 recursive list merging, but explicitly added `from errors import ServiceError # Added for H04` at the top of `pipeline_composer.py`. Because this repository does not include an `errors` module, test collection failed immediately with `ModuleNotFoundError: No module named 'errors'`. Under Rule-only R, the model received only Rule H12 and did not attempt to import `ServiceError`, passing 4/4.
2. **`idempotency_keys` (Rule H13): Full Handbook F (13/16, 81.2%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Tasks 2063 (`r1`), 2065 (`r2`), 2067 (`r1`):** R scored 4/4 on each, F scored 3/4 on each.
   - **Patch Verification:** In Task 2063 `r1`, the model added a `ServiceError` class to `errors.py` with type annotation `Dict[str, Any]` without importing `Dict` from `typing`, triggering a collection `NameError: name 'Dict' is not defined`. In Task 2065 `r2` and 2067 `r1`, similar unrequested error-handling logic caused test collection crashes. Under Rule-only R, the model modified only `X-Idempotency-Key` headers, achieving 16/16.
3. **`state_transitions` (Rule H15): Full Handbook F (13/16, 81.2%) below Rule-Only R (16/16, 100.0%) — *Interference***
   - **Task 2078 (Payment Escrow Lifecycle):** R scored 4/4, F scored 1/4 (failing F runs: `r1`, `r3`, `r4`).
   - **Patch Verification:** The model incorporated Rule H03 (Container Immutability) from the full handbook into escrow state transitions, altering dictionary copy semantics and breaking assertions. Under Rule-only R, it implemented only the FSM transition validation, scoring 4/4.
4. **`config_merge` (Rule H03): Rule-Only R (1/8, 12.5%) below Placebo P (5/8, 62.5%) — *Noise / Task Sensitivity (Low Confidence)***
   - **Task 2006 (Database Pool Settings):** Single task with $n=8$.
   - **Patch Verification:** Under arm R, the model interpreted Rule H03 literally by applying defensive deep-copying inside `options.py` (`ConnectionOptions.__post_init__`) or `pool.py` rather than modifying `env_loader.py` (`merge_env_settings`). Under Placebo P, unaided by Rule H03, the model simply addressed the ticket issue description SEC-402 directly in `env_loader.py` (5/8 passes). Because this family consists of only 1 task ($n=8$), arm differences are high-variance; the P arm serves as the noise check.
5. **`timestamp_iso` (Rule H09): Full Handbook F (14/16, 87.5%) below Baseline B0 (15/16) and Rule-Only R (16/16) — *Noise / Real Formatting Bug***
   - **Tasks 2047 (`r3`) & 2049 (`r2`):**
   - **Patch Verification:** The model produced naive `isoformat(timespec='milliseconds') + 'Z'` strings that passed visible tests but failed hidden format assertions. Under Rule-only R, it produced canonical UTC timestamps, passing 16/16. This 2-attempt difference is consistent with sampling noise.
6. **`cache_ttl` (Rule H11): Rule-Only R (15/16, 93.8%) below Baseline B0 (16/16, 100.0%) — *Noise***
   - **Task 2026 (`r2`):**
   - **Patch Verification:** A single run added an extraneous quota validation inside `is_active`, failing one hidden check. 15/16 vs 16/16 is within expected temperature=0.7 variation.

## 4. Plain-Language Reading (5 Lines)

1. Unknown end (positions 1–5): state_transitions (Pos 1) gained +81.2 (full); idempotency_keys (Pos 2) gained +81.2 (full); service_errors (Pos 3) gained +100.0 (full); config_merge (Pos 4, low-conf n=8) baseline was 1/8 and gained +0.0 (rule) and +37.5 (full); event_ordering (Pos 5) baseline was 4/16 and gained +75.0 (rule) and +75.0 (full).
2. Ceiling end (positions 10–14): money_rounding (Pos 10) baseline was 11/18 and gained +5.6 (rule) and +5.6 (full); config_lists (Pos 11) baseline was 10/16 and gained +37.5 (rule) and +25.0 (full); timestamp_iso (Pos 12) gained -6.2 (full); cache_ttl (Pos 13) gained +0.0 (full); calendar_recurrence (Pos 14) gained +0.0 (full).
3. Placebo comparisons: config_merge P=62.5% (serving as noise check for the single-task family); event_ordering P=25.0%; money_rounding P=44.4%; config_lists P=37.5%.
4. Across the 10 evaluated families, full handbook gain averages +75.0 pts on the unknown end (Pos 1–5), compared to +4.9 pts on the ceiling end (Pos 10–14).
5. Cross-rule interference accounted for the full handbook scoring below rule-only in config_lists (Task 2055 importing unneeded ServiceError), idempotency_keys, and state_transitions, while sampling noise characterized config_merge, timestamp_iso, and cache_ttl.

## 5. Verification Artifacts & Links

- **Raw Outputs Directory:** [`results/stage3/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/raw)
- **Consolidated Results:** [`results/stage3/results.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/results.json)
- **Schedule File:** [`results/stage3/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage3/schedule_order.json)
- **Runner Script:** [`runner/run_stage3.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage3.py)
