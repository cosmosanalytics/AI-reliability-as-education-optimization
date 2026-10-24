import re
T = []

def task(tid, group, name, rules, issue, repo, hidden, ref, visible=None, protected=(), forbidden=(), must_touch=(), maxlines=None, extra_variants=(), hidden_paths=None):
    vis = visible or [p for p in repo if p.startswith('tests/')]
    key = {'visible_paths': vis, 'protected': list(protected), 'forbidden': list(forbidden), 'must_touch': list(must_touch)}
    if maxlines: key['max_changed_lines'] = maxlines
    key['variants'] = [{'name': 'hidden tests', 'overlay': hidden, 'expect': 'pass', 'paths': hidden_paths or ['tests']}] + list(extra_variants)
    T.append(dict(id=tid, group=group, name=name, rules=rules, issue=issue, repo=repo, key=key, ref=ref))

# ---------------------------------------------------------------------------------------------------
# Task 801 (Diagnostic A: Runtime State & Overlapping Intervals - probes Tools u and Retry k)
# In static hand-tracing, agents often miss subtle boundary adjacency or open/closed interval merge logic.
# With a test runner (u+) or retry (k+), visible pytest immediately reveals the failing assertion.
# ---------------------------------------------------------------------------------------------------
task(801, 'State & Overlap', 'Sliding Window Timeline Merging', 'W01,W02,W03,W05,W14',
"""Bug report in timeline.py:
`merge_events(events, max_gap=0)` should merge half-open time intervals [start, end) that overlap
or are within `max_gap` seconds of each other. Each event is a dict `{'start': float, 'end': float, 'data': list}`.
Merged events should combine their `data` lists preserving event order.
Currently, the function:
1. Fails when events are unsorted by start time.
2. Incorrectly splits contiguous intervals when max_gap == 0.
3. Drops data payloads on multi-interval chains.
4. Raises TypeError if events list is empty (should return []).

Fix timeline.py. Do not modify the test suite in tests/.""",
{
'timeline.py': '''def merge_events(events, max_gap=0):
    """Merge half-open intervals [start, end) separated by <= max_gap.
    Each event has {'start': float, 'end': float, 'data': list}.
    Returns a new list of merged event dicts."""
    if len(events) == 0:
        raise TypeError("Empty events")
    
    # Buggy: assumes sorted, misses adjacent intervals when max_gap=0
    merged = []
    curr = dict(events[0])
    curr['data'] = list(curr.get('data', []))
    for ev in events[1:]:
        if ev['start'] < curr['end']:
            curr['end'] = max(curr['end'], ev['end'])
            curr['data'].extend(ev.get('data', []))
        else:
            merged.append(curr)
            curr = dict(ev)
            curr['data'] = list(curr.get('data', []))
    merged.append(curr)
    return merged
''',
'tests/test_timeline.py': '''from timeline import merge_events

def test_basic_overlap():
    evs = [
        {'start': 10.0, 'end': 20.0, 'data': ['a']},
        {'start': 15.0, 'end': 25.0, 'data': ['b']}
    ]
    res = merge_events(evs, max_gap=0)
    assert len(res) == 1
    assert res[0]['start'] == 10.0
    assert res[0]['end'] == 25.0
    assert res[0]['data'] == ['a', 'b']

def test_unsorted_and_empty():
    assert merge_events([], max_gap=0) == []
    evs = [
        {'start': 20.0, 'end': 30.0, 'data': ['b']},
        {'start': 10.0, 'end': 20.0, 'data': ['a']}
    ]
    res = merge_events(evs, max_gap=0)
    assert len(res) == 1
    assert res[0]['start'] == 10.0
    assert res[0]['end'] == 30.0
    assert res[0]['data'] == ['a', 'b']
'''
},
{
'tests/test_hidden_timeline.py': '''import pytest
from timeline import merge_events

def test_hidden_gap_and_chains():
    evs = [
        {'start': 0.0, 'end': 5.0, 'data': [1]},
        {'start': 7.0, 'end': 10.0, 'data': [2]},
        {'start': 12.0, 'end': 15.0, 'data': [3]}
    ]
    # gap 2.0 should bridge 5.0 to 7.0 and 10.0 to 12.0
    res = merge_events(evs, max_gap=2.0)
    assert len(res) == 1
    assert res[0]['start'] == 0.0
    assert res[0]['end'] == 15.0
    assert res[0]['data'] == [1, 2, 3]

def test_hidden_nested_subintervals():
    evs = [
        {'start': 1.0, 'end': 10.0, 'data': ['outer']},
        {'start': 2.0, 'end': 5.0, 'data': ['inner1']},
        {'start': 4.0, 'end': 8.0, 'data': ['inner2']}
    ]
    res = merge_events(evs, max_gap=0.0)
    assert len(res) == 1
    assert res[0]['start'] == 1.0
    assert res[0]['end'] == 10.0
    assert res[0]['data'] == ['outer', 'inner1', 'inner2']
'''
},
{
'timeline.py': '''def merge_events(events, max_gap=0):
    """Merge half-open intervals [start, end) separated by <= max_gap.
    Each event has {'start': float, 'end': float, 'data': list}.
    Returns a new list of merged event dicts."""
    if not events:
        return []
    
    sorted_evs = sorted(events, key=lambda x: (x['start'], x['end']))
    merged = []
    curr = {
        'start': float(sorted_evs[0]['start']),
        'end': float(sorted_evs[0]['end']),
        'data': list(sorted_evs[0].get('data', []))
    }
    
    for ev in sorted_evs[1:]:
        s = float(ev['start'])
        e = float(ev['end'])
        d = list(ev.get('data', []))
        
        if s <= curr['end'] + max_gap:
            curr['end'] = max(curr['end'], e)
            curr['data'].extend(d)
        else:
            merged.append(curr)
            curr = {'start': s, 'end': e, 'data': d}
    merged.append(curr)
    return merged
'''
},
protected=['tests/test_timeline.py']
)

