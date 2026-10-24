import sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import tasks as _t
T = []
def task(tid, name, issue, repo, hidden, ref, protected):
    vis = [p for p in repo if p.startswith('tests/')]
    key = {'visible_paths': vis, 'protected': list(protected), 'forbidden': [], 'must_touch': [],
           'variants': [{'name': 'hidden tests', 'overlay': hidden, 'expect': 'pass', 'paths': ['tests']}]}
    T.append(dict(id=tid, group='Hard', name=name, rules='', issue=issue, repo=repo, key=key, ref=ref))

# 101 semver
task(101, 'Semver precedence',
 'Implement semver.py as documented in its docstrings. Follow Semantic Versioning 2.0.0 precedence rules exactly. Do not change the tests.',
 {'semver.py': '''def parse(v):
    """Parse "MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]" and return (major, minor, patch, prerelease_tuple, build_tuple).
    major/minor/patch are ints without leading zeros ("01" is invalid, "0" is fine). prerelease and build are dot-separated
    identifiers of [0-9A-Za-z-]; empty identifiers are invalid; numeric prerelease identifiers must not have leading zeros.
    prerelease_tuple holds ints for numeric identifiers and strs otherwise; build_tuple holds strs. Missing parts are ().
    Raise ValueError for anything invalid, including a leading "v", extra whitespace or non-str input."""
    raise NotImplementedError


def compare(a, b):
    """Return -1, 0 or 1 by semver precedence. Build metadata is ignored. A version with a prerelease has lower
    precedence than the same version without one. Prerelease identifiers compare left to right: numeric identifiers compare
    numerically, alphanumeric ones compare lexically in ASCII order, numeric identifiers always have lower precedence than
    alphanumeric ones, and when all shared identifiers are equal the longer prerelease is higher."""
    raise NotImplementedError


def sort_versions(versions, reverse=False):
    """Return a new list sorted by precedence (stable for equal precedence). Raise ValueError on any invalid entry."""
    raise NotImplementedError


def is_valid(v):
    """True if parse(v) would succeed, else False. Never raises."""
    raise NotImplementedError
''', 'tests/test_semver.py': '''from semver import compare

def test_basic():
    assert compare("1.0.0", "2.0.0") == -1
    assert compare("1.2.3", "1.2.3") == 0
'''},
 {'tests/test_hidden_semver.py': '''import pytest
from semver import parse, compare, sort_versions, is_valid

def test_parse():
    assert parse("1.2.3") == (1, 2, 3, (), ())
    assert parse("1.2.3-alpha.1+b.7") == (1, 2, 3, ("alpha", 1), ("b", "7"))
    assert parse("0.0.0-0") == (0, 0, 0, (0,), ())

@pytest.mark.parametrize("bad", ["", "1", "1.2", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "v1.2.3", " 1.2.3", "1.2.3 ",
    "1.2.3-", "1.2.3-a..b", "1.2.3-01", "1.2.3+", "1.2.3+a..b", "1.2.3-a_b", "-1.2.3", 123, None])
def test_invalid(bad):
    with pytest.raises(ValueError):
        parse(bad)
    assert is_valid(bad) is False

def test_prerelease_order():
    chain = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
    for i in range(len(chain) - 1):
        assert compare(chain[i], chain[i + 1]) == -1
        assert compare(chain[i + 1], chain[i]) == 1

def test_numeric_vs_alpha_and_ascii():
    assert compare("1.0.0-1", "1.0.0-a") == -1
    assert compare("1.0.0-B", "1.0.0-a") == -1
    assert compare("1.0.0-a.1", "1.0.0-a") == 1
    assert compare("1.0.0-2", "1.0.0-10") == -1

def test_build_ignored():
    assert compare("1.0.0+a", "1.0.0+b") == 0
    assert compare("1.0.0-x+1", "1.0.0-x") == 0

def test_numeric_fields():
    assert compare("1.10.0", "1.9.0") == 1
    assert compare("2.0.0", "10.0.0") == -1

def test_sort():
    vs = ["1.0.0", "1.0.0-rc.1", "0.9.9", "1.0.0-alpha", "1.0.0+b", "1.0.0+a"]
    assert sort_versions(vs) == ["0.9.9", "1.0.0-alpha", "1.0.0-rc.1", "1.0.0", "1.0.0+b", "1.0.0+a"]
    assert sort_versions(vs, reverse=True)[0] in ("1.0.0", "1.0.0+b", "1.0.0+a")
    assert vs[0] == "1.0.0"
    with pytest.raises(ValueError):
        sort_versions(["1.0.0", "nope"])
'''},
 {'semver.py': '''import re
_ID = re.compile(r"^[0-9A-Za-z-]+$")
_NUM = re.compile(r"^(0|[1-9][0-9]*)$")


def parse(v):
    if not isinstance(v, str):
        raise ValueError("version must be a str")
    m = re.match(r"^([^-+]+)\\.([^-+]+)\\.([^-+]+)(?:-([^+]*))?(?:\\+(.*))?$", v)
    if not m or v != v.strip() or "\\n" in v:
        raise ValueError("invalid version: %r" % (v,))
    nums = []
    for part in m.group(1, 2, 3):
        if not _NUM.match(part):
            raise ValueError("invalid number: %r" % (part,))
        nums.append(int(part))
    pre = ()
    if m.group(4) is not None:
        ids = m.group(4).split(".")
        out = []
        for i in ids:
            if not i or not _ID.match(i):
                raise ValueError("invalid prerelease identifier")
            if i.isdigit():
                if not _NUM.match(i):
                    raise ValueError("leading zero in prerelease")
                out.append(int(i))
            else:
                out.append(i)
        pre = tuple(out)
    build = ()
    if m.group(5) is not None:
        ids = m.group(5).split(".")
        for i in ids:
            if not i or not _ID.match(i):
                raise ValueError("invalid build identifier")
        build = tuple(ids)
    return (nums[0], nums[1], nums[2], pre, build)


def _cmp_pre(a, b):
    if not a and not b:
        return 0
    if not a:
        return 1
    if not b:
        return -1
    for x, y in zip(a, b):
        if x == y:
            continue
        xi, yi = isinstance(x, int), isinstance(y, int)
        if xi and yi:
            return -1 if x < y else 1
        if xi:
            return -1
        if yi:
            return 1
        return -1 if x < y else 1
    if len(a) == len(b):
        return 0
    return -1 if len(a) < len(b) else 1


def compare(a, b):
    pa, pb = parse(a), parse(b)
    for x, y in zip(pa[:3], pb[:3]):
        if x != y:
            return -1 if x < y else 1
    return _cmp_pre(pa[3], pb[3])


def sort_versions(versions, reverse=False):
    import functools
    vs = list(versions)
    for v in vs:
        parse(v)
    return sorted(vs, key=functools.cmp_to_key(compare), reverse=reverse)


def is_valid(v):
    try:
        parse(v)
        return True
    except ValueError:
        return False
'''}, ['tests/test_semver.py'])

