# Discarded Engineering Smoke Test (Round 23 Item B2)

**Status:** DISCARDED ENGINEERING CHECK  
**Purpose:** Measure empirical token consumption (in, out, thinking), API call counts, and wall-clock execution time across three representative scaffolding cells on 3 Tune tasks, to establish empirical budget extrapolation and hard-stop caps prior to full screening execution.

**Crucial Experimental Invariants:**
1. These outputs are **engineering checks only** and are **NOT part of the screening data**.
2. Seed: `seed=99999` (guaranteed distinct from all screening seeds).
3. Evaluated Tasks: 2001 (`money_rounding`), 2005 (`config_merge`), 2013 (`csv_roundtrip`).
4. Temperature: `0.7`, Model: `gemini-2.5-flash`, Thinking Budget: `2048`, Max Output: `16384`.