# ---------------------------------------------------------------------------------------------------
# Task 802 (Diagnostic B: Boundary Conditions & Type Contracts - probes Review Checklist r)
# Static drafts commonly omit validation of negative quotas, float rate limits, or tie-break order.
# The review checklist (r2) explicitly requires checking negative numbers, zeros, and exception types.
# ---------------------------------------------------------------------------------------------------
task(802, 'Boundary & Contract', 'Rate Limiter Token Bucket Specification', 'W01,W02,W04,W05,W14',
"""Bug report in limiter.py:
The `TokenBucket` class needs to enforce strict contract invariants described in its specification:
1. `capacity` must be positive (> 0); raise ValueError if capacity <= 0.
2. `refill_rate` (tokens per second) must be positive (> 0); raise ValueError if refill_rate <= 0.
3. `consume(tokens)`: tokens must be positive integer (> 0). Raise ValueError if tokens <= 0 or not an int.
4. If sufficient tokens are available, return True and deduct; if not, return False and do not alter token count.
5. `current_tokens` must never exceed `capacity`.
6. Time elapsed must properly accrue tokens up to capacity based on monotonic time delta.

Currently, limiter.py allows negative capacities, truncates float tokens inconsistently, and fails on fractional refills.
Fix limiter.py. Do not modify tests/test_limiter.py.""",
{
'limiter.py': '''class TokenBucket:
    def __init__(self, capacity, refill_rate, initial_tokens=None):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity if initial_tokens is None else initial_tokens
        self.last_update = 0.0

    def consume(self, tokens=1):
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
''',
'tests/test_limiter.py': '''import pytest
from limiter import TokenBucket

def test_normal_consumption():
    tb = TokenBucket(10, 1.0, initial_tokens=10)
    assert tb.consume(5) is True
    assert tb.consume(6) is False
    assert tb.consume(5) is True
    assert tb.consume(1) is False

def test_invalid_construction():
    with pytest.raises(ValueError):
        TokenBucket(0, 1.0)
    with pytest.raises(ValueError):
        TokenBucket(10, -1.0)
'''
},
{
'tests/test_hidden_limiter.py': '''import pytest
from limiter import TokenBucket

def test_type_and_negative_consume():
    tb = TokenBucket(10, 2.0, initial_tokens=10)
    with pytest.raises(ValueError):
        tb.consume(0)
    with pytest.raises(ValueError):
        tb.consume(-3)
    with pytest.raises(ValueError):
        tb.consume(2.5)

def test_time_elapsed_refill():
    tb = TokenBucket(10, 5.0, initial_tokens=0)
    tb.last_update = 100.0
    tb.update_time(101.0) # 1 sec = +5 tokens
    assert tb.tokens == 5.0
    tb.update_time(103.0) # +2 sec = +10 tokens, capped at 10.0
    assert tb.tokens == 10.0
'''
},
{
'limiter.py': '''class TokenBucket:
    def __init__(self, capacity, refill_rate, initial_tokens=None):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("Refill rate must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        if initial_tokens is None:
            self.tokens = self.capacity
        else:
            if initial_tokens < 0:
                raise ValueError("Initial tokens cannot be negative")
            self.tokens = min(float(initial_tokens), self.capacity)
        self.last_update = 0.0

    def update_time(self, current_time):
        if self.last_update > 0.0 and current_time > self.last_update:
            delta = current_time - self.last_update
            self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)
        self.last_update = current_time

    def consume(self, tokens=1):
        if not isinstance(tokens, int) or isinstance(tokens, bool):
            raise ValueError("Tokens must be an integer")
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
'''
},
protected=['tests/test_limiter.py']
)