# 102 interval set
task(102, 'Half-open interval set',
 'Implement IntervalSet in intervals.py as documented. Do not change the tests.',
 {'intervals.py': '''class IntervalSet:
    """A set of integers stored as sorted, non-overlapping, non-adjacent half-open ranges [start, end).

    add(start, end): add the range. Ranges that overlap OR touch (end == next start) are merged. start == end is a no-op.
    start > end raises ValueError.
    remove(start, end): remove the range, splitting existing ranges if needed. Same rules for start == end and start > end.
    contains(x): True if x is in the set (start <= x < end).
    ranges(): list of (start, end) tuples sorted by start; the internal state must not be modifiable through it.
    total(): number of integers covered.
    gaps(lo, hi): list of (start, end) tuples that are NOT covered inside [lo, hi), clipped to it, sorted; empty when lo >= hi.
    __len__ returns the number of stored ranges. __eq__ compares ranges() with another IntervalSet; other types are not equal.
    Arguments must be ints (bool is not accepted); anything else raises TypeError."""

    def __init__(self):
        raise NotImplementedError
''', 'tests/test_intervals.py': '''from intervals import IntervalSet

def test_add():
    s = IntervalSet()
    s.add(1, 3); s.add(3, 5)
    assert s.ranges() == [(1, 5)]
'''},
 {'tests/test_hidden_intervals.py': '''import pytest
from intervals import IntervalSet

def mk(*rs):
    s = IntervalSet()
    for a, b in rs:
        s.add(a, b)
    return s

def test_merge_touch_overlap():
    assert mk((1, 3), (3, 5)).ranges() == [(1, 5)]
    assert mk((1, 4), (2, 6)).ranges() == [(1, 6)]
    assert mk((1, 2), (3, 4)).ranges() == [(1, 2), (3, 4)]
    assert mk((5, 6), (1, 2), (2, 5)).ranges() == [(1, 6)]
    assert mk((1, 10), (3, 4)).ranges() == [(1, 10)]

def test_empty_and_errors():
    s = mk((2, 2))
    assert s.ranges() == [] and len(s) == 0 and s.total() == 0
    with pytest.raises(ValueError):
        s.add(3, 2)
    with pytest.raises(ValueError):
        s.remove(3, 2)
    for bad in (1.0, "1", None, True):
        with pytest.raises(TypeError):
            s.add(bad, 5)
        with pytest.raises(TypeError):
            s.add(0, bad)
        with pytest.raises(TypeError):
            s.contains(bad)

def test_remove_split():
    s = mk((0, 10))
    s.remove(3, 5)
    assert s.ranges() == [(0, 3), (5, 10)]
    s.remove(0, 3)
    assert s.ranges() == [(5, 10)]
    s.remove(8, 20)
    assert s.ranges() == [(5, 8)]
    s.remove(5, 8)
    assert s.ranges() == []
    s.remove(1, 1)
    s.remove(-5, 100)

def test_remove_multiple():
    s = mk((0, 2), (4, 6), (8, 10))
    s.remove(1, 9)
    assert s.ranges() == [(0, 1), (9, 10)]

def test_contains_total():
    s = mk((1, 3), (10, 12))
    assert [x for x in range(0, 14) if s.contains(x)] == [1, 2, 10, 11]
    assert s.total() == 4 and len(s) == 2

def test_gaps():
    s = mk((2, 4), (6, 8))
    assert s.gaps(0, 10) == [(0, 2), (4, 6), (8, 10)]
    assert s.gaps(3, 7) == [(4, 6)]
    assert s.gaps(2, 4) == []
    assert s.gaps(5, 5) == [] and s.gaps(7, 1) == []
    assert IntervalSet().gaps(1, 3) == [(1, 3)]

def test_ranges_is_copy_and_eq():
    s = mk((1, 3))
    r = s.ranges(); r.append((9, 9)); r[0] = (0, 0)
    assert s.ranges() == [(1, 3)]
    assert mk((1, 2), (2, 3)) == mk((1, 3))
    assert mk((1, 3)) != mk((1, 4))
    assert (mk((1, 3)) == [(1, 3)]) is False
'''},
 {'intervals.py': '''def _chk(*xs):
    for x in xs:
        if type(x) is not int:
            raise TypeError("ints only")


class IntervalSet:
    def __init__(self):
        self._r = []

    def add(self, start, end):
        _chk(start, end)
        if start > end:
            raise ValueError("start > end")
        if start == end:
            return
        out = []
        placed = False
        for a, b in self._r:
            if b < start:
                out.append((a, b))
            elif a > end:
                if not placed:
                    out.append((start, end)); placed = True
                out.append((a, b))
            else:
                start, end = min(a, start), max(b, end)
        if not placed:
            out.append((start, end))
        self._r = out

    def remove(self, start, end):
        _chk(start, end)
        if start > end:
            raise ValueError("start > end")
        if start == end:
            return
        out = []
        for a, b in self._r:
            if b <= start or a >= end:
                out.append((a, b))
                continue
            if a < start:
                out.append((a, start))
            if b > end:
                out.append((end, b))
        self._r = out

    def contains(self, x):
        _chk(x)
        return any(a <= x < b for a, b in self._r)

    def ranges(self):
        return list(self._r)

    def total(self):
        return sum(b - a for a, b in self._r)

    def gaps(self, lo, hi):
        _chk(lo, hi)
        if lo >= hi:
            return []
        out = []
        cur = lo
        for a, b in self._r:
            if b <= cur:
                continue
            if a >= hi:
                break
            if a > cur:
                out.append((cur, a))
            cur = max(cur, b)
        if cur < hi:
            out.append((cur, hi))
        return out

    def __len__(self):
        return len(self._r)

    def __eq__(self, other):
        return isinstance(other, IntervalSet) and self._r == other._r
'''}, ['tests/test_intervals.py'])

# 103 rate limiter
task(103, 'Sliding-window rate limiter',
 'Implement RateLimiter in ratelimit.py as documented. Time is always passed in by the caller; never read the system clock. Do not change the tests.',
 {'ratelimit.py': '''class RateLimiter:
    """Sliding-window-log limiter: at most `limit` allowed requests per key in any window of `window` seconds.

    __init__(limit, window): limit must be an int >= 1 and window a number > 0, else ValueError.
    allow(key, now): True and the request is recorded if fewer than `limit` allowed requests for `key` happened in the
    half-open window (now - window, now]. A request at time t stops counting once now >= t + window. Rejected requests
    are NOT recorded. `now` must not be earlier than the latest `now` already seen for that key; if it is, raise ValueError
    and change nothing. Keys are independent.
    retry_after(key, now): 0 if allow(key, now) would succeed, else the number of seconds until it would first succeed
    (a float or int, never negative). It does not record anything. The same `now` ordering rule applies.
    remaining(key, now): how many more requests would be allowed right now (0..limit). Does not record anything.
    reset(key=None): forget one key, or all keys when key is None."""

    def __init__(self, limit, window):
        raise NotImplementedError
''', 'tests/test_ratelimit.py': '''from ratelimit import RateLimiter

def test_basic():
    r = RateLimiter(2, 10)
    assert r.allow("a", 0) and r.allow("a", 1)
    assert not r.allow("a", 2)
'''},
 {'tests/test_hidden_ratelimit.py': '''import pytest
from ratelimit import RateLimiter

def test_window_edges():
    r = RateLimiter(2, 10)
    assert r.allow("a", 0) and r.allow("a", 5)
    assert not r.allow("a", 9.99)
    assert r.allow("a", 10)          # request at 0 stops counting at now >= 10
    assert not r.allow("a", 14)      # 5 and 10 count
    assert r.allow("a", 15)

def test_rejected_not_recorded():
    r = RateLimiter(1, 10)
    assert r.allow("a", 0)
    for t in (1, 2, 3, 9):
        assert not r.allow("a", t)
    assert r.allow("a", 10)

def test_keys_independent_and_reset():
    r = RateLimiter(1, 10)
    assert r.allow("a", 0) and r.allow("b", 0)
    assert not r.allow("a", 1)
    r.reset("a")
    assert r.allow("a", 1) and not r.allow("b", 1)
    r.reset()
    assert r.allow("b", 1)

def test_retry_after():
    r = RateLimiter(2, 10)
    assert r.retry_after("a", 0) == 0
    r.allow("a", 0); r.allow("a", 4)
    assert r.retry_after("a", 5) == 5
    assert r.retry_after("a", 9) == 1
    assert r.retry_after("a", 10) == 0
    assert r.allow("a", 5) is False and r.retry_after("a", 5) == 5

def test_remaining():
    r = RateLimiter(3, 10)
    assert r.remaining("a", 0) == 3
    r.allow("a", 0); r.allow("a", 1)
    assert r.remaining("a", 2) == 1
    assert r.remaining("a", 10) == 2
    assert r.remaining("a", 11) == 3

def test_time_going_backwards():
    r = RateLimiter(2, 10)
    r.allow("a", 5)
    with pytest.raises(ValueError):
        r.allow("a", 4)
    with pytest.raises(ValueError):
        r.retry_after("a", 4)
    with pytest.raises(ValueError):
        r.remaining("a", 4)
    assert r.allow("a", 5)
    assert not r.allow("a", 5)

def test_bad_args():
    for lim, win in [(0, 1), (-1, 1), (1.5, 1), (True, 1), (1, 0), (1, -2), ("1", 1), (1, "5")]:
        with pytest.raises(ValueError):
            RateLimiter(lim, win)
    RateLimiter(1, 0.5)
'''},
 {'ratelimit.py': '''class RateLimiter:
    def __init__(self, limit, window):
        if type(limit) is not int or limit < 1:
            raise ValueError("limit must be int >= 1")
        if isinstance(window, bool) or not isinstance(window, (int, float)) or window <= 0:
            raise ValueError("window must be > 0")
        self.limit = limit
        self.window = window
        self._log = {}
        self._last = {}

    def _check(self, key, now):
        if key in self._last and now < self._last[key]:
            raise ValueError("time went backwards")

    def _live(self, key, now):
        return [t for t in self._log.get(key, []) if now < t + self.window]

    def allow(self, key, now):
        self._check(key, now)
        live = self._live(key, now)
        self._last[key] = now
        if len(live) < self.limit:
            live.append(now)
            self._log[key] = live
            return True
        self._log[key] = live
        return False

    def retry_after(self, key, now):
        self._check(key, now)
        live = self._live(key, now)
        if len(live) < self.limit:
            return 0
        need = len(live) - self.limit + 1
        return max(0, live[need - 1] + self.window - now)

    def remaining(self, key, now):
        self._check(key, now)
        return max(0, self.limit - len(self._live(key, now)))

    def reset(self, key=None):
        if key is None:
            self._log.clear(); self._last.clear()
        else:
            self._log.pop(key, None); self._last.pop(key, None)
'''}, ['tests/test_ratelimit.py'])

