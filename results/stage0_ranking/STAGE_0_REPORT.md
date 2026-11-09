# Stage 0 Ranking Report: Baseline (B0) Performance

- **Protocol:** Staged Testing Protocol for Antigravity (Stage 0: Ranking)
- **Date / Time:** 2026-10-26 15:01:45 UTC
- **Frozen Model:** `gemini-2.5-flash`
- **Inference Parameters:** `temperature=0.7`, `top_p=0.95`, `max_output_tokens=16384`, `thinking_budget=2048`
- **Arm:** `B0` (Intro `briefs/C0000.md` only; zero tools, zero retries, single call)
- **Total Attempts Executed:** 218/218
- **Overall Strict Pass Rate:** 99/218 (45.41%)
- **Tokens Billed:** Input=191,420, Output=95,877, Thinking=307,281, Total=594,578
- **Total Wall-Clock Run Duration:** ~337s (5m 37s across 8 parallel workers)

## 1. Family Baseline Ranking Table

Display position 1 = lowest baseline pass rate (greatest lack of unaided knowledge, highest headroom for handbook gain).
Ties share a rank; display order broken by earlier pilot rank on Taught/Transfer tasks (`results/pilot_calibration/rows.json`), then alphabetically.

| Pos | Tied Rank | Bug Family | Rule ID | Tasks Used | k / n | Baseline (%) | Pilot Rank (Taught/Transfer) | Confidence Note |
|:---:|:---:|:---|:---:|:---|:---:|:---:|:---:|:---|
| **1** | 1 | `state_transitions` | H15 | 2077;2078;2079;2080 | 0/16 | **0.00%** | 1 | Standard |
| **2** | 1 | `idempotency_keys` | H13 | 2062;2063;2065;2067 | 0/16 | **0.00%** | 5 | Standard |
| **3** | 1 | `service_errors` | H04 | 2030;2031;2033;2035 | 0/16 | **0.00%** | 7 | Standard |
| **4** | 4 | `config_merge` | H03 | 2006 | 1/8 | **12.50%** | 11 | **Low Confidence** (1 task, 8 att: 1/8 vs 5/6 pilot) |
| **5** | 5 | `event_ordering` | H07 | 2022;2024 | 4/16 | **25.00%** | 2 | Standard |
| **6** | 5 | `wire_envelope` | H08 | 2037;2038;2039;2041 | 4/16 | **25.00%** | 3 | Standard |
| **7** | 7 | `csv_roundtrip` | H10 | 2014;2015;2100;2101 | 6/16 | **37.50%** | 4 | Standard |
| **8** | 8 | `permission_prefix` | H06 | 2018;2020 | 7/16 | **43.75%** | 6 | Standard |
| **9** | 9 | `metric_percentiles` | H14 | 2070;2071;2073;2075 | 9/16 | **56.25%** | 9 | **Low Confidence** (narrow 1-2 pass margin across adjacent families: 56.25% - 62.50%) |
| **10** | 10 | `money_rounding` | H02 | 2002;2003;2102 | 11/18 | **61.11%** | 10 | **Low Confidence** (narrow 1-2 pass margin across adjacent families: 56.25% - 62.50%) |
| **11** | 11 | `config_lists` | H12 | 2054;2055;2057;2059 | 10/16 | **62.50%** | 8 | **Low Confidence** (narrow 1-2 pass margin across adjacent families: 56.25% - 62.50%) |
| **12** | 12 | `timestamp_iso` | H09 | 2046;2047;2049;2051 | 15/16 | **93.75%** | 12 | Standard |
| **13** | 13 | `cache_ttl` | H11 | 2025;2026;2027;2028 | 16/16 | **100.00%** | 13 | Standard |
| **14** | 13 | `calendar_recurrence` | H05 | 2010;2012 | 16/16 | **100.00%** | 14 | Standard |

## 2. Stage Plan Assignments (By Display Position)