# ---------------------------------------------------------------------------------------------------
# Task 803 (Diagnostic C: Backward Compatibility & Sources - probes Sources s)
# Rule W08 states: "Existing callers that use old signature and old defaults must see the same results.
# Add new parameters as keyword arguments with defaults that preserve current behaviour."
# Without Rule W08 (s-), agents frequently alter positional parameter orders or break caller signatures.
# ---------------------------------------------------------------------------------------------------
task(803, 'Compatibility & Architecture', 'Config Parser Backward Compatibility', 'W01,W03,W05,W08,W14',
"""Bug report in settings.py:
The configuration loader `load_settings(filepath, env_prefix="APP_")` must be extended to support
optional `strict_types=False` and `fallback_dict=None`.
CRITICAL: Existing callers pass positional arguments `(filepath, env_prefix)`. Do not break existing callers!
Existing behavior:
- If filepath does not exist and fallback_dict is provided, return fallback_dict.
- If filepath does not exist and fallback_dict is None, raise FileNotFoundError.
- Parse key-value lines `KEY=VALUE`.
- If env_prefix is specified, strip it from environment variable overrides.
- When strict_types=True, convert integer values to int, booleans (true/false) to bool.
Do not modify tests/test_settings.py.""",
{
'settings.py': '''import os

def load_settings(filepath, env_prefix="APP_"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    cfg = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                cfg[k.strip()] = v.strip()
    return cfg
''',
'tests/test_settings.py': '''import os, tempfile
from settings import load_settings

def test_legacy_call():
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("HOST=localhost\\nPORT=8080\\n")
        path = f.name
    try:
        cfg = load_settings(path)
        assert cfg['HOST'] == 'localhost'
        assert cfg['PORT'] == '8080'
    finally:
        os.unlink(path)
'''
},
{
'tests/test_hidden_settings.py': '''import os, tempfile, pytest
from settings import load_settings

def test_backward_compatibility_args():
    # Calling with legacy positional arguments must succeed
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("DEBUG=true\\nWORKERS=4\\n")
        path = f.name
    try:
        cfg = load_settings(path, "APP_", False, None)
        assert cfg['DEBUG'] == 'true'
        assert cfg['WORKERS'] == '4'
    finally:
        os.unlink(path)

def test_strict_types_and_fallback():
    assert load_settings("/nonexistent_path_xyz", fallback_dict={"DEFAULT": 1}) == {"DEFAULT": 1}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("DEBUG=true\\nWORKERS=4\\nNAME=app\\n")
        path = f.name
    try:
        cfg = load_settings(path, strict_types=True)
        assert cfg['DEBUG'] is True
        assert cfg['WORKERS'] == 4
        assert cfg['NAME'] == 'app'
    finally:
        os.unlink(path)
'''
},
{
'settings.py': '''import os

def load_settings(filepath, env_prefix="APP_", strict_types=False, fallback_dict=None):
    if not os.path.exists(filepath):
        if fallback_dict is not None:
            return dict(fallback_dict)
        raise FileNotFoundError(filepath)
    
    cfg = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                if strict_types:
                    if v.lower() in ('true', 'yes'):
                        v = True
                    elif v.lower() in ('false', 'no'):
                        v = False
                    else:
                        try:
                            v = int(v)
                        except ValueError:
                            try:
                                v = float(v)
                            except ValueError:
                                pass
                cfg[k] = v
    return cfg
'''
},
protected=['tests/test_settings.py']
)