# 104 topo sort
task(104, 'Deterministic topological sort',
 'Implement toposort in topo.py as documented. Do not change the tests.',
 {'topo.py': '''class CycleError(ValueError):
    """Raised when the graph has a cycle. The attribute `cycle` is a list of nodes forming one cycle, starting and
    ending at the same node (e.g. ["a", "b", "c", "a"]), following dependency edges (each node depends on the next)."""


def toposort(deps):
    """deps maps node -> iterable of nodes it depends on. Return a list in which every node appears after all of its
    dependencies. Nodes that only appear as dependencies are included. Duplicate dependencies are ignored.
    Among nodes that are ready at the same time, the smallest (by normal ordering of the nodes) comes first.
    A node depending on itself is a cycle of length 1 (cycle == [n, n]). deps itself must not be modified.
    If there is a cycle raise CycleError. The reported cycle must be the one found by starting from the smallest node that is
    part of any cycle and following, at each step, the smallest dependency that still leads back into a cycle."""
    raise NotImplementedError
''', 'tests/test_topo.py': '''from topo import toposort

def test_simple():
    assert toposort({"b": ["a"], "a": []}) == ["a", "b"]
'''},
 {'tests/test_hidden_topo.py': '''import pytest
from topo import toposort, CycleError

def test_order_and_ties():
    deps = {"d": ["b", "c"], "c": ["a"], "b": ["a"], "a": []}
    assert toposort(deps) == ["a", "b", "c", "d"]
    assert toposort({"z": [], "y": [], "x": []}) == ["x", "y", "z"]

def test_implicit_nodes_and_dupes():
    assert toposort({"b": ["a", "a", "c"]}) == ["a", "c", "b"]
    assert toposort({}) == []

def test_ready_smallest_first_not_dfs():
    deps = {"m": ["z"], "a": ["b"], "b": []}
    assert toposort(deps) == ["b", "a", "z", "m"]

def test_input_not_modified():
    deps = {"b": ["a"], "a": []}
    toposort(deps)
    assert deps == {"b": ["a"], "a": []}

def test_cycle_self():
    with pytest.raises(CycleError) as e:
        toposort({"a": ["a"]})
    assert e.value.cycle == ["a", "a"]
    assert isinstance(e.value, ValueError)

def test_cycle_path():
    with pytest.raises(CycleError) as e:
        toposort({"a": ["b"], "b": ["c"], "c": ["a"], "x": []})
    assert e.value.cycle == ["a", "b", "c", "a"]

def test_cycle_smallest_cyclic_start_and_branch():
    deps = {"a": ["b"], "b": [], "c": ["e", "d"], "d": ["c"], "e": ["f"], "f": []}
    with pytest.raises(CycleError) as e:
        toposort(deps)
    assert e.value.cycle == ["c", "d", "c"]

def test_cycle_downstream_node_not_in_cycle():
    deps = {"a": ["z"], "z": ["y"], "y": ["z"]}
    with pytest.raises(CycleError) as e:
        toposort(deps)
    assert e.value.cycle == ["y", "z", "y"]
'''},
 {'topo.py': '''class CycleError(ValueError):
    def __init__(self, cycle):
        super().__init__("cycle: " + " -> ".join(map(str, cycle)))
        self.cycle = cycle


def toposort(deps):
    graph = {}
    for n, ds in deps.items():
        graph.setdefault(n, set()).update(ds)
        for d in ds:
            graph.setdefault(d, set())
    indeg = {n: len(ds) for n, ds in graph.items()}
    rev = {n: [] for n in graph}
    for n, ds in graph.items():
        for d in ds:
            rev[d].append(n)
    import heapq
    ready = [n for n, k in indeg.items() if k == 0]
    heapq.heapify(ready)
    out = []
    while ready:
        n = heapq.heappop(ready)
        out.append(n)
        for m in rev[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(ready, m)
    if len(out) == len(graph):
        return out
    done = set(out)
    rest = {n: sorted(d for d in ds if d not in done) for n, ds in graph.items() if n not in done}
    # nodes that can reach themselves
    def reaches_self(s):
        seen, stack = set(), list(rest[s])
        while stack:
            x = stack.pop()
            if x == s:
                return True
            if x in seen or x not in rest:
                continue
            seen.add(x)
            stack.extend(rest[x])
        return False
    cyc = {n for n in rest if reaches_self(n)}
    start = min(cyc)
    path = [start]
    cur = start
    while True:
        nxt = min(d for d in rest[cur] if d in cyc and (d == start or _reach(rest, d, start)))
        path.append(nxt)
        if nxt == start:
            break
        cur = nxt
    raise CycleError(path)


def _reach(rest, a, b):
    seen, stack = set(), [a]
    while stack:
        x = stack.pop()
        if x == b:
            return True
        if x in seen or x not in rest:
            continue
        seen.add(x)
        stack.extend(rest[x])
    return False
'''}, ['tests/test_topo.py'])

# 105 CSV
task(105, 'CSV parser',
 'Implement parse_csv in csvparse.py as documented. Use only the standard library but do not use the csv module. Do not change the tests.',
 {'csvparse.py': '''def parse_csv(text, delimiter=","):
    """Parse CSV text into a list of rows (lists of str).

    Fields are separated by `delimiter` (a single character that is not a quote, CR or LF, else ValueError). Rows end at
    LF, CRLF or a lone CR. A field may be quoted with double quotes; inside a quoted field the delimiter and line breaks
    are literal and a doubled quote ("") is one quote character. A quote that appears in the middle of an unquoted field is
    literal. After the closing quote of a quoted field only the delimiter or the end of the row may follow, else ValueError.
    An unterminated quoted field raises ValueError. A final line break does not create an extra empty row, but a completely
    empty input returns []. A blank line in the middle yields [""] (one empty field). `text` must be a str, else TypeError.
    Line breaks inside quotes are kept exactly as they appear (no normalisation)."""
    raise NotImplementedError
''', 'tests/test_csvparse.py': '''from csvparse import parse_csv

def test_simple():
    assert parse_csv("a,b\\n1,2\\n") == [["a", "b"], ["1", "2"]]
'''},
 {'tests/test_hidden_csvparse.py': '''import pytest
from csvparse import parse_csv

def test_basic_and_endings():
    assert parse_csv("a,b\\r\\n1,2\\r\\n") == [["a", "b"], ["1", "2"]]
    assert parse_csv("a,b\\r1,2") == [["a", "b"], ["1", "2"]]
    assert parse_csv("a,b\\n1,2") == [["a", "b"], ["1", "2"]]
    assert parse_csv("") == []
    assert parse_csv("\\n") == [[""]]

def test_empty_fields():
    assert parse_csv("a,,c\\n,\\n") == [["a", "", "c"], ["", ""]]
    assert parse_csv("a,b,\\n") == [["a", "b", ""]]

def test_blank_line_middle():
    assert parse_csv("a\\n\\nb\\n") == [["a"], [""], ["b"]]

def test_quotes():
    assert parse_csv('"a,b",c\\n') == [["a,b", "c"]]
    assert parse_csv('"he said ""hi""",x') == [['he said "hi"', "x"]]
    assert parse_csv('"line1\\nline2",x\\n') == [["line1\\nline2", "x"]]
    assert parse_csv('"a\\r\\nb"') == [["a\\r\\nb"]]
    assert parse_csv('""') == [[""]]
    assert parse_csv('"",x') == [["", "x"]]
    assert parse_csv('""""') == [['"']]

def test_literal_quote_mid_field():
    assert parse_csv('ab"c,d\\n') == [['ab"c', "d"]]

def test_errors():
    for bad in ['"abc', '"abc"x,y', '"a""', '"a" ,b']:
        with pytest.raises(ValueError):
            parse_csv(bad)
    with pytest.raises(TypeError):
        parse_csv(b"a,b")
    for d in ["", ",,", '"', "\\n", "\\r"]:
        with pytest.raises(ValueError):
            parse_csv("a", delimiter=d)

def test_delimiter():
    assert parse_csv("a;b\\n", delimiter=";") == [["a", "b"]]
    assert parse_csv("a,b;c", delimiter=";") == [["a,b", "c"]]
    assert parse_csv("a\\tb\\n", delimiter="\\t") == [["a", "b"]]

def test_quoted_then_eof_and_newline():
    assert parse_csv('"a",b\\n"c",d') == [["a", "b"], ["c", "d"]]
    assert parse_csv('a,"b"\\n') == [["a", "b"]]
'''},
 {'csvparse.py': '''def parse_csv(text, delimiter=","):
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter in '"\\r\\n':
        raise ValueError("bad delimiter")
    rows, row, field = [], [], []
    i, n = 0, len(text)
    if n == 0:
        return []
    state = "start"
    while i < n:
        c = text[i]
        if state == "start":
            if c == '"':
                state = "quoted"
            elif c == delimiter:
                row.append("");
            elif c in "\\r\\n":
                row.append(""); rows.append(row); row = []
                if c == "\\r" and i + 1 < n and text[i + 1] == "\\n":
                    i += 1
            else:
                field.append(c); state = "plain"
        elif state == "plain":
            if c == delimiter:
                row.append("".join(field)); field = []; state = "start"
            elif c in "\\r\\n":
                row.append("".join(field)); field = []; rows.append(row); row = []; state = "start"
                if c == "\\r" and i + 1 < n and text[i + 1] == "\\n":
                    i += 1
            else:
                field.append(c)
        elif state == "quoted":
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"'); i += 1
                else:
                    state = "after"
            else:
                field.append(c)
        elif state == "after":
            if c == delimiter:
                row.append("".join(field)); field = []; state = "start"
            elif c in "\\r\\n":
                row.append("".join(field)); field = []; rows.append(row); row = []; state = "start"
                if c == "\\r" and i + 1 < n and text[i + 1] == "\\n":
                    i += 1
            else:
                raise ValueError("junk after closing quote")
        i += 1
    if state == "quoted":
        raise ValueError("unterminated quote")
    if state == "plain" or state == "after":
        row.append("".join(field)); rows.append(row)
    elif state == "start" and row:
        row.append("".join(field)); rows.append(row)
    return rows
'''}, ['tests/test_csvparse.py'])

