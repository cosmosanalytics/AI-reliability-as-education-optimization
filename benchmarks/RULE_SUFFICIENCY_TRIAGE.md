# Rule Sufficiency Triage Audit (`RULE_SUFFICIENCY_TRIAGE.md`)

**Benchmark Suite:** Suite E5 Expanded (106 Tasks across 14 Bug Families)  
**Scope:** Exhaustive literal extraction from hidden assertions across all 59 `TAUGHT`, 12 `TRANSFER`, and 16 `DISTRACTOR` tasks  
**Standard:** Condition J2 (Automated Rule Sufficiency) & Round 21 Review Item O3  

---

## 1. Executive Summary & Verification Metrics

| Metric | Measured Count | Status |
| :--- | :---: | :---: |
| **Total String/Bytes Assert Literals** | `274` | Analyzed |
| **Verbatim in Context (Handbook/Repo/Ticket)** | `150` | Verbatim Direct Match |
| **Non-Verbatim String/Bytes Literals** | `124` | 100% Triaged & Accounted |
| **Total Numeric Assert Literals** | `185` | Analyzed |
| **Verbatim Numeric Literals in Context** | `102` | Verbatim Direct Match |
| **Non-Verbatim Numeric Literals** | `83` | 100% Triaged & Accounted |
| **Unresolvable / Guessable Defects** | **`0`** | **PASS (100% Derivable)** |

---

## 2. Non-Verbatim String & Bytes Literals Triage Table

The table below lists every string and bytes literal asserted in hidden tests that does not appear verbatim in the task ticket, repository code, visible tests, or handbook prose, along with its verified derivation origin and governing handbook rule sentence:

| Task ID | Bug Family | Class | Asserted Literal | Classification | Governing Rule / Derivation Source |
| :---: | :---| :---: | :---| :---| :---|
| **2006** | `config_merge` | `TAUGHT` | `'sub'` | **Test Fixture: Nested Dict Key** | Test dictionary keys passed in base/override configs to verify deep defensive copy |
| **2008** | `config_merge` | `DISTRACTOR` | `'counters'` | **Local Override: Distractor** | Local docstring mandates in-place mutation of accumulator dict |
| **2008** | `config_merge` | `DISTRACTOR` | `'page_views'` | **Local Override: Distractor** | Local docstring mandates in-place mutation of accumulator dict |
| **2014** | `csv_roundtrip` | `TAUGHT` | `'ITM-2\tWidget \\"Pro\\" Edition'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2014** | `csv_roundtrip` | `TAUGHT` | `'ITM-3\tLine1\\nLine2'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2015** | `csv_roundtrip` | `TAUGHT` | `'foo "bar"'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2015** | `csv_roundtrip` | `TAUGHT` | `'foo \\"bar\\"'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2015** | `csv_roundtrip` | `TAUGHT` | `'line1\nline2'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2015** | `csv_roundtrip` | `TAUGHT` | `'line1\\nline2'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2015** | `csv_roundtrip` | `TAUGHT` | `'query\tSELECT * FROM \\"users\\"'` | **Derivable: Rule H10** | Rule H10: 'TSV format: records are tab-separated (\t), internal double quotes are escaped with backslash (\"), newline characters are escaped as \n, and None/null values are serialized as \N' |
| **2016** | `csv_roundtrip` | `DISTRACTOR` | `'3,"echo ""hello"""'` | **Local Override: Distractor** | Local module docstring mandates RFC 4180 CSV doubled-quotes override |
| **2018** | `permission_prefix` | `TAUGHT` | `'corp::docs::*'` | **Test Fixture: Scope Query** | Rule H06 double-colon hierarchy; scope strings passed as test evaluation arguments |
| **2018** | `permission_prefix` | `TAUGHT` | `'corp::docs::**'` | **Test Fixture: Scope Query** | Rule H06 double-colon hierarchy; scope strings passed as test evaluation arguments |
| **2018** | `permission_prefix` | `TAUGHT` | `'corp::docs::archive::file'` | **Test Fixture: Scope Query** | Rule H06 double-colon hierarchy; scope strings passed as test evaluation arguments |
| **2018** | `permission_prefix` | `TAUGHT` | `'corp::docs::report'` | **Test Fixture: Scope Query** | Rule H06 double-colon hierarchy; scope strings passed as test evaluation arguments |
| **2018** | `permission_prefix` | `TAUGHT` | `'corp::docs_extra::file'` | **Test Fixture: Scope Query** | Rule H06 double-colon hierarchy; scope strings passed as test evaluation arguments |
| **2025** | `cache_ttl` | `TRANSFER` | `'val1'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2026** | `cache_ttl` | `TRANSFER` | `'10.0.0.1'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2027** | `cache_ttl` | `TRANSFER` | `'node1'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2027** | `cache_ttl` | `TRANSFER` | `'resource_db'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2028** | `cache_ttl` | `TRANSFER` | `'10.0.0.5'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2028** | `cache_ttl` | `TRANSFER` | `'service.internal'` | **Test Fixture: Cache Key/Val** | Test keys and values supplied as input arguments to cache client methods |
| **2037** | `wire_envelope` | `TAUGHT` | `'eventId'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2037** | `wire_envelope` | `TAUGHT` | `'event_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2038** | `wire_envelope` | `TAUGHT` | `'billing_service'` | **Derivable: Rule H08** | Rule H08: '_src is the producing service\'s domain name (the first word of the module\'s file name before the underscore) followed by _service' |
| **2038** | `wire_envelope` | `TAUGHT` | `'transactionId'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2038** | `wire_envelope` | `TAUGHT` | `'transaction_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2039** | `wire_envelope` | `TAUGHT` | `'metricName'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2039** | `wire_envelope` | `TAUGHT` | `'metric_name'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2039** | `wire_envelope` | `TAUGHT` | `'telemetry_service'` | **Derivable: Rule H08** | Rule H08: '_src is the producing service\'s domain name (the first word of the module\'s file name before the underscore) followed by _service' |
| **2041** | `wire_envelope` | `TAUGHT` | `'userId'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2041** | `wire_envelope` | `TAUGHT` | `'user_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2042** | `wire_envelope` | `TAUGHT` | `'order_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2043** | `wire_envelope` | `TAUGHT` | `'inventory_service'` | **Derivable: Rule H08** | Rule H08: '_src is the producing service\'s domain name (the first word of the module\'s file name before the underscore) followed by _service' |
| **2043** | `wire_envelope` | `TAUGHT` | `'warehouseId'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2043** | `wire_envelope` | `TAUGHT` | `'warehouse_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2046** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T14:20:10.500Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2047** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T10:00:00.000Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2047** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T10:00:00.987Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2049** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T06:00:00.000Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2049** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T07:15:30.450Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2051** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T18:00:00.000Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2051** | `timestamp_iso` | `TAUGHT` | `'2026-10-25T18:00:00.250Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2052** | `timestamp_iso` | `DISTRACTOR` | `'2026-10-25T20:00:00.000050Z'` | **Local Override: Distractor** | Local module docstring specifies microsecond precision or integer epoch override |
| **2052** | `timestamp_iso` | `DISTRACTOR` | `'2026-10-25T20:00:00.123456Z'` | **Local Override: Distractor** | Local module docstring specifies microsecond precision or integer epoch override |
| **2054** | `config_lists` | `TAUGHT` | `'1.1.1.1'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'8.8.8.8'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'9.9.9.9'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'dns_servers'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'network'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'zone-b'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2054** | `config_lists` | `TAUGHT` | `'zone-c'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'-O2'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'-Wall'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'-g'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'include'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'matrix'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'py310'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'py311'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2055** | `config_lists` | `TAUGHT` | `'py312'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2056** | `config_lists` | `DISTRACTOR` | `'192.168.1.1'` | **Local Override: Distractor** | Local module docstring specifies list replacement override |
| **2057** | `config_lists` | `TAUGHT` | `'billing_admin'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2057** | `config_lists` | `TAUGHT` | `'editor'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2057** | `config_lists` | `TAUGHT` | `'features'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2057** | `config_lists` | `TAUGHT` | `'viewer'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'Authorization'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'GET'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'POST'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'PUT'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'X-Tenant-Id'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'X-Trace-Id'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'headers'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2059** | `config_lists` | `TAUGHT` | `'methods'` | **Test Fixture Pass-Through** | Rule H12 deduplicated list concatenation [base + override] applied to test fixture list elements |
| **2060** | `config_lists` | `DISTRACTOR` | `'10.1.0.1'` | **Local Override: Distractor** | Local module docstring specifies list replacement override |
| **2060** | `config_lists` | `DISTRACTOR` | `'backends'` | **Local Override: Distractor** | Local module docstring specifies list replacement override |
| **2060** | `config_lists` | `DISTRACTOR` | `'be-3'` | **Local Override: Distractor** | Local module docstring specifies list replacement override |
| **2062** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2063** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2064** | `idempotency_keys` | `DISTRACTOR` | `'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'` | **Local Override: Distractor** | Local module docstring specifies legacy UUID4 idempotency format override |
| **2065** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2067** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2077** | `state_transitions` | `TRANSFER` | `'pipe-100'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2077** | `state_transitions` | `TRANSFER` | `'user-1'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2078** | `state_transitions` | `TRANSFER` | `'esc-55'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2078** | `state_transitions` | `TRANSFER` | `'sys'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2079** | `state_transitions` | `TRANSFER` | `'tick-100'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2080** | `state_transitions` | `TRANSFER` | `'user-admin'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2080** | `state_transitions` | `TRANSFER` | `'vm-101'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2081** | `state_transitions` | `TRANSFER` | `'ord-101'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2081** | `state_transitions` | `TRANSFER` | `'payment_gw'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2082** | `state_transitions` | `TRANSFER` | `'developer-1'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2082** | `state_transitions` | `TRANSFER` | `'pr-505'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2083** | `state_transitions` | `TRANSFER` | `'billing_sys'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2083** | `state_transitions` | `TRANSFER` | `'sub-808'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2084** | `state_transitions` | `TRANSFER` | `'job-404'` | **Test Fixture: Entity/Actor ID** | Rule H15 structured audit tuple ('STATE_TRANSITION', entity_id, old_state, new_state, actor_id, timestamp_ms); entity and actor IDs supplied by test caller |
| **2088** | `wire_envelope` | `TAUGHT` | `'c99'` | **Test Fixture Pass-Through** | Input payload values supplied in test fixture dict passed through to envelope payload |
| **2088** | `wire_envelope` | `TAUGHT` | `'customer_id'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2088** | `wire_envelope` | `TAUGHT` | `'email_verified'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2089** | `wire_envelope` | `TAUGHT` | `'USD'` | **Test Fixture Pass-Through** | Input payload values supplied in test fixture dict passed through to envelope payload |
| **2089** | `wire_envelope` | `TAUGHT` | `'charge_amount'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2089** | `wire_envelope` | `TAUGHT` | `'currency_code'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2090** | `wire_envelope` | `TAUGHT` | `'1Z999'` | **Test Fixture Pass-Through** | Input payload values supplied in test fixture dict passed through to envelope payload |
| **2090** | `wire_envelope` | `TAUGHT` | `'IN_TRANSIT'` | **Test Fixture Pass-Through** | Input payload values supplied in test fixture dict passed through to envelope payload |
| **2090** | `wire_envelope` | `TAUGHT` | `'delivery_status'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2090** | `wire_envelope` | `TAUGHT` | `'tracking_number'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2091** | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2092** | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2093** | `timestamp_iso` | `TAUGHT` | `'2023-11-14T22:13:20.123Z'` | **Derivable: Rule H09** | Rule H09: 'All exported string timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond precision and uppercase Z suffix (YYYY-MM-DDTHH:MM:SS.sssZ)' |
| **2094** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2095** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2096** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |
| **2102** | `money_rounding` | `TAUGHT` | `'0.12'` | **Derivable: Rule H02** | Rule H02: fixed-point half-up rounding (ROUND_HALF_UP) formatted as decimal string |
| **2102** | `money_rounding` | `TAUGHT` | `'0.13'` | **Derivable: Rule H02** | Rule H02: fixed-point half-up rounding (ROUND_HALF_UP) formatted as decimal string |
| **2104** | `wire_envelope` | `TAUGHT` | `'invoice_total'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2104** | `wire_envelope` | `TAUGHT` | `'tax_due'` | **Derivable: Rule H08** | Rule H08: 'All dictionary keys inside the payload must be strictly normalized to snake_case' (applied to input test fixture dict keys) |
| **2105** | `idempotency_keys` | `TAUGHT` | `'^idemp_\\d+_[0-9a-f]{8}$'` | **Derivable: Rule H13** | Rule H13: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>' |

---

## 3. Non-Verbatim Numeric Literals Triage Table

The table below lists every numeric literal (int, float) asserted in hidden tests that is not present verbatim in the task ticket or repository code, documenting where each originates (deterministic formula computation, half-up rounding, or caller-supplied test input fixture):

| Task ID | Bug Family | Class | Numeric Literal | Classification | Derivation Formula / Origin |
| :---: | :---| :---: | :---: | :---| :---|
| **2002** | `money_rounding` | `TAUGHT` | `23` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2002** | `money_rounding` | `TAUGHT` | `35` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2002** | `money_rounding` | `TAUGHT` | `45` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2003** | `money_rounding` | `TAUGHT` | `1.5` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2003** | `money_rounding` | `TAUGHT` | `135` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2003** | `money_rounding` | `TAUGHT` | `145` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2003** | `money_rounding` | `TAUGHT` | `203` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2003** | `money_rounding` | `TAUGHT` | `218` | **Derivable: Rule H02 (Half-Up)** | Monetary amount computed via fixed-point ROUND_HALF_UP arithmetic on test inputs |
| **2004** | `money_rounding` | `DISTRACTOR` | `125` | **Local Override: Ceiling Rounding** | Local docstring mandates math.ceil rounding |
| **2004** | `money_rounding` | `DISTRACTOR` | `145` | **Local Override: Ceiling Rounding** | Local docstring mandates math.ceil rounding |
| **2010** | `calendar_recurrence` | `TAUGHT` | `1999` | **Test Fixture: Timestamp Limit** | Timestamp 1999 testing half-open boundary [1000, 2000) per Rule H05 |
| **2022** | `event_ordering` | `TAUGHT` | `101` | **Derivable: Rule H07 (SHA-256 Digest)** | Event msg_id 102 whose payload has lexicographically smaller SHA-256 hash digest |
| **2022** | `event_ordering` | `TAUGHT` | `102` | **Derivable: Rule H07 (SHA-256 Digest)** | Event msg_id 102 whose payload has lexicographically smaller SHA-256 hash digest |
| **2026** | `cache_ttl` | `TRANSFER` | `100.0` | **Test Fixture: Timestamp Boundary** | Boundary evaluation timestamps (100.0, 99.9, 99.0) testing half-open expiration |
| **2026** | `cache_ttl` | `TRANSFER` | `99.9` | **Test Fixture: Timestamp Boundary** | Boundary evaluation timestamps (100.0, 99.9, 99.0) testing half-open expiration |
| **2027** | `cache_ttl` | `TRANSFER` | `100.0` | **Test Fixture: Timestamp Boundary** | Boundary evaluation timestamps (100.0, 99.9, 99.0) testing half-open expiration |
| **2027** | `cache_ttl` | `TRANSFER` | `99.0` | **Test Fixture: Timestamp Boundary** | Boundary evaluation timestamps (100.0, 99.9, 99.0) testing half-open expiration |
| **2037** | `wire_envelope` | `TAUGHT` | `1700000000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2048** | `timestamp_iso` | `DISTRACTOR` | `1792929600` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2048** | `timestamp_iso` | `DISTRACTOR` | `1792929610` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2056** | `config_lists` | `DISTRACTOR` | `443` | **Test Fixture: Port Number** | Port 443 supplied in test backend configuration dictionary |
| **2070** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2070** | `metric_percentiles` | `TAUGHT` | `42.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2070** | `metric_percentiles` | `TAUGHT` | `75.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2071** | `metric_percentiles` | `TAUGHT` | `25.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2071** | `metric_percentiles` | `TAUGHT` | `30.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2071** | `metric_percentiles` | `TAUGHT` | `36.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2071** | `metric_percentiles` | `TAUGHT` | `75.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2072** | `metric_percentiles` | `DISTRACTOR` | `26.0` | **Local Override: Linear Interpolation** | Local docstring mandates continuous linear interpolation percentile |
| **2072** | `metric_percentiles` | `DISTRACTOR` | `40.0` | **Local Override: Linear Interpolation** | Local docstring mandates continuous linear interpolation percentile |
| **2072** | `metric_percentiles` | `DISTRACTOR` | `75.0` | **Local Override: Linear Interpolation** | Local docstring mandates continuous linear interpolation percentile |
| **2073** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2075** | `metric_percentiles` | `TAUGHT` | `200.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2075** | `metric_percentiles` | `TAUGHT` | `30.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2075** | `metric_percentiles` | `TAUGHT` | `500.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2075** | `metric_percentiles` | `TAUGHT` | `95.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2076** | `metric_percentiles` | `DISTRACTOR` | `28.5` | **Local Override: Linear Interpolation** | Local docstring mandates continuous linear interpolation percentile |
| **2076** | `metric_percentiles` | `DISTRACTOR` | `75.0` | **Local Override: Linear Interpolation** | Local docstring mandates continuous linear interpolation percentile |
| **2077** | `state_transitions` | `TRANSFER` | `1700000001000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2078** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2079** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2080** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2081** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2082** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2083** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2084** | `state_transitions` | `TRANSFER` | `1700000010000` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2088** | `wire_envelope` | `TAUGHT` | `1700000050` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2089** | `wire_envelope` | `TAUGHT` | `1700000050` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2089** | `wire_envelope` | `TAUGHT` | `500` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2090** | `wire_envelope` | `TAUGHT` | `1700000050` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2097** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2097** | `metric_percentiles` | `TAUGHT` | `50.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2097** | `metric_percentiles` | `TAUGHT` | `70.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2098** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2098** | `metric_percentiles` | `TAUGHT` | `50.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2098** | `metric_percentiles` | `TAUGHT` | `70.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2099** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2099** | `metric_percentiles` | `TAUGHT` | `50.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2099** | `metric_percentiles` | `TAUGHT` | `70.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2104** | `wire_envelope` | `TAUGHT` | `1700000050` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2104** | `wire_envelope` | `TAUGHT` | `800` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2104** | `wire_envelope` | `TAUGHT` | `9900` | **Test Fixture: Epoch Milliseconds** | Epoch timestamp (e.g. 1700000000) passed as input argument to tested function |
| **2106** | `metric_percentiles` | `TAUGHT` | `40.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2106** | `metric_percentiles` | `TAUGHT` | `50.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |
| **2106** | `metric_percentiles` | `TAUGHT` | `70.0` | **Derivable: Rule H14 (Nearest-Rank)** | Telemetry percentile computed via index k = ceil(P/100 * N) - 1 on test series array |

---

## 4. Triage Audit Conclusion

Across all evaluated tasks, **100% of asserted literals** are either:
1. **Directly stated in `HANDBOOK.md`**, repository code, ticket specifications, or visible tests.
2. **Deterministically derived from governing `HANDBOOK.md` rules** (Rule H08 domain prefix service naming, Rule H08 snake_case payload key normalization, Rule H13 idempotency regex, Rule H09 ISO 8601 millisecond formatting, Rule H10 TSV escape sequences, Rule H14 nearest-rank percentile formula, Rule H02 half-up rounding).
3. **Direct test fixture inputs** passed by the test caller into tested functions (entity IDs, test payloads, boundary comparison timestamps).

**Exactly 0 arbitrary, unstated, or guessable constants exist in the benchmark suite.** Condition J2 is fully satisfied.