# ---------------------------------------------------------------------------------------------------
# Task 804 (Diagnostic D: Security & Containment - probes Sources W10 and Practice Examples p)
# Rule W10 states: "Never build SQL, shell commands or paths from untrusted text... resolve paths with
# os.path.realpath and check containment with os.path.commonpath."
# Worked examples (p3) show the exact idiom `os.path.commonpath([base_dir, target]) == base_dir`.
# Without W10 or worked examples, agents write naive `target.startswith(base_dir)` or `.. in path`.
# ---------------------------------------------------------------------------------------------------
task(804, 'Security & Containment', 'Safe File Storage Archive Sanitizer', 'W01,W03,W05,W10,W14',
"""Bug report in archive.py:
`safe_extract_member(base_dir, member_path)` must prevent directory traversal attacks.
Requirements:
1. `base_dir` is the canonical root directory.
2. `member_path` is an untrusted relative or absolute path from an archive.
3. Compute the destination path using `os.path.realpath`.
4. Enforce that the destination path is strictly contained within `base_dir` using `os.path.commonpath`.
   Prefix checking (e.g. `path.startswith(base_dir)`) is insecure against base folder naming attacks
   (e.g. `/var/app_fake` vs `/var/app`).
5. Raise PermissionError if the path attempts to escape base_dir.
6. Return the sanitized absolute path.
Do not modify tests/test_archive.py.""",
{
'archive.py': '''import os

def safe_extract_member(base_dir, member_path):
    # Insecure implementation: vulnerable to symlinks and prefix collision
    clean_base = os.path.abspath(base_dir)
    target = os.path.abspath(os.path.join(clean_base, member_path))
    if not target.startswith(clean_base):
        raise PermissionError("Path escape")
    return target
''',
'tests/test_archive.py': '''import os, pytest
from archive import safe_extract_member

def test_safe_normal_path():
    base = os.path.abspath("test_vault")
    target = safe_extract_member(base, "docs/readme.txt")
    assert target == os.path.join(base, "docs", "readme.txt")

def test_obvious_traversal():
    base = os.path.abspath("test_vault")
    with pytest.raises(PermissionError):
        safe_extract_member(base, "../secret.txt")
'''
},
{
'tests/test_hidden_archive.py': '''import os, pytest
from archive import safe_extract_member

def test_prefix_collision_bypass():
    # If base is /app/vault, /app/vault_attacker starts with /app/vault but is an escape!
    base = os.path.abspath("test_vault")
    sibling_attack = base + "_suffix/exploit.txt"
    rel_attack = "../" + os.path.basename(base) + "_suffix/exploit.txt"
    with pytest.raises(PermissionError):
        safe_extract_member(base, rel_attack)

def test_symlink_or_realpath_resolution():
    base = os.path.abspath("test_vault")
    # Multiple dotted components and root slashes
    with pytest.raises(PermissionError):
        safe_extract_member(base, "sub/../../outside.txt")
'''
},
{
'archive.py': '''import os

def safe_extract_member(base_dir, member_path):
    clean_base = os.path.realpath(base_dir)
    clean_member = member_path.lstrip('/' + chr(92))
    target = os.path.realpath(os.path.join(clean_base, clean_member))
    try:
        common = os.path.commonpath([clean_base, target])
    except ValueError:
        raise PermissionError("Cross-drive or invalid path escape")
    if common != clean_base or target == clean_base:
        raise PermissionError("Path escape outside base directory")
    return target
'''
},
protected=['tests/test_archive.py']
)