# 106 glob
task(106, 'Path glob matcher',
 'Implement glob_match in globmatch.py as documented. Do not use fnmatch or glob. Do not change the tests.',
 {'globmatch.py': '''def glob_match(pattern, path):
    """Return True if `path` matches `pattern` completely. Paths use "/" as separator.

    "?"  matches exactly one character that is not "/".
    "*"  matches zero or more characters that are not "/".
    "**" as a whole path segment (between slashes or at either end) matches zero or more whole segments, so "a/**/b"
         matches "a/b", "a/x/b" and "a/x/y/b"; "**/x" matches "x" and "a/x"; "a/**" matches "a/" and "a/x/y" but NOT "a".
         "**" that is part of a larger segment (like "a**") behaves like a single "*".
    "[abc]" matches one of the listed characters; "[a-c]" a range; "[!abc]" or "[^abc]" any one character except those
         and except "/". A "]" right after "[" or "[!" is a literal member. A "[" with no closing "]" is a literal "[".
         A range whose start is after its end (like "[z-a]") raises ValueError.
    "\\\\" escapes the next character so it is taken literally (a trailing lone backslash raises ValueError).
    Matching is case-sensitive. A leading "." is not special. Both arguments must be str, else TypeError."""
    raise NotImplementedError
''', 'tests/test_globmatch.py': '''from globmatch import glob_match

def test_star():
    assert glob_match("*.py", "a.py")
    assert not glob_match("*.py", "d/a.py")
'''},
 {'tests/test_hidden_globmatch.py': '''import pytest
from globmatch import glob_match as g

def test_star_q():
    assert g("a*c", "abc") and g("a*c", "ac") and not g("a*c", "a/c")
    assert g("a?c", "abc") and not g("a?c", "a/c") and not g("a?c", "ac")
    assert g("*", "") and g("*", "abc") and not g("*", "a/b")
    assert g("", "") and not g("", "a")

def test_doublestar():
    assert g("a/**/b", "a/b") and g("a/**/b", "a/x/b") and g("a/**/b", "a/x/y/b")
    assert not g("a/**/b", "ab") and not g("a/**/b", "a/x/c")
    assert g("**/x", "x") and g("**/x", "a/x") and g("**/x", "a/b/x") and not g("**/x", "ax")
    assert g("a/**", "a/") and g("a/**", "a/x/y") and not g("a/**", "a")
    assert g("**", "") and g("**", "a/b/c")
    assert g("a**c", "abc") and not g("a**c", "a/c")
    assert g("**/*.py", "m.py") and g("**/*.py", "p/q/m.py") and not g("**/*.py", "m.txt")

def test_classes():
    assert g("[abc]x", "bx") and not g("[abc]x", "dx")
    assert g("[a-c]x", "cx") and not g("[a-c]x", "dx")
    assert g("[!a-c]x", "dx") and not g("[!a-c]x", "bx") and g("[^a]x", "bx")
    assert not g("[!a]x", "/x")
    assert g("[]]", "]") and g("[!]]", "a") and not g("[!]]", "]")
    assert g("[", "[") and g("a[b", "a[b") and not g("a[b", "ab")
    assert g("[a-]", "-") and g("[a-]", "a")

def test_bad_range():
    with pytest.raises(ValueError):
        g("[z-a]", "m")

def test_escape():
    assert g("\\\\*", "*") and not g("\\\\*", "a")
    assert g("a\\\\?b", "a?b") and not g("a\\\\?b", "axb")
    assert g("\\\\[a]", "[a]")
    with pytest.raises(ValueError):
        g("abc\\\\", "abc")

def test_case_and_types():
    assert not g("A", "a")
    assert g("*", ".hidden") and g(".*", ".x")
    with pytest.raises(TypeError):
        g(1, "a")
    with pytest.raises(TypeError):
        g("a", None)

def test_backtracking():
    assert g("*a*a*a*b", "aaaaaaaaab") and not g("*a*a*a*b", "aaaaaaaaac")
    assert g("a*b*c", "aXbXbXc")
'''},
 {'globmatch.py': '''import re


def _seg_to_re(seg):
    out, i, n = [], 0, len(seg)
    while i < n:
        c = seg[i]
        if c == "\\\\":
            if i + 1 >= n:
                raise ValueError("trailing backslash")
            out.append(re.escape(seg[i + 1])); i += 2
        elif c == "*":
            while i < n and seg[i] == "*":
                i += 1
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]"); i += 1
        elif c == "[":
            j = i + 1
            neg = False
            if j < n and seg[j] in "!^":
                neg = True; j += 1
            members = []
            first = True
            k = j
            closed = False
            while k < n:
                ch = seg[k]
                if ch == "]" and not first:
                    closed = True
                    break
                first = False
                if ch == "\\\\" and k + 1 < n:
                    ch = seg[k + 1]; k += 1
                if k + 2 < n and seg[k + 1] == "-" and seg[k + 2] != "]":
                    hi = seg[k + 2]
                    if hi == "\\\\" and k + 3 < n:
                        hi = seg[k + 3]; k += 1
                    if ch > hi:
                        raise ValueError("bad range")
                    members.append((ch, hi)); k += 3
                else:
                    members.append((ch, ch)); k += 1
            if not closed:
                out.append(re.escape("[")); i += 1
                continue
            cls = "".join(re.escape(a) + "-" + re.escape(b) if a != b else re.escape(a) for a, b in members)
            out.append(("[^/" if neg else "[") + cls + "]")
            i = k + 1
        else:
            out.append(re.escape(c)); i += 1
    return "".join(out)


def glob_match(pattern, path):
    if not isinstance(pattern, str) or not isinstance(path, str):
        raise TypeError("str only")
    pats = pattern.split("/")
    segs = path.split("/")
    rx = {}
    def seg_ok(i, j):
        if i not in rx:
            rx[i] = re.compile(_seg_to_re(pats[i]), re.S)
        return rx[i].fullmatch(segs[j]) is not None
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def go(i, j):
        if i == len(pats):
            return j == len(segs)
        if pats[i] == "**":
            last = i == len(pats) - 1
            lo = 1 if (last and len(pats) > 1) else 0
            for k in range(lo, len(segs) - j + 1):
                if go(i + 1, j + k):
                    return True
            return False
        if j >= len(segs):
            return False
        return seg_ok(i, j) and go(i + 1, j + 1)
    for p in pats:
        if p != "**":
            _seg_to_re(p)
    return go(0, 0)
'''}, ['tests/test_globmatch.py'])

# 107 allocate
task(107, 'Largest-remainder allocation',
 'Implement allocate and split_even in allocate.py as documented. Use integer arithmetic only. Do not change the tests.',
 {'allocate.py': '''def allocate(total, ratios):
    """Split the integer `total` (cents) into len(ratios) integer parts that sum exactly to total, proportional to ratios.

    Use the largest-remainder method: each part first gets floor(total * ratio / sum(ratios)) (floor toward -infinity for
    positive total); the leftover units are given one each to the parts with the largest fractional remainders, ties going
    to the lower index. Negative `total` is allocated as the negation of allocate(-total, ratios). Ratios must be a
    non-empty list/tuple of ints >= 0 (bool not accepted) with a positive sum, else ValueError; total must be an int (bool not
    accepted), else TypeError. A zero ratio always gets 0. Never use floats."""
    raise NotImplementedError


def split_even(total, n):
    """Split `total` into n parts as evenly as possible; extra units go to the first parts. Same type rules as allocate;
    n must be an int >= 1 else ValueError."""
    raise NotImplementedError
''', 'tests/test_allocate.py': '''from allocate import allocate

def test_basic():
    assert allocate(100, [1, 1]) == [50, 50]
'''},
 {'tests/test_hidden_allocate.py': '''import pytest
from allocate import allocate, split_even

def test_sum_and_basic():
    assert allocate(100, [1, 1, 1]) == [34, 33, 33]
    assert allocate(10, [1, 2, 3]) == [2, 3, 5]
    assert allocate(5, [1, 1]) == [3, 2]
    assert allocate(0, [3, 4]) == [0, 0]

def test_remainder_ranking_not_index_order():
    assert allocate(10, [3, 3, 4]) == [3, 3, 4]
    assert allocate(7, [1, 5, 5]) == [1, 3, 3]
    assert allocate(100, [33, 33, 34]) == [33, 33, 34]
    assert allocate(2, [1, 2, 2]) == [0, 1, 1]
    assert allocate(3, [2, 3, 3]) == [1, 1, 1]

def test_zero_ratio():
    assert allocate(10, [0, 1, 0]) == [0, 10, 0]
    assert allocate(5, [0, 1, 1]) == [0, 3, 2]

def test_negative():
    assert allocate(-100, [1, 1, 1]) == [-34, -33, -33]
    assert allocate(-5, [1, 1]) == [-3, -2]
    assert sum(allocate(-1001, [7, 11, 13])) == -1001

def test_big_exact():
    r = allocate(10**30 + 1, [1, 1, 1])
    assert sum(r) == 10**30 + 1 and max(r) - min(r) <= 1

def test_errors():
    for bad in ([], (), [0, 0], [1, -1], [1.5, 1], [True, 1], "12", None, [1, "2"]):
        with pytest.raises(ValueError):
            allocate(10, bad)
    for t in (1.5, "10", True, None):
        with pytest.raises(TypeError):
            allocate(t, [1, 1])

def test_tuple_ok():
    assert allocate(4, (1, 1)) == [2, 2]

def test_split_even():
    assert split_even(10, 3) == [4, 3, 3]
    assert split_even(-10, 3) == [-4, -3, -3]
    assert split_even(2, 5) == [1, 1, 0, 0, 0]
    with pytest.raises(ValueError):
        split_even(5, 0)
    with pytest.raises(ValueError):
        split_even(5, True)
    with pytest.raises(TypeError):
        split_even(5.0, 2)
'''},
 {'allocate.py': '''def allocate(total, ratios):
    if type(total) is not int:
        raise TypeError("total must be int")
    if not isinstance(ratios, (list, tuple)) or len(ratios) == 0:
        raise ValueError("ratios must be a non-empty list or tuple")
    for r in ratios:
        if type(r) is not int or r < 0:
            raise ValueError("ratios must be ints >= 0")
    s = sum(ratios)
    if s <= 0:
        raise ValueError("ratios must have a positive sum")
    if total < 0:
        return [-x for x in allocate(-total, ratios)]
    parts = [total * r // s for r in ratios]
    rem = [(total * r) % s for r in ratios]
    left = total - sum(parts)
    order = sorted(range(len(ratios)), key=lambda i: (-rem[i], i))
    for i in order[:left]:
        parts[i] += 1
    return parts


def split_even(total, n):
    if type(total) is not int:
        raise TypeError("total must be int")
    if type(n) is not int or n < 1:
        raise ValueError("n must be int >= 1")
    if total < 0:
        return [-x for x in split_even(-total, n)]
    q, r = divmod(total, n)
    return [q + 1 if i < r else q for i in range(n)]
'''}, ['tests/test_allocate.py'])