To avoid ambiguity from tied ranks, protocol stages are partitioned strictly by display position:

- **Stage 1 (One family on each end):**
  - Unknown end (Pos 1): `state_transitions` (Rule H15)
  - Ceiling end (Pos 14): `calendar_recurrence` (Rule H05)
- **Stage 2 (Two more families on each end):**
  - Unknown end (Pos 2–3): `idempotency_keys` (Rule H13), `service_errors` (Rule H04)
  - Ceiling end (Pos 12–13): `timestamp_iso` (Rule H09), `cache_ttl` (Rule H11)
- **Stage 3 (Two more families on each end):**
  - Unknown end (Pos 4–5): `config_merge` (Rule H03), `event_ordering` (Rule H07)
  - Ceiling end (Pos 10–11): `money_rounding` (Rule H02), `config_lists` (Rule H12)
- **Stage 4 (Remaining 4 middle families):**
  - Middle (Pos 6–9): `wire_envelope` (Rule H08), `csv_roundtrip` (Rule H10), `permission_prefix` (Rule H06), `metric_percentiles` (Rule H14)

## 3. Per-Task Breakdown

| Family | Task ID | Description | Class | Passes (k/n) | Pass Rate (%) |
|:---|:---:|:---|:---:|:---:|:---:|
| `state_transitions` | 2077 | Deployment Pipeline Lifecycle | `TRANSFER` | 0/4 | 0.0% |
| `state_transitions` | 2078 | Payment Escrow Lifecycle | `TRANSFER` | 0/4 | 0.0% |
| `state_transitions` | 2079 | Support Ticket Workflow | `TRANSFER` | 0/4 | 0.0% |
| `state_transitions` | 2080 | Cloud Compute Instance Lifecycle | `TRANSFER` | 0/4 | 0.0% |
| `idempotency_keys` | 2062 | Order Fulfillment RPC Client | `TAUGHT` | 0/4 | 0.0% |
| `idempotency_keys` | 2063 | Subscription Recurring Charge Request | `TAUGHT` | 0/4 | 0.0% |
| `idempotency_keys` | 2065 | Customer Refund Dispatcher | `TAUGHT` | 0/4 | 0.0% |
| `idempotency_keys` | 2067 | Cloud Virtual Machine Provisioning RPC | `TAUGHT` | 0/4 | 0.0% |
| `service_errors` | 2030 | Tenant Scope Authorization Guard | `TAUGHT` | 0/4 | 0.0% |
| `service_errors` | 2031 | Payload Schema Validation Pipeline | `TAUGHT` | 0/4 | 0.0% |
| `service_errors` | 2033 | Concurrent Document Lock Manager | `TAUGHT` | 0/4 | 0.0% |
| `service_errors` | 2035 | Burst Quota Throttling Guard | `TAUGHT` | 0/4 | 0.0% |
| `config_merge` | 2006 | Database Pool Settings | `TAUGHT` | 1/8 | 12.5% |
| `event_ordering` | 2022 | Notification Batch Sorter | `TAUGHT` | 4/8 | 50.0% |
| `event_ordering` | 2024 | Event Stream Ingestion Sequencer | `TAUGHT` | 0/8 | 0.0% |
| `wire_envelope` | 2037 | Audit Event Wire Formatter | `TAUGHT` | 2/4 | 50.0% |
| `wire_envelope` | 2038 | Billing Transaction Message Emitter | `TAUGHT` | 1/4 | 25.0% |
| `wire_envelope` | 2039 | Telemetry Metric Stream Normalizer | `TAUGHT` | 0/4 | 0.0% |
| `wire_envelope` | 2041 | User Activity Event Dispatcher | `TAUGHT` | 1/4 | 25.0% |
| `csv_roundtrip` | 2014 | Order Item TSV Serializer | `TAUGHT` | 2/4 | 50.0% |
| `csv_roundtrip` | 2015 | Batch Metric TSV Downloader | `TAUGHT` | 0/4 | 0.0% |
| `csv_roundtrip` | 2100 | Transaction Ledger TSV Exporter | `TAUGHT` | 2/4 | 50.0% |
| `csv_roundtrip` | 2101 | System Log TSV Serializer | `TAUGHT` | 2/4 | 50.0% |
| `permission_prefix` | 2018 | Document Store Scope RBAC Filter | `TAUGHT` | 0/8 | 0.0% |
| `permission_prefix` | 2020 | Webhook Subscription Scope Enforcer | `TAUGHT` | 7/8 | 87.5% |
| `metric_percentiles` | 2070 | Database Query Duration Monitor | `TAUGHT` | 1/4 | 25.0% |
| `metric_percentiles` | 2071 | Microservice RPC Response Timer | `TAUGHT` | 3/4 | 75.0% |
| `metric_percentiles` | 2073 | Cache Lookup Latency Reporter | `TAUGHT` | 2/4 | 50.0% |
| `metric_percentiles` | 2075 | Storage IO Wait Time Tracker | `TAUGHT` | 3/4 | 75.0% |
| `money_rounding` | 2002 | Invoice Discount Allocation | `TAUGHT` | 0/6 | 0.0% |
| `money_rounding` | 2003 | Multi-Currency Fee Conversion | `TAUGHT` | 5/6 | 83.3% |
| `money_rounding` | 2102 | Merchant Settlement Fee Calculator | `TAUGHT` | 6/6 | 100.0% |
| `config_lists` | 2054 | Cloud Infrastructure Cluster Specification Merge | `TAUGHT` | 3/4 | 75.0% |
| `config_lists` | 2055 | CI/CD Pipeline Step Arguments Merger | `TAUGHT` | 1/4 | 25.0% |
| `config_lists` | 2057 | Application Feature Gate Setting Aggregator | `TAUGHT` | 3/4 | 75.0% |
| `config_lists` | 2059 | Service Mesh Route Matcher Configurator | `TAUGHT` | 3/4 | 75.0% |
| `timestamp_iso` | 2046 | Telemetry Log Serializer | `TAUGHT` | 4/4 | 100.0% |
| `timestamp_iso` | 2047 | Webhook Delivery Envelope | `TAUGHT` | 4/4 | 100.0% |
| `timestamp_iso` | 2049 | Database Snapshot Metadata Generator | `TAUGHT` | 4/4 | 100.0% |
| `timestamp_iso` | 2051 | Security Token Exchange Ledger | `TAUGHT` | 3/4 | 75.0% |
| `cache_ttl` | 2025 | In-Memory Token Cache | `TRANSFER` | 4/4 | 100.0% |
| `cache_ttl` | 2026 | API Rate Limit Session Store | `TRANSFER` | 4/4 | 100.0% |
| `cache_ttl` | 2027 | Distributed Lease Expiry Guard | `TRANSFER` | 4/4 | 100.0% |
| `cache_ttl` | 2028 | DNS Cache TTL Resolver | `TRANSFER` | 4/4 | 100.0% |
| `calendar_recurrence` | 2010 | Subscription Active Window Evaluator | `TAUGHT` | 8/8 | 100.0% |
| `calendar_recurrence` | 2012 | Audit Log Retention Window | `TAUGHT` | 8/8 | 100.0% |

## 4. Protocol Compliance & Verification Artifacts

- **Raw Outputs Directory:** [`results/stage0_ranking/raw/`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage0_ranking/raw)
- **Schedule Order File:** [`results/stage0_ranking/schedule_order.json`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage0_ranking/schedule_order.json)
- **Consolidated CSV:** [`results/stage0_ranking/ranking.csv`](file:///C:/Users/richa/ai-engineering/repo_push/results/stage0_ranking/ranking.csv)
- **Runner Script:** [`runner/run_stage0_ranking.py`](file:///C:/Users/richa/ai-engineering/repo_push/runner/run_stage0_ranking.py)