# 108 wrap
task(108, 'Text wrapping',
 'Implement wrap in wrapper.py as documented. Do not use the textwrap module. Do not change the tests.',
 {'wrapper.py': '''def wrap(text, width, indent="", subsequent_indent=None):
    """Greedy word-wrap `text` and return a list of lines (no trailing newlines).

    Paragraphs are separated by one or more blank lines (lines that are empty or only whitespace); within a paragraph all
    runs of whitespace (spaces, tabs, newlines) collapse to a single space and leading/trailing whitespace is dropped.
    The output has one empty string "" between consecutive paragraphs (exactly one, however many blank lines were in the
    input) and no leading or trailing empty strings. Empty or all-whitespace text returns [].
    Every line has length <= width counting its indent. The first line of each paragraph starts with `indent`, the others
    with `subsequent_indent` (which defaults to `indent`). A word that does not fit on an empty line (after the indent) is
    split into chunks that fill the line exactly. A word is never split if it fits on a fresh line. No line ever has
    trailing spaces. Raise ValueError if width < 1 or if either indent is as long as width or longer (no room for text).
    width must be an int (not bool), else TypeError."""
    raise NotImplementedError
''', 'tests/test_wrapper.py': '''from wrapper import wrap

def test_basic():
    assert wrap("aa bb cc", 5) == ["aa bb", "cc"]
'''},
 {'tests/test_hidden_wrapper.py': '''import pytest
from wrapper import wrap

def test_greedy():
    assert wrap("aa bb cc", 5) == ["aa bb", "cc"]
    assert wrap("aa bb cc", 4) == ["aa", "bb", "cc"]
    assert wrap("aa bb", 5) == ["aa bb"]
    assert wrap("a b c d e f", 3) == ["a b", "c d", "e f"]

def test_whitespace_collapse():
    assert wrap("  aa \\t bb\\n\\ncc  ", 10) == ["aa bb", "", "cc"]
    assert wrap("", 5) == [] and wrap("   \\n \\t ", 5) == []

def test_paragraphs():
    assert wrap("a\\n\\n\\n\\nb", 5) == ["a", "", "b"]
    assert wrap("a\\n  \\nb", 5) == ["a", "", "b"]
    assert wrap("\\n\\na b\\n\\n", 5) == ["a b"]
    assert wrap("a\\nb", 5) == ["a b"]

def test_long_word():
    assert wrap("abcdefghij", 4) == ["abcd", "efgh", "ij"]
    assert wrap("x abcdefghij y", 4) == ["x", "abcd", "efgh", "ij y"]
    assert wrap("abcd", 4) == ["abcd"]
    assert wrap("ab abcde", 5) == ["ab", "abcde"]

def test_indent():
    assert wrap("aa bb cc dd", 7, indent="* ", subsequent_indent="  ") == ["* aa bb", "  cc dd"]
    assert wrap("aa bb cc", 6, indent="--") == ["--aa", "--bb", "--cc"]
    assert wrap("aa\\n\\nbb cc", 6, indent="> ", subsequent_indent="  ") == ["> aa", "", "> bb", "  cc"]
    assert wrap("abcdefgh", 5, indent="> ", subsequent_indent="  ") == ["> abc", "  def", "  gh"]

def test_no_trailing_spaces_and_widths():
    out = wrap("the quick brown fox jumps over the lazy dog " * 5, 17, indent="  ")
    assert all(len(l) <= 17 and l == l.rstrip() for l in out)
    assert " ".join(w for l in out for w in l.split()) == ("the quick brown fox jumps over the lazy dog " * 5).strip()

def test_errors():
    for w in (0, -3):
        with pytest.raises(ValueError):
            wrap("a", w)
    with pytest.raises(ValueError):
        wrap("a", 3, indent="   ")
    with pytest.raises(ValueError):
        wrap("a", 3, indent="", subsequent_indent="abc")
    with pytest.raises(TypeError):
        wrap("a", 3.0)
    with pytest.raises(TypeError):
        wrap("a", True)
'''},
 {'wrapper.py': '''def wrap(text, width, indent="", subsequent_indent=None):
    if type(width) is not int:
        raise TypeError("width must be int")
    if subsequent_indent is None:
        subsequent_indent = indent
    if width < 1 or len(indent) >= width or len(subsequent_indent) >= width:
        raise ValueError("bad width/indent")
    paras, cur = [], []
    for line in text.replace("\\r\\n", "\\n").split("\\n"):
        if line.strip() == "":
            if cur:
                paras.append(" ".join(" ".join(cur).split())); cur = []
        else:
            cur.append(line)
    if cur:
        paras.append(" ".join(" ".join(cur).split()))
    out = []
    for pi, para in enumerate(paras):
        if pi:
            out.append("")
        prefix = indent
        line = ""
        for w in para.split(" "):
            while True:
                room = width - len(prefix)
                if line == "":
                    if len(w) <= room:
                        line = w
                        break
                    out.append(prefix + w[:room])
                    w = w[room:]
                    prefix = subsequent_indent
                    continue
                if len(line) + 1 + len(w) <= room:
                    line += " " + w
                    break
                out.append(prefix + line)
                prefix = subsequent_indent
                line = ""
        if line:
            out.append(prefix + line)
    return out
'''}, ['tests/test_wrapper.py'])

# 109 expression evaluator
task(109, 'Arithmetic expression evaluator',
 'Implement evaluate in calc.py as documented. Do not use eval, exec, ast or compile. Do not change the tests.',
 {'calc.py': '''def evaluate(expr, variables=None):
    """Evaluate an arithmetic expression string and return an int or a float.

    Grammar: numbers (digits with an optional ".digits" part; "1." and ".5" are invalid), names (letters/underscore then
    letters/digits/underscore, looked up in the `variables` dict), binary + - * / % ^ ( ), unary + and -, whitespace anywhere
    between tokens. Precedence, loosest to tightest: + - ; * / % ; unary + - ; ^ . "^" is power and is RIGHT associative,
    and binds tighter than unary minus on its left but a unary minus is allowed on its right: "-2^2" is -4, "2^-2" is 0.25,
    "2^3^2" is 512. "/" is true division and returns an int when the result is exactly integral and both operands are ints
    ("6/3" is the int 2, "7/2" is 3.5); "%" is Python's modulo. Integer results stay ints; any float operand gives a float.
    Errors: a malformed expression (empty, dangling operator, unbalanced parentheses, unknown character, two numbers in a
    row) raises SyntaxError; an unknown variable raises NameError; division or modulo by zero raises ZeroDivisionError.
    Exponentiation that would produce a complex number (negative base to a fractional power) raises ValueError.
    `expr` must be a str, else TypeError. variables may be None."""
    raise NotImplementedError
''', 'tests/test_calc.py': '''from calc import evaluate

def test_basic():
    assert evaluate("1+2*3") == 7
'''},
 {'tests/test_hidden_calc.py': '''import pytest
from calc import evaluate as ev

def test_precedence():
    assert ev("1+2*3") == 7 and ev("(1+2)*3") == 9 and ev("10-4-3") == 3 and ev("2*3%4") == 2
    assert ev("100/10/5") == 2 and ev("7%4*2") == 6

def test_power():
    assert ev("2^3^2") == 512
    assert ev("-2^2") == -4
    assert ev("2^-2") == 0.25
    assert ev("(-2)^2") == 4
    assert ev("2^0") == 1
    assert ev("-2^-2") == -0.25
    assert ev("2*3^2") == 18
    assert ev("4^0.5") == 2.0

def test_unary():
    assert ev("--3") == 3 and ev("+-3") == -3 and ev("3--3") == 6 and ev("-(1+2)") == -3
    assert ev("2*-3") == -6

def test_division_types():
    r = ev("6/3")
    assert r == 2 and type(r) is int
    assert ev("7/2") == 3.5
    r = ev("6.0/3")
    assert r == 2.0 and type(r) is float
    assert type(ev("2^3")) is int
    assert ev("7%3") == 1 and ev("-7%3") == 2

def test_numbers_whitespace():
    assert ev("  1 +   2 ") == 3 and ev("1.5+1.5") == 3.0 and ev("0.25*4") == 1.0
    assert type(ev("1.5+1.5")) is float

def test_variables():
    assert ev("x*y+z_1", {"x": 2, "y": 3, "z_1": 4}) == 10
    assert ev("-x^2", {"x": 3}) == -9
    with pytest.raises(NameError):
        ev("x+1")
    with pytest.raises(NameError):
        ev("x", {})

@pytest.mark.parametrize("bad", ["", "   ", "1+", "+", "*2", "(1", "1)", "()", "1 2", "1..2", "1.", ".5", "2 $ 3", "1+*2", "(1+2", "1+2)", "x y"])
def test_syntax(bad):
    with pytest.raises(SyntaxError):
        ev(bad, {"x": 1, "y": 2})

def test_math_errors():
    for e in ("1/0", "1%0", "1/(2-2)", "5%(3-3)"):
        with pytest.raises(ZeroDivisionError):
            ev(e)
    with pytest.raises(ValueError):
        ev("(-8)^0.5")
    with pytest.raises(ValueError):
        ev("(-2)^0.5")

def test_type():
    with pytest.raises(TypeError):
        ev(5)
    with pytest.raises(TypeError):
        ev(None)
'''},
 {'calc.py': '''import re

_TOK = re.compile(r"\\s*(?:(\\d+\\.\\d+|\\d+)|([A-Za-z_][A-Za-z0-9_]*)|(.))")


def _tokens(expr):
    out, pos = [], 0
    s = expr
    while pos < len(s):
        m = _TOK.match(s, pos)
        if not m:
            break
        if m.group(1) is None and m.group(2) is None and m.group(3) is None:
            break
        pos = m.end()
        if m.group(1) is not None:
            t = m.group(1)
            out.append(("num", float(t) if "." in t else int(t)))
        elif m.group(2) is not None:
            out.append(("name", m.group(2)))
        else:
            ch = m.group(3)
            if ch.isspace():
                continue
            if ch not in "+-*/%^()":
                raise SyntaxError("unknown character %r" % ch)
            out.append(("op", ch))
    # reject "1." and ".5" and "1..2": a number token directly followed/preceded by "." op
    for i, (k, v) in enumerate(out):
        if k == "op" and v == ".":
            raise SyntaxError("bad number")
    return out


def evaluate(expr, variables=None):
    if not isinstance(expr, str):
        raise TypeError("expr must be str")
    if "." in expr:
        if re.search(r"(?<!\\d)\\.|\\.(?!\\d)|\\d\\.\\d+\\.", expr):
            raise SyntaxError("bad number")
    toks = _tokens(expr)
    variables = variables or {}
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else (None, None)

    def eat():
        nonlocal pos
        t = toks[pos]; pos += 1
        return t

    def expr_():
        v = term()
        while peek() in (("op", "+"), ("op", "-")):
            op = eat()[1]
            r = term()
            v = v + r if op == "+" else v - r
        return v

    def term():
        v = unary()
        while peek() in (("op", "*"), ("op", "/"), ("op", "%")):
            op = eat()[1]
            r = unary()
            if op == "*":
                v = v * r
            elif op == "/":
                if r == 0:
                    raise ZeroDivisionError("division by zero")
                if type(v) is int and type(r) is int and v % r == 0:
                    v = v // r
                else:
                    v = v / r
            else:
                if r == 0:
                    raise ZeroDivisionError("modulo by zero")
                v = v % r
        return v

    def unary():
        if peek() == ("op", "-"):
            eat(); return -unary()
        if peek() == ("op", "+"):
            eat(); return unary()
        return power()

    def power():
        base = atom()
        if peek() == ("op", "^"):
            eat()
            exp = unary()          # right assoc, allows unary minus on the right
            if base < 0 and isinstance(exp, float) and exp != int(exp):
                raise ValueError("complex result")
            try:
                res = base ** exp
            except ZeroDivisionError:
                raise
            if isinstance(res, complex):
                raise ValueError("complex result")
            return res
        return base

    def atom():
        k, v = peek()
        if k == "num":
            eat(); return v
        if k == "name":
            eat()
            if v not in variables:
                raise NameError(v)
            return variables[v]
        if (k, v) == ("op", "("):
            eat()
            r = expr_()
            if peek() != ("op", ")"):
                raise SyntaxError("expected )")
            eat()
            return r
        raise SyntaxError("unexpected token")

    if not toks:
        raise SyntaxError("empty")
    r = expr_()
    if pos != len(toks):
        raise SyntaxError("trailing tokens")
    return r
'''}, ['tests/test_calc.py'])

# 110 ttl lru
task(110, 'LRU cache with TTL',
 'Implement TTLCache in ttlcache.py as documented. Time is always passed in by the caller; never read the system clock. Do not change the tests.',
 {'ttlcache.py': '''class TTLCache:
    """A cache with a maximum size and per-entry time-to-live, driven by caller-supplied time.

    __init__(maxsize, ttl): maxsize an int >= 1, ttl a number > 0 (default lifetime in seconds), else ValueError.
    put(key, value, now, ttl=None): store the value; it expires when now >= now_of_put + ttl (use the cache default when
    ttl is None; an explicit ttl must be > 0 else ValueError). Putting an existing key replaces value and expiry and makes
    it most recently used. Before inserting a NEW key into a full cache, first drop every expired entry; if it is still
    full, evict the least recently used live entry.
    get(key, now, default=None): the value if present and live, else default. A hit makes the key most recently used but
    does NOT change its expiry. An expired entry found by get is removed.
    __contains__ is not supported; use peek(key, now) which returns True/False for presence of a live entry without changing recency.
    size(now): number of live entries at time `now` (does not remove anything).
    purge(now): remove all expired entries and return how many were removed.
    keys(now): live keys from least to most recently used.
    `now` may not go backwards across calls: a call with a `now` smaller than the largest seen so far raises ValueError
    and changes nothing."""

    def __init__(self, maxsize, ttl):
        raise NotImplementedError
''', 'tests/test_ttlcache.py': '''from ttlcache import TTLCache

def test_basic():
    c = TTLCache(2, 10)
    c.put("a", 1, 0)
    assert c.get("a", 5) == 1
    assert c.get("a", 10) is None
'''},
 {'tests/test_hidden_ttlcache.py': '''import pytest
from ttlcache import TTLCache

def test_expiry_boundary():
    c = TTLCache(3, 10)
    c.put("a", 1, 0)
    assert c.get("a", 9.99) == 1
    assert c.get("a", 10) is None
    assert c.peek("a", 10) is False

def test_get_does_not_extend_ttl():
    c = TTLCache(3, 10)
    c.put("a", 1, 0)
    assert c.get("a", 8) == 1
    assert c.get("a", 10) is None

def test_put_resets_expiry_and_recency():
    c = TTLCache(2, 10)
    c.put("a", 1, 0); c.put("b", 2, 1)
    c.put("a", 3, 5)
    assert c.keys(5) == ["b", "a"]
    assert c.get("b", 11) is None
    assert c.get("a", 14) == 3

def test_eviction_lru_live():
    c = TTLCache(2, 100)
    c.put("a", 1, 0); c.put("b", 2, 1)
    c.get("a", 2)
    c.put("c", 3, 3)
    assert c.keys(3) == ["a", "c"] and c.get("b", 3, "x") == "x"

def test_expired_dropped_before_evicting_live():
    c = TTLCache(2, 10)
    c.put("a", 1, 0, ttl=2)
    c.put("b", 2, 1)
    c.put("c", 3, 5)          # a expired at 2: drop it instead of evicting live b
    assert c.keys(5) == ["b", "c"]

def test_default_and_custom_ttl():
    c = TTLCache(3, 10)
    c.put("a", 1, 0, ttl=3)
    c.put("b", 2, 0)
    assert c.peek("a", 3) is False and c.peek("b", 3) is True
    assert c.get("zz", 3, default=7) == 7

def test_peek_no_recency_change():
    c = TTLCache(3, 10)
    c.put("a", 1, 0); c.put("b", 2, 0)
    assert c.peek("a", 1) is True
    assert c.keys(1) == ["a", "b"]

def test_size_purge():
    c = TTLCache(5, 10)
    c.put("a", 1, 0, ttl=1); c.put("b", 2, 0, ttl=2); c.put("c", 3, 0)
    assert c.size(1) == 2
    assert c.purge(1) == 1
    assert c.purge(1) == 0
    assert c.size(2) == 1
    assert c.purge(5) == 1
    assert c.keys(5) == ["c"]

def test_get_removes_expired():
    c = TTLCache(2, 5)
    c.put("a", 1, 0)
    assert c.get("a", 6) is None
    assert c.purge(6) == 0

def test_time_backwards():
    c = TTLCache(2, 5)
    c.put("a", 1, 10)
    for call in (lambda: c.get("a", 9), lambda: c.put("b", 1, 9), lambda: c.size(9), lambda: c.purge(9),
                 lambda: c.keys(9), lambda: c.peek("a", 9)):
        with pytest.raises(ValueError):
            call()
    assert c.keys(10) == ["a"]

def test_bad_args():
    for ms, t in [(0, 1), (-1, 1), (1.5, 1), (True, 1), (1, 0), (1, -1), (1, "3")]:
        with pytest.raises(ValueError):
            TTLCache(ms, t)
    c = TTLCache(1, 1)
    for t in (0, -1):
        with pytest.raises(ValueError):
            c.put("a", 1, 0, ttl=t)
    assert c.size(0) == 0
'''},
 {'ttlcache.py': '''from collections import OrderedDict


class TTLCache:
    def __init__(self, maxsize, ttl):
        if type(maxsize) is not int or maxsize < 1:
            raise ValueError("maxsize")
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or ttl <= 0:
            raise ValueError("ttl")
        self.maxsize = maxsize
        self.ttl = ttl
        self._d = OrderedDict()   # key -> (value, expires)
        self._max_now = None

    def _tick(self, now):
        if self._max_now is not None and now < self._max_now:
            raise ValueError("time went backwards")
        self._max_now = now

    def _check(self, now):
        if self._max_now is not None and now < self._max_now:
            raise ValueError("time went backwards")

    def put(self, key, value, now, ttl=None):
        self._check(now)
        if ttl is None:
            ttl = self.ttl
        elif isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or ttl <= 0:
            raise ValueError("ttl")
        self._tick(now)
        if key in self._d:
            del self._d[key]
        else:
            if len(self._d) >= self.maxsize:
                for k in [k for k, (_, e) in self._d.items() if now >= e]:
                    del self._d[k]
                if len(self._d) >= self.maxsize:
                    self._d.popitem(last=False)
        self._d[key] = (value, now + ttl)

    def get(self, key, now, default=None):
        self._check(now)
        self._tick(now)
        if key not in self._d:
            return default
        v, e = self._d[key]
        if now >= e:
            del self._d[key]
            return default
        self._d.move_to_end(key)
        return v

    def peek(self, key, now):
        self._check(now)
        self._tick(now)
        return key in self._d and now < self._d[key][1]

    def size(self, now):
        self._check(now)
        self._tick(now)
        return sum(1 for _, (_, e) in self._d.items() if now < e)

    def purge(self, now):
        self._check(now)
        self._tick(now)
        dead = [k for k, (_, e) in self._d.items() if now >= e]
        for k in dead:
            del self._d[k]
        return len(dead)

    def keys(self, now):
        self._check(now)
        self._tick(now)
        return [k for k, (_, e) in self._d.items() if now < e]
'''}, ['tests/test_ttlcache.py'])

# 111 JSON pointer
task(111, 'JSON Pointer (RFC 6901)',
 'Implement pointer.py as documented. Do not change the tests.',
 {'pointer.py': '''def parse(ptr):
    """Split a JSON Pointer into a list of reference tokens. "" is the whole document -> []. Otherwise the pointer must start
    with "/" else ValueError. Tokens are separated by "/"; in each token "~1" becomes "/" and then "~0" becomes "~" (in
    that order). A "~" not followed by 0 or 1 raises ValueError. Non-str input raises TypeError."""
    raise NotImplementedError


def get(doc, ptr):
    """Return the value at the pointer. dict keys are matched exactly (a missing key raises KeyError). For lists the token
    must be "0" or digits without leading zeros (otherwise ValueError, including "-" and signs) and in range (IndexError
    when out of range). Walking into a scalar (str, int, float, bool, None) raises KeyError. The result is the real
    object, not a copy."""
    raise NotImplementedError


def set(doc, ptr, value):
    """Return a NEW document (deep copy of the path; do not modify `doc`) with `value` placed at the pointer.
    Setting "" returns value. For a dict parent the key is created or replaced. For a list parent the token is an index
    0..len (inserting before that index; len or "-" appends) -- a replace is NOT performed, the list grows; an index > len
    raises IndexError and a malformed index raises ValueError. All parents on the path must already exist (KeyError /
    IndexError as in get)."""
    raise NotImplementedError


def remove(doc, ptr):
    """Return a NEW document without the target. Removing "" raises ValueError. A dict key must exist (KeyError); a list
    index must be a valid existing index (ValueError if malformed, IndexError if out of range; "-" is malformed here).
    `doc` is not modified."""
    raise NotImplementedError


def escape(token):
    """Escape a key for use in a pointer: "~" -> "~0" and "/" -> "~1" (in that order). Non-str raises TypeError."""
    raise NotImplementedError
''', 'tests/test_pointer.py': '''from pointer import get

def test_basic():
    assert get({"a": [1, 2]}, "/a/1") == 2
'''},
 {'tests/test_hidden_pointer.py': '''import pytest
from pointer import parse, get, set, remove, escape

def test_parse():
    assert parse("") == [] and parse("/") == [""] and parse("/a/b") == ["a", "b"]
    assert parse("/a~1b/c~0d") == ["a/b", "c~d"]
    assert parse("/~01") == ["~1"]
    assert parse("//") == ["", ""]
    for bad in ("a", "a/b", "/a~", "/a~2", "/~"):
        with pytest.raises(ValueError):
            parse(bad)
    with pytest.raises(TypeError):
        parse(None)

def test_escape_roundtrip():
    assert escape("a/b~c") == "a~1b~0c"
    assert parse("/" + escape("~1/")) == ["~1/"]
    with pytest.raises(TypeError):
        escape(1)

DOC = {"foo": ["bar", "baz"], "": 0, "a/b": 1, "m~n": 8, "k": {"x": None}, "n": None}

def test_get_rfc_examples():
    assert get(DOC, "") is DOC
    assert get(DOC, "/foo") == ["bar", "baz"]
    assert get(DOC, "/foo/0") == "bar"
    assert get(DOC, "/") == 0
    assert get(DOC, "/a~1b") == 1
    assert get(DOC, "/m~0n") == 8
    assert get(DOC, "/k/x") is None

def test_get_errors():
    with pytest.raises(KeyError):
        get(DOC, "/nope")
    with pytest.raises(KeyError):
        get(DOC, "/n/x")
    with pytest.raises(KeyError):
        get(DOC, "/foo/0/x")
    for tok in ("01", "-1", "+1", "-", "x", " 1", "1 ", ""):
        with pytest.raises(ValueError):
            get(DOC, "/foo/" + tok)
    with pytest.raises(IndexError):
        get(DOC, "/foo/2")

def test_set_dict_and_root():
    d = {"a": {"b": 1}}
    r = set(d, "/a/c", 2)
    assert r == {"a": {"b": 1, "c": 2}} and d == {"a": {"b": 1}}
    assert set(d, "/a/b", 9) == {"a": {"b": 9}}
    assert set(d, "", 5) == 5

def test_set_list_inserts():
    d = {"l": [1, 2, 3]}
    assert set(d, "/l/1", 9) == {"l": [1, 9, 2, 3]}
    assert set(d, "/l/3", 9) == {"l": [1, 2, 3, 9]}
    assert set(d, "/l/-", 9) == {"l": [1, 2, 3, 9]}
    assert d == {"l": [1, 2, 3]}
    with pytest.raises(IndexError):
        set(d, "/l/4", 9)
    with pytest.raises(ValueError):
        set(d, "/l/01", 9)
    with pytest.raises(ValueError):
        set(d, "/l/x", 9)

def test_set_missing_parent_and_no_aliasing():
    with pytest.raises(KeyError):
        set({}, "/a/b", 1)
    d = {"a": {"b": [1]}, "other": {"z": 1}}
    r = set(d, "/a/b/0", 0)
    r["other"]["z"] = 99
    assert d["other"]["z"] == 99 or d["other"]["z"] == 1
    r["a"]["b"].append(5)
    assert d["a"]["b"] == [1]

def test_remove():
    d = {"a": [1, 2, 3], "b": {"c": 1}}
    assert remove(d, "/a/1") == {"a": [1, 3], "b": {"c": 1}}
    assert remove(d, "/b/c") == {"a": [1, 2, 3], "b": {}}
    assert d == {"a": [1, 2, 3], "b": {"c": 1}}
    with pytest.raises(ValueError):
        remove(d, "")
    with pytest.raises(KeyError):
        remove(d, "/zz")
    with pytest.raises(IndexError):
        remove(d, "/a/3")
    with pytest.raises(ValueError):
        remove(d, "/a/-")
    with pytest.raises(ValueError):
        remove(d, "/a/00")
'''},
 {'pointer.py': '''import copy


def parse(ptr):
    if not isinstance(ptr, str):
        raise TypeError("pointer must be str")
    if ptr == "":
        return []
    if not ptr.startswith("/"):
        raise ValueError("pointer must start with /")
    out = []
    for tok in ptr[1:].split("/"):
        i = 0
        res = []
        while i < len(tok):
            c = tok[i]
            if c == "~":
                if i + 1 >= len(tok) or tok[i + 1] not in "01":
                    raise ValueError("bad escape")
                res.append("/" if tok[i + 1] == "1" else "~")
                i += 2
            else:
                res.append(c); i += 1
        out.append("".join(res))
    return out


def escape(token):
    if not isinstance(token, str):
        raise TypeError("token must be str")
    return token.replace("~", "~0").replace("/", "~1")


def _index(tok):
    if not (tok.isascii() and tok.isdigit() and (tok == "0" or not tok.startswith("0"))):
        raise ValueError("bad index %r" % tok)
    return int(tok)


def get(doc, ptr):
    cur = doc
    for tok in parse(ptr):
        if isinstance(cur, dict):
            if tok not in cur:
                raise KeyError(tok)
            cur = cur[tok]
        elif isinstance(cur, list):
            i = _index(tok)
            if i >= len(cur):
                raise IndexError(tok)
            cur = cur[i]
        else:
            raise KeyError(tok)
    return cur


def _parent(doc, toks):
    cur = doc
    for tok in toks:
        cur = _step(cur, tok)
    return cur


def _step(cur, tok):
    if isinstance(cur, dict):
        if tok not in cur:
            raise KeyError(tok)
        return cur[tok]
    if isinstance(cur, list):
        i = _index(tok)
        if i >= len(cur):
            raise IndexError(tok)
        return cur[i]
    raise KeyError(tok)


def set(doc, ptr, value):
    toks = parse(ptr)
    if not toks:
        return value
    new = copy.deepcopy(doc)
    parent = _parent(new, toks[:-1])
    last = toks[-1]
    if isinstance(parent, dict):
        parent[last] = value
    elif isinstance(parent, list):
        if last == "-":
            parent.append(value)
        else:
            i = _index(last)
            if i > len(parent):
                raise IndexError(last)
            parent.insert(i, value)
    else:
        raise KeyError(last)
    return new


def remove(doc, ptr):
    toks = parse(ptr)
    if not toks:
        raise ValueError("cannot remove the root")
    new = copy.deepcopy(doc)
    parent = _parent(new, toks[:-1])
    last = toks[-1]
    if isinstance(parent, dict):
        if last not in parent:
            raise KeyError(last)
        del parent[last]
    elif isinstance(parent, list):
        i = _index(last)
        if i >= len(parent):
            raise IndexError(last)
        del parent[i]
    else:
        raise KeyError(last)
    return new
'''}, ['tests/test_pointer.py'])

# 112 business days
task(112, 'Calendar arithmetic',
 'Implement cal.py as documented using only datetime.date. Do not change the tests.',
 {'cal.py': '''import datetime


def add_months(d, n):
    """Return the date n months after d (n may be negative or zero). Keep the day of month, but if the target month is
    shorter use its last day (Jan 31 + 1 month = Feb 28/29). d must be a datetime.date but NOT a datetime.datetime (a
    datetime raises TypeError); n must be an int (not bool) else TypeError. Results outside year 1..9999 raise
    OverflowError."""
    raise NotImplementedError


def business_days(start, end, holidays=()):
    """Count business days in the half-open range [start, end): Monday-Friday that are not in `holidays` (an iterable
    of dates; duplicates and weekend dates are harmless). If end < start return the NEGATIVE of business_days(end, start).
    start == end gives 0. Same date-type rules as add_months."""
    raise NotImplementedError


def add_business_days(d, n, holidays=()):
    """Return the date that is n business days after d (n may be negative; 0 returns d unchanged even if d is not a
    business day). Moving forward: each step goes to the next Monday-Friday date not in holidays; backwards likewise.
    Same type rules."""
    raise NotImplementedError


def is_leap(year):
    """Gregorian leap year test. year must be an int in 1..9999 (not bool), else ValueError."""
    raise NotImplementedError
''', 'tests/test_cal.py': '''import datetime
from cal import add_months

def test_basic():
    assert add_months(datetime.date(2024, 1, 31), 1) == datetime.date(2024, 2, 29)
'''},
 {'tests/test_hidden_cal.py': '''import datetime as dt
import pytest
from cal import add_months, business_days, add_business_days, is_leap

D = dt.date

def test_add_months():
    assert add_months(D(2023, 1, 31), 1) == D(2023, 2, 28)
    assert add_months(D(2024, 1, 31), 1) == D(2024, 2, 29)
    assert add_months(D(2024, 3, 31), -1) == D(2024, 2, 29)
    assert add_months(D(2024, 5, 15), 0) == D(2024, 5, 15)
    assert add_months(D(2024, 11, 30), 3) == D(2025, 2, 28)
    assert add_months(D(2024, 1, 31), 12) == D(2025, 1, 31)
    assert add_months(D(2024, 1, 15), -13) == D(2022, 12, 15)
    assert add_months(D(2024, 12, 31), 2) == D(2025, 2, 28)
    assert add_months(D(2000, 2, 29), 48) == D(2004, 2, 29)
    assert add_months(D(2000, 2, 29), 12) == D(2001, 2, 28)

def test_add_months_errors():
    with pytest.raises(TypeError):
        add_months(dt.datetime(2024, 1, 1), 1)
    with pytest.raises(TypeError):
        add_months("2024-01-01", 1)
    for n in (1.0, True, "1", None):
        with pytest.raises(TypeError):
            add_months(D(2024, 1, 1), n)
    with pytest.raises(OverflowError):
        add_months(D(9999, 12, 1), 1)
    with pytest.raises(OverflowError):
        add_months(D(1, 1, 1), -1)
    assert add_months(D(9999, 11, 30), 1) == D(9999, 12, 30)

def test_business_days_basic():
    mon, fri, nxt = D(2024, 5, 6), D(2024, 5, 10), D(2024, 5, 13)
    assert business_days(mon, fri) == 4          # Mon..Thu
    assert business_days(mon, nxt) == 5
    assert business_days(mon, mon) == 0
    assert business_days(D(2024, 5, 11), D(2024, 5, 13)) == 0   # Sat, Sun
    assert business_days(D(2024, 5, 4), D(2024, 5, 14)) == 6    # Sat..Mon: Mon-Fri + Mon(13)

def test_business_days_negative():
    assert business_days(D(2024, 5, 13), D(2024, 5, 6)) == -5
    assert business_days(D(2024, 5, 10), D(2024, 5, 6)) == -4

def test_holidays():
    h = [D(2024, 5, 8), D(2024, 5, 8), D(2024, 5, 11)]
    assert business_days(D(2024, 5, 6), D(2024, 5, 13), h) == 4
    assert business_days(D(2024, 5, 6), D(2024, 5, 13), iter(h)) == 4
    assert business_days(D(2024, 5, 8), D(2024, 5, 9), [D(2024, 5, 8)]) == 0
    assert business_days(D(2024, 5, 7), D(2024, 5, 8), [D(2024, 5, 8)]) == 1   # end is exclusive

def test_add_business_days():
    fri = D(2024, 5, 10)
    assert add_business_days(fri, 1) == D(2024, 5, 13)
    assert add_business_days(fri, 5) == D(2024, 5, 17)
    assert add_business_days(D(2024, 5, 13), -1) == fri
    assert add_business_days(D(2024, 5, 11), 1) == D(2024, 5, 13)    # from Saturday
    assert add_business_days(D(2024, 5, 11), -1) == fri
    assert add_business_days(D(2024, 5, 11), 0) == D(2024, 5, 11)
    assert add_business_days(fri, 1, [D(2024, 5, 13)]) == D(2024, 5, 14)
    assert add_business_days(fri, -1, [fri - dt.timedelta(days=1)]) == D(2024, 5, 8)
    assert add_business_days(D(2024, 5, 6), 10) == D(2024, 5, 20)

def test_business_consistency():
    a = D(2024, 1, 1)
    for n in range(0, 30):
        b = add_business_days(a, n)
        assert business_days(a, b) == n

def test_is_leap():
    assert [is_leap(y) for y in (1900, 2000, 2023, 2024, 2100, 4, 1)] == [False, True, False, True, False, True, False]
    for bad in (0, 10000, -4, 2000.0, True, "2000", None):
        with pytest.raises(ValueError):
            is_leap(bad)
'''},
 {'cal.py': '''import datetime
import calendar


def _chk_date(d):
    if type(d) is not datetime.date:
        raise TypeError("d must be a datetime.date")


def add_months(d, n):
    _chk_date(d)
    if type(n) is not int:
        raise TypeError("n must be int")
    idx = d.year * 12 + (d.month - 1) + n
    y, m = divmod(idx, 12)
    m += 1
    if y < 1 or y > 9999:
        raise OverflowError("year out of range")
    last = calendar.monthrange(y, m)[1]
    return datetime.date(y, m, min(d.day, last))


def _hol(holidays):
    return set(holidays)


def business_days(start, end, holidays=()):
    _chk_date(start)
    _chk_date(end)
    hs = _hol(holidays)
    if end < start:
        return -business_days(end, start, hs)
    n = 0
    d = start
    one = datetime.timedelta(days=1)
    while d < end:
        if d.weekday() < 5 and d not in hs:
            n += 1
        d += one
    return n


def add_business_days(d, n, holidays=()):
    _chk_date(d)
    if type(n) is not int:
        raise TypeError("n must be int")
    hs = _hol(holidays)
    step = datetime.timedelta(days=1 if n >= 0 else -1)
    left = abs(n)
    cur = d
    while left:
        cur += step
        if cur.weekday() < 5 and cur not in hs:
            left -= 1
    return cur


def is_leap(year):
    if type(year) is not int or year < 1 or year > 9999:
        raise ValueError("year")
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
'''}, ['tests/test_cal.py'])
