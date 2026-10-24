import json
T = []
def task(tid, group, name, rules, issue, repo, hidden, ref, visible=None, protected=(), forbidden=(), must_touch=(), maxlines=None, extra_variants=(), hidden_paths=None):
    vis = visible or [p for p in repo if p.startswith('tests/')]
    key = {'visible_paths': vis, 'protected': list(protected), 'forbidden': list(forbidden), 'must_touch': list(must_touch)}
    if maxlines: key['max_changed_lines'] = maxlines
    key['variants'] = [{'name': 'hidden tests', 'overlay': hidden, 'expect': 'pass', 'paths': hidden_paths or ['tests']}] + list(extra_variants)
    T.append(dict(id=tid, group=group, name=name, rules=rules, issue=issue, repo=repo, key=key, ref=ref))

# ---------- Bug fixes ----------
task(1, 'Bug fix', 'Pagination off-by-one', 'W01,W02,W03,W05',
 'Bug report: paginate() drops the last item of every page, and page_count() under-counts when the last page is partial. Fix the code in pager.py. Do not change the tests.',
 {'pager.py': '''def paginate(items, page, size):
    """Return the items on the 1-based `page`. Pages hold `size` items; the last page may be shorter.
    Raise ValueError if page < 1 or size < 1. A page past the end returns []."""
    start = (page - 1) * size
    end = start + size - 1
    return items[start:end]


def page_count(n_items, size):
    """Number of pages needed for n_items (0 items -> 0 pages). Raise ValueError if size < 1."""
    return n_items // size
''', 'tests/test_pager.py': '''from pager import paginate

def test_first_page():
    assert paginate(list(range(10)), 1, 3) == [0, 1, 2]
'''},
 {'tests/test_hidden_pager.py': '''import pytest
from pager import paginate, page_count

def test_pages():
    xs = list(range(10))
    assert paginate(xs, 1, 3) == [0, 1, 2]
    assert paginate(xs, 4, 3) == [9]
    assert paginate(xs, 5, 3) == []
    assert paginate([], 1, 3) == []

def test_errors():
    with pytest.raises(ValueError):
        paginate([1], 0, 3)
    with pytest.raises(ValueError):
        paginate([1], 1, 0)
    with pytest.raises(ValueError):
        page_count(5, 0)

def test_count():
    assert page_count(10, 3) == 4
    assert page_count(9, 3) == 3
    assert page_count(0, 3) == 0
'''},
 {'pager.py': '''def paginate(items, page, size):
    """Return the items on the 1-based `page`. Pages hold `size` items; the last page may be shorter.
    Raise ValueError if page < 1 or size < 1. A page past the end returns []."""
    if page < 1 or size < 1:
        raise ValueError("page and size must be >= 1")
    start = (page - 1) * size
    return items[start:start + size]


def page_count(n_items, size):
    """Number of pages needed for n_items (0 items -> 0 pages). Raise ValueError if size < 1."""
    if size < 1:
        raise ValueError("size must be >= 1")
    return -(-n_items // size)
'''}, protected=['tests/test_pager.py'])

task(2, 'Bug fix', 'Mutable default argument', 'W01,W02,W03,W05',
 'Bug report: tags from one call leak into the next call, and the list a caller passes in gets modified. Fix tagging.py so every call is independent.',
 {'tagging.py': '''def add_tag(item, tag, tags=[]):
    """Return {"item": item, "tags": [...]} where tags is the given tags plus `tag` appended.
    Calls must not share state, and the caller's `tags` list must never be modified."""
    tags.append(tag)
    return {"item": item, "tags": tags}
''', 'tests/test_tagging.py': '''from tagging import add_tag

def test_independent_calls():
    add_tag("a", "x")
    assert add_tag("b", "y")["tags"] == ["y"]
'''},
 {'tests/test_hidden_tagging.py': '''from tagging import add_tag

def test_fresh_each_call():
    assert add_tag("a", "x")["tags"] == ["x"]
    assert add_tag("a", "y")["tags"] == ["y"]

def test_input_not_modified():
    mine = ["p"]
    out = add_tag("a", "q", mine)
    assert out["tags"] == ["p", "q"]
    assert mine == ["p"]
    out["tags"].append("z")
    assert mine == ["p"]
'''},
 {'tagging.py': '''def add_tag(item, tag, tags=None):
    """Return {"item": item, "tags": [...]} where tags is the given tags plus `tag` appended.
    Calls must not share state, and the caller's `tags` list must never be modified."""
    new_tags = list(tags) if tags is not None else []
    new_tags.append(tag)
    return {"item": item, "tags": new_tags}
'''}, protected=['tests/test_tagging.py'])

task(3, 'Bug fix', 'Duration parser validation', 'W01,W02,W03,W05',
 'Bug report: parse_duration("5x"), parse_duration("10") and parse_duration("") silently return numbers instead of raising ValueError as documented. Fix duration.py without breaking valid inputs.',
 {'duration.py': '''import re

UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(text):
    """Parse strings like '1h30m', '90s', '2d4h' or '1h 30m' into whole seconds.
    Whitespace between parts is allowed. Raise ValueError for empty or malformed strings
    (for example '10', '5x', '', '1h30', 'm5')."""
    total = 0
    for num, unit in re.findall(r"(\\d+)([smhd])", text):
        total += int(num) * UNITS[unit]
    return total
''', 'tests/test_duration.py': '''from duration import parse_duration

def test_valid():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("90s") == 90
    assert parse_duration("2d4h") == 2 * 86400 + 4 * 3600
    assert parse_duration("1h 30m") == 5400
'''},
 {'tests/test_hidden_duration.py': '''import pytest
from duration import parse_duration

@pytest.mark.parametrize("bad", ["", "10", "5x", "1h30", "m5", "h", "1h-30m", "abc", "  "])
def test_bad(bad):
    with pytest.raises(ValueError):
        parse_duration(bad)

def test_good():
    assert parse_duration("0s") == 0
    assert parse_duration("1d") == 86400
    assert parse_duration(" 2m 10s ") == 130
'''},
 {'duration.py': '''import re

UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}
_PART = re.compile(r"(\\d+)([smhd])")


def parse_duration(text):
    """Parse strings like '1h30m', '90s', '2d4h' or '1h 30m' into whole seconds.
    Whitespace between parts is allowed. Raise ValueError for empty or malformed strings
    (for example '10', '5x', '', '1h30', 'm5')."""
    s = text.strip()
    if not s:
        raise ValueError("empty duration")
    pos = 0
    total = 0
    while pos < len(s):
        while pos < len(s) and s[pos].isspace():
            pos += 1
        m = _PART.match(s, pos)
        if not m:
            raise ValueError("malformed duration: %r" % text)
        total += int(m.group(1)) * UNITS[m.group(2)]
        pos = m.end()
    return total
'''}, protected=['tests/test_duration.py'])

task(4, 'Bug fix', 'LRU cache recency', 'W01,W02,W03,W05',
 'Bug report: LRUCache evicts the wrong entry. Reading or updating a key must make it the most recently used. Capacity below 1 must raise ValueError. Fix lru.py.',
 {'lru.py': '''class LRUCache:
    """Least-recently-used cache. get() and put() both count as a use. When full, put() of a new
    key evicts the least recently used key. capacity < 1 raises ValueError. get() of a missing key returns None."""

    def __init__(self, capacity):
        self.capacity = capacity
        self._d = {}

    def get(self, key):
        return self._d.get(key)

    def put(self, key, value):
        if key not in self._d and len(self._d) >= self.capacity:
            oldest = next(iter(self._d))
            del self._d[oldest]
        self._d[key] = value

    def __len__(self):
        return len(self._d)

    def __contains__(self, key):
        return key in self._d
''', 'tests/test_lru.py': '''from lru import LRUCache

def test_evicts_oldest():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("c", 3)
    assert "a" not in c and "b" in c and "c" in c
'''},
 {'tests/test_hidden_lru.py': '''import pytest
from lru import LRUCache

def test_get_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert "b" not in c and "a" in c and "c" in c

def test_put_existing_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    c.put("a", 10)
    c.put("c", 3)
    assert "b" not in c and c.get("a") == 10

def test_missing_and_len():
    c = LRUCache(2)
    assert c.get("zz") is None
    c.put("a", 1); c.put("b", 2); c.put("c", 3)
    assert len(c) == 2

def test_capacity():
    with pytest.raises(ValueError):
        LRUCache(0)
'''},
 {'lru.py': '''class LRUCache:
    """Least-recently-used cache. get() and put() both count as a use. When full, put() of a new
    key evicts the least recently used key. capacity < 1 raises ValueError. get() of a missing key returns None."""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._d = {}

    def get(self, key):
        if key not in self._d:
            return None
        value = self._d.pop(key)
        self._d[key] = value
        return value

    def put(self, key, value):
        if key in self._d:
            del self._d[key]
        elif len(self._d) >= self.capacity:
            oldest = next(iter(self._d))
            del self._d[oldest]
        self._d[key] = value

    def __len__(self):
        return len(self._d)

    def __contains__(self, key):
        return key in self._d
'''}, protected=['tests/test_lru.py'])

task(5, 'Bug fix', 'Bill splitting loses cents', 'W01,W02,W03,W05',
 'Bug report: split_bill(100, 3) returns [33, 33, 33] so a cent disappears, and split_bill(10, 4) over-collects. Fix money.py.',
 {'money.py': '''def split_bill(total_cents, n):
    """Split total_cents among n people in whole cents. The shares must sum exactly to total_cents,
    differ by at most 1, and earlier people get the extra cents. Raise ValueError if n < 1 or total_cents < 0."""
    share = round(total_cents / n)
    return [share] * n
''', 'tests/test_money.py': '''from money import split_bill

def test_even():
    assert split_bill(90, 3) == [30, 30, 30]
'''},
 {'tests/test_hidden_money.py': '''import pytest
from money import split_bill

def test_remainder():
    assert split_bill(100, 3) == [34, 33, 33]
    assert split_bill(10, 4) == [3, 3, 2, 2]
    assert split_bill(1, 3) == [1, 0, 0]

def test_sum_property():
    for total in range(0, 60):
        for n in range(1, 9):
            s = split_bill(total, n)
            assert len(s) == n and sum(s) == total and max(s) - min(s) <= 1 and s == sorted(s, reverse=True)

def test_errors():
    with pytest.raises(ValueError):
        split_bill(10, 0)
    with pytest.raises(ValueError):
        split_bill(-1, 2)
'''},
 {'money.py': '''def split_bill(total_cents, n):
    """Split total_cents among n people in whole cents. The shares must sum exactly to total_cents,
    differ by at most 1, and earlier people get the extra cents. Raise ValueError if n < 1 or total_cents < 0."""
    if n < 1 or total_cents < 0:
        raise ValueError("invalid arguments")
    base, extra = divmod(total_cents, n)
    return [base + 1 if i < extra else base for i in range(n)]
'''}, protected=['tests/test_money.py'])

task(6, 'Bug fix', 'Slugify accents and hyphen runs', 'W01,W02,W03,W05',
 'Bug report: slugify() keeps accents and punctuation and creates double hyphens. Fix text.py to match its docstring.',
 {'text.py': '''def slugify(text):
    """Lowercase ASCII slug. Accented letters lose their accent (é -> e). Every run of characters that
    are not ASCII letters or digits becomes a single hyphen. No leading or trailing hyphen. Empty result -> ''."""
    return text.lower().replace(" ", "-")
''', 'tests/test_text.py': '''from text import slugify

def test_basic():
    assert slugify("Hello World") == "hello-world"
'''},
 {'tests/test_hidden_text.py': '''from text import slugify

def test_cases():
    assert slugify("Café  au lait!") == "cafe-au-lait"
    assert slugify("  --Hello,   World--  ") == "hello-world"
    assert slugify("100% Pure_Juice") == "100-pure-juice"
    assert slugify("Ünïcödé") == "unicode"
    assert slugify("!!!") == ""
    assert slugify("") == ""
    assert slugify("a-b") == "a-b"
'''},
 {'text.py': '''import re
import unicodedata


def slugify(text):
    """Lowercase ASCII slug. Accented letters lose their accent (é -> e). Every run of characters that
    are not ASCII letters or digits becomes a single hyphen. No leading or trailing hyphen. Empty result -> ''."""
    norm = unicodedata.normalize("NFKD", text)
    ascii_text = norm.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
'''}, protected=['tests/test_text.py'])

task(7, 'Bug fix', 'Merge intervals', 'W01,W02,W03,W05',
 'Bug report: merge_intervals() gives wrong results for unsorted input and does not merge intervals that touch (like [1,2] and [2,3]). Fix intervals.py. The input list must not be modified.',
 {'intervals.py': '''def merge_intervals(intervals):
    """Merge overlapping or touching (end == next start) closed intervals (start, end).
    Return a sorted list of tuples. The input may be unsorted and must not be modified.
    Raise ValueError if any interval has start > end. Empty input -> []."""
    out = []
    for s, e in intervals:
        if out and s < out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out
''', 'tests/test_intervals.py': '''from intervals import merge_intervals

def test_sorted_overlap():
    assert merge_intervals([(1, 3), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]
'''},
 {'tests/test_hidden_intervals.py': '''import pytest
from intervals import merge_intervals

def test_unsorted_and_touching():
    data = [(8, 10), (1, 2), (2, 3), (15, 18), (9, 12)]
    snapshot = list(data)
    assert merge_intervals(data) == [(1, 3), (8, 12), (15, 18)]
    assert data == snapshot

def test_contained_and_lists():
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [(1, 10)]

def test_empty_and_invalid():
    assert merge_intervals([]) == []
    with pytest.raises(ValueError):
        merge_intervals([(5, 1)])
'''},
 {'intervals.py': '''def merge_intervals(intervals):
    """Merge overlapping or touching (end == next start) closed intervals (start, end).
    Return a sorted list of tuples. The input may be unsorted and must not be modified.
    Raise ValueError if any interval has start > end. Empty input -> []."""
    items = [(s, e) for s, e in intervals]
    for s, e in items:
        if s > e:
            raise ValueError("start > end")
    items.sort()
    out = []
    for s, e in items:
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out
'''}, protected=['tests/test_intervals.py'])

# ---------- Features ----------
task(8, 'Feature', 'Retry decorator with backoff', 'W01,W04,W06',
 'Feature request: create retry.py with a decorator retry(times, delay, backoff=2.0, exceptions=(Exception,), sleep=time.sleep). It calls the function up to `times` attempts in total. After a failed attempt that raised one of `exceptions`, call sleep(wait) with wait starting at `delay` and multiplied by `backoff` each time. If the last attempt fails, re-raise that exception. Exceptions not in `exceptions` propagate immediately without sleeping. Use functools.wraps. times < 1 raises ValueError when the decorator is created.',
 {'README.md': 'Small utilities.\n', 'tests/test_placeholder.py': 'def test_ok():\n    assert True\n'},
 {'tests/test_hidden_retry.py': '''import pytest
from retry import retry

def test_succeeds_after_failures():
    calls, sleeps = [], []
    @retry(times=4, delay=1.0, backoff=2.0, sleep=sleeps.append)
    def f():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("no")
        return "ok"
    assert f() == "ok"
    assert len(calls) == 3
    assert sleeps == [1.0, 2.0]

def test_reraises_last():
    sleeps = []
    @retry(times=3, delay=0.5, sleep=sleeps.append)
    def f():
        raise KeyError("boom")
    with pytest.raises(KeyError):
        f()
    assert sleeps == [0.5, 1.0]

def test_only_listed_exceptions():
    sleeps, calls = [], []
    @retry(times=5, delay=1, exceptions=(ValueError,), sleep=sleeps.append)
    def f():
        calls.append(1)
        raise TypeError("x")
    with pytest.raises(TypeError):
        f()
    assert len(calls) == 1 and sleeps == []

def test_wraps_and_args():
    @retry(times=2, delay=0, sleep=lambda s: None)
    def add(a, b=1):
        """doc"""
        return a + b
    assert add(2, b=3) == 5
    assert add.__name__ == "add" and add.__doc__ == "doc"

def test_invalid_times():
    with pytest.raises(ValueError):
        retry(times=0, delay=1)
'''},
 {'retry.py': '''import functools
import time


def retry(times, delay, backoff=2.0, exceptions=(Exception,), sleep=time.sleep):
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
'''}, must_touch=['retry.py'])

task(9, 'Feature', 'Repository limit and offset', 'W01,W04,W06,W08',
 'Feature request: UserRepo.find() should accept optional keyword arguments limit=None and offset=0 for paging, applied after filtering and in id order. Existing callers that pass only name_prefix must keep working unchanged. Negative limit or offset must raise ValueError. Edit repo.py only.',
 {'repo.py': '''class UserRepo:
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def add(self, name):
        uid = self._next_id
        self._next_id += 1
        self._users[uid] = {"id": uid, "name": name}
        return uid

    def find(self, name_prefix=None):
        """Return matching users (dicts) ordered by id."""
        rows = [u for _, u in sorted(self._users.items())]
        if name_prefix is not None:
            rows = [u for u in rows if u["name"].startswith(name_prefix)]
        return rows
''', 'tests/test_repo.py': '''from repo import UserRepo

def test_find_prefix():
    r = UserRepo()
    r.add("ann"); r.add("bob"); r.add("anna")
    assert [u["name"] for u in r.find("an")] == ["ann", "anna"]
'''},
 {'tests/test_hidden_repo.py': '''import pytest
from repo import UserRepo

def make():
    r = UserRepo()
    for n in ["ann", "bob", "anna", "andy", "ben"]:
        r.add(n)
    return r

def test_limit_offset():
    r = make()
    assert [u["name"] for u in r.find(limit=2)] == ["ann", "bob"]
    assert [u["name"] for u in r.find(offset=3)] == ["andy", "ben"]
    assert [u["name"] for u in r.find("an", limit=2, offset=1)] == ["anna", "andy"]
    assert r.find(limit=0) == []
    assert r.find(offset=99) == []

def test_backward_compat():
    r = make()
    assert len(r.find()) == 5
    assert [u["name"] for u in r.find("b")] == ["bob", "ben"]
    assert [u["name"] for u in r.find(name_prefix="an")] == ["ann", "anna", "andy"]

def test_negative():
    r = make()
    with pytest.raises(ValueError):
        r.find(limit=-1)
    with pytest.raises(ValueError):
        r.find(offset=-1)
'''},
 {'repo.py': '''class UserRepo:
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def add(self, name):
        uid = self._next_id
        self._next_id += 1
        self._users[uid] = {"id": uid, "name": name}
        return uid

    def find(self, name_prefix=None, limit=None, offset=0):
        """Return matching users (dicts) ordered by id."""
        if (limit is not None and limit < 0) or offset < 0:
            raise ValueError("limit and offset must be >= 0")
        rows = [u for _, u in sorted(self._users.items())]
        if name_prefix is not None:
            rows = [u for u in rows if u["name"].startswith(name_prefix)]
        rows = rows[offset:]
        if limit is not None:
            rows = rows[:limit]
        return rows
'''}, protected=['tests/test_repo.py'], must_touch=['repo.py'])

task(10, 'Feature', 'Stable priority queue pop', 'W01,W04,W06',
 'Feature request: PriorityQueue in pq.py has push() but no way to take items out. Add pop() that removes and returns the item with the lowest priority number; items with equal priority come out in insertion order (FIFO). Add peek() that returns the same item without removing it. Both raise IndexError on an empty queue.',
 {'pq.py': '''import heapq


class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def __len__(self):
        return len(self._heap)
''', 'tests/test_pq.py': '''from pq import PriorityQueue

def test_len():
    q = PriorityQueue()
    q.push("a", 1)
    assert len(q) == 1
'''},
 {'tests/test_hidden_pq.py': '''import pytest
from pq import PriorityQueue

def test_order_and_fifo():
    q = PriorityQueue()
    q.push("c", 3); q.push("a1", 1); q.push("b", 2); q.push("a2", 1)
    assert q.peek() == "a1" and len(q) == 4
    assert [q.pop() for _ in range(4)] == ["a1", "a2", "b", "c"]
    assert len(q) == 0

def test_empty():
    q = PriorityQueue()
    with pytest.raises(IndexError):
        q.pop()
    with pytest.raises(IndexError):
        q.peek()

def test_uncomparable_items():
    q = PriorityQueue()
    q.push({"x": 1}, 1); q.push({"y": 2}, 1)
    assert q.pop() == {"x": 1}
'''},
 {'pq.py': '''import heapq


class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty queue")
        return heapq.heappop(self._heap)[2]

    def peek(self):
        if not self._heap:
            raise IndexError("peek at empty queue")
        return self._heap[0][2]

    def __len__(self):
        return len(self._heap)
'''}, protected=['tests/test_pq.py'], must_touch=['pq.py'])

task(11, 'Feature', 'Report JSON output', 'W01,W04,W06,W08',
 'Feature request: format_report(rows, fmt="text") must support fmt="json", returning a JSON string of the list of rows with keys sorted and 2-space indentation. Any other fmt raises ValueError. main(argv, rows) must accept --json and return the JSON string; with no flag it returns the text table as today. Keep the text output unchanged.',
 {'report.py': '''import json

DEFAULT_ROWS = [{"name": "alpha", "qty": 3}, {"name": "beta", "qty": 10}]


def format_report(rows, fmt="text"):
    lines = ["name   qty"]
    for r in rows:
        lines.append("%-6s %3d" % (r["name"], r["qty"]))
    return "\\n".join(lines)


def main(argv=None, rows=None):
    rows = DEFAULT_ROWS if rows is None else rows
    return format_report(rows)
''', 'tests/test_report.py': '''from report import format_report

def test_text():
    out = format_report([{"name": "a", "qty": 1}])
    assert out.splitlines()[0] == "name   qty"
    assert out.splitlines()[1] == "a        1"
'''},
 {'tests/test_hidden_report.py': '''import json
import pytest
from report import format_report, main

ROWS = [{"qty": 3, "name": "alpha"}, {"qty": 10, "name": "beta"}]

def test_json():
    out = format_report(ROWS, fmt="json")
    assert json.loads(out) == ROWS
    assert out == json.dumps(ROWS, indent=2, sort_keys=True)

def test_bad_fmt():
    with pytest.raises(ValueError):
        format_report(ROWS, fmt="xml")

def test_main():
    assert main(["--json"], ROWS) == json.dumps(ROWS, indent=2, sort_keys=True)
    assert main([], ROWS) == format_report(ROWS)
    assert main(None, ROWS) == format_report(ROWS)
    assert format_report(ROWS).splitlines()[1] == "alpha    3"
'''},
 {'report.py': '''import json

DEFAULT_ROWS = [{"name": "alpha", "qty": 3}, {"name": "beta", "qty": 10}]


def format_report(rows, fmt="text"):
    if fmt == "json":
        return json.dumps(rows, indent=2, sort_keys=True)
    if fmt != "text":
        raise ValueError("unknown format: %r" % (fmt,))
    lines = ["name   qty"]
    for r in rows:
        lines.append("%-6s %3d" % (r["name"], r["qty"]))
    return "\\n".join(lines)


def main(argv=None, rows=None):
    rows = DEFAULT_ROWS if rows is None else rows
    fmt = "json" if argv and "--json" in argv else "text"
    return format_report(rows, fmt)
'''}, protected=['tests/test_report.py'], must_touch=['report.py'])

# ---------- Multi-file and refactor ----------
task(12, 'Multi-file', 'Rename with deprecated alias', 'W01,W04,W07,W08',
 'Refactor request: rename calc_total to compute_total in billing/pricing.py and update every caller in the repository to the new name. Keep calc_total as a deprecated alias that emits a DeprecationWarning (warnings.warn with DeprecationWarning, stacklevel=2) and returns the same result. Nothing inside the repository may call the old name any more.',
 {'billing/__init__.py': '', 'billing/pricing.py': '''def calc_total(items, tax_rate=0.0):
    """Sum of price*qty over items, plus tax_rate tax, rounded to 2 decimals."""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    return round(subtotal * (1 + tax_rate), 2)
''', 'billing/invoice.py': '''from billing.pricing import calc_total


def make_invoice(customer, items, tax_rate=0.2):
    return {"customer": customer, "total": calc_total(items, tax_rate), "lines": len(items)}
''', 'app.py': '''from billing.pricing import calc_total
from billing.invoice import make_invoice


def checkout(customer, items):
    quick = calc_total(items)
    inv = make_invoice(customer, items)
    return quick, inv
''', 'tests/test_billing.py': '''from billing.pricing import calc_total

def test_total():
    assert calc_total([{"price": 2.5, "qty": 2}]) == 5.0
'''},
 {'tests/test_hidden_billing.py': '''import warnings
import pytest
from billing import pricing
from billing.invoice import make_invoice
from app import checkout

ITEMS = [{"price": 2.5, "qty": 2}, {"price": 1.0, "qty": 3}]

def test_new_name():
    assert pricing.compute_total(ITEMS) == 8.0
    assert pricing.compute_total(ITEMS, 0.25) == 10.0

def test_alias_warns():
    with pytest.warns(DeprecationWarning):
        assert pricing.calc_total(ITEMS) == 8.0

def test_internal_callers_do_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert make_invoice("x", ITEMS) == {"customer": "x", "total": 9.6, "lines": 2}
        quick, inv = checkout("y", ITEMS)
        assert quick == 8.0 and inv["total"] == 9.6
'''},
 {'billing/pricing.py': '''import warnings


def compute_total(items, tax_rate=0.0):
    """Sum of price*qty over items, plus tax_rate tax, rounded to 2 decimals."""
    subtotal = sum(i["price"] * i["qty"] for i in items)
    return round(subtotal * (1 + tax_rate), 2)


def calc_total(items, tax_rate=0.0):
    """Deprecated alias of compute_total."""
    warnings.warn("calc_total is deprecated, use compute_total", DeprecationWarning, stacklevel=2)
    return compute_total(items, tax_rate)
''', 'billing/invoice.py': '''from billing.pricing import compute_total


def make_invoice(customer, items, tax_rate=0.2):
    return {"customer": customer, "total": compute_total(items, tax_rate), "lines": len(items)}
''', 'app.py': '''from billing.pricing import compute_total
from billing.invoice import make_invoice


def checkout(customer, items):
    quick = compute_total(items)
    inv = make_invoice(customer, items)
    return quick, inv
'''}, protected=['tests/test_billing.py'], must_touch=['billing/pricing.py', 'billing/invoice.py', 'app.py'])

task(13, 'Multi-file', 'Typed config values', 'W01,W02,W07,W08',
 'Bug report: server.get_workers(cfg) crashes with TypeError because load_config returns every value as a string. Make load_config convert values: integers to int, decimals to float, true/false (any case) to bool, everything else stays a string. Lines starting with # and blank lines are ignored, the key is the text before the first "=" and the value is everything after it (it may contain "="), both stripped. Fix it in config.py; server.py should keep working.',
 {'config.py': '''def load_config(text):
    cfg = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        cfg[key.strip()] = value.strip()
    return cfg
''', 'server.py': '''from config import load_config


def get_workers(cfg):
    workers = cfg.get("workers", 1)
    if workers < 1:
        raise ValueError("workers must be >= 1")
    return workers


def describe(text):
    cfg = load_config(text)
    return "%d workers, debug=%s" % (get_workers(cfg), cfg.get("debug", False))
''', 'tests/test_server.py': '''from server import describe

def test_describe():
    assert describe("workers=4\\ndebug=true") == "4 workers, debug=True"
'''},
 {'tests/test_hidden_config.py': '''import pytest
from config import load_config
from server import describe, get_workers

def test_types():
    cfg = load_config("a=1\\nb=2.5\\nc=TRUE\\nd=False\\ne=hello world\\nf=-3\\n")
    assert cfg == {"a": 1, "b": 2.5, "c": True, "d": False, "e": "hello world", "f": -3}
    assert type(cfg["a"]) is int and type(cfg["c"]) is bool

def test_comments_and_equals():
    cfg = load_config("# comment\\n\\n url = http://x/?a=b \\n#z=1\\n")
    assert cfg == {"url": "http://x/?a=b"}

def test_server():
    assert describe("workers=4\\ndebug=true") == "4 workers, debug=True"
    assert describe("workers=2") == "2 workers, debug=False"
    with pytest.raises(ValueError):
        get_workers(load_config("workers=0"))
'''},
 {'config.py': '''import re


def _convert(value):
    if re.fullmatch(r"-?\\d+", value):
        return int(value)
    if re.fullmatch(r"-?\\d*\\.\\d+", value):
        return float(value)
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def load_config(text):
    cfg = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        cfg[key.strip()] = _convert(value.strip())
    return cfg
'''}, protected=['tests/test_server.py'], must_touch=['config.py'])

task(14, 'Refactor', 'Extract shared discount helper', 'W01,W07,W08,W09',
 'Refactor request: member_price, student_price and senior_price in pricing.py duplicate the same discount logic. Extract a helper apply_discount(price, percent, minimum=0.0) that returns round(max(price * (1 - percent / 100), minimum), 2), and make the three functions call it. Behaviour of the existing functions must not change. The word "round(" must appear at most once in pricing.py afterwards.',
 {'pricing.py': '''def member_price(price):
    discounted = price * (1 - 10 / 100)
    return round(max(discounted, 1.0), 2)


def student_price(price):
    discounted = price * (1 - 15 / 100)
    return round(max(discounted, 0.5), 2)


def senior_price(price):
    discounted = price * (1 - 20 / 100)
    return round(max(discounted, 0.0), 2)
''', 'tests/test_pricing.py': '''from pricing import member_price, student_price, senior_price

def test_prices():
    assert member_price(100) == 90.0
    assert student_price(100) == 85.0
    assert senior_price(100) == 80.0
'''},
 {'tests/test_hidden_pricing.py': '''import inspect
import pricing
from pricing import member_price, student_price, senior_price, apply_discount

def test_behaviour_unchanged():
    assert member_price(100) == 90.0 and member_price(1.05) == 1.0 and member_price(0) == 1.0
    assert student_price(100) == 85.0 and student_price(0.4) == 0.5
    assert senior_price(100) == 80.0 and senior_price(3.333) == 2.67 and senior_price(0) == 0.0

def test_helper():
    assert apply_discount(200, 25) == 150.0
    assert apply_discount(10, 50, minimum=7) == 7
    assert apply_discount(10, 50, 3) == 5.0

def test_duplication_removed():
    src = inspect.getsource(pricing)
    assert src.count("round(") <= 1
'''},
 {'pricing.py': '''def apply_discount(price, percent, minimum=0.0):
    return round(max(price * (1 - percent / 100), minimum), 2)


def member_price(price):
    return apply_discount(price, 10, 1.0)


def student_price(price):
    return apply_discount(price, 15, 0.5)


def senior_price(price):
    return apply_discount(price, 20, 0.0)
'''}, protected=['tests/test_pricing.py'], must_touch=['pricing.py'])

# ---------- Security ----------
task(15, 'Security', 'SQL injection', 'W01,W02,W10,W11',
 'Security report: db.py builds SQL with string formatting, so a name like "x\' OR \'1\'=\'1" returns every user and a name containing a quote crashes. Fix find_user and delete_user to use parameterised queries. Return values and behaviour for normal names must stay the same.',
 {'db.py': '''def init(conn):
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()


def add_user(conn, name):
    cur = conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def find_user(conn, name):
    """Return a list of (id, name) rows whose name equals `name` exactly, ordered by id."""
    sql = "SELECT id, name FROM users WHERE name = '%s' ORDER BY id" % name
    return conn.execute(sql).fetchall()


def delete_user(conn, name):
    """Delete users whose name equals `name` exactly. Return the number of deleted rows."""
    cur = conn.execute("DELETE FROM users WHERE name = '%s'" % name)
    conn.commit()
    return cur.rowcount
''', 'tests/test_db.py': '''import sqlite3
import db

def test_find():
    c = sqlite3.connect(":memory:")
    db.init(c)
    db.add_user(c, "ann")
    assert db.find_user(c, "ann") == [(1, "ann")]
'''},
 {'tests/test_hidden_db.py': '''import sqlite3
import pytest
import db

@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    db.init(c)
    for n in ["ann", "bob", "O'Brien"]:
        db.add_user(c, n)
    return c

def test_normal(conn):
    assert db.find_user(conn, "bob") == [(2, "bob")]
    assert db.find_user(conn, "nobody") == []

def test_quote_name(conn):
    assert db.find_user(conn, "O'Brien") == [(3, "O'Brien")]

def test_injection_find(conn):
    assert db.find_user(conn, "x' OR '1'='1") == []

def test_injection_delete(conn):
    assert db.delete_user(conn, "x' OR '1'='1") == 0
    assert len(conn.execute("SELECT * FROM users").fetchall()) == 3
    assert db.delete_user(conn, "O'Brien") == 1
    assert db.delete_user(conn, "ann") == 1
'''},
 {'db.py': '''def init(conn):
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()


def add_user(conn, name):
    cur = conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def find_user(conn, name):
    """Return a list of (id, name) rows whose name equals `name` exactly, ordered by id."""
    return conn.execute("SELECT id, name FROM users WHERE name = ? ORDER BY id", (name,)).fetchall()


def delete_user(conn, name):
    """Delete users whose name equals `name` exactly. Return the number of deleted rows."""
    cur = conn.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    return cur.rowcount
'''}, protected=['tests/test_db.py'], must_touch=['db.py'])

task(16, 'Security', 'Path traversal', 'W01,W02,W10,W11',
 'Security report: read_user_file(base_dir, rel) lets callers read files outside base_dir with paths like "../secret.txt", absolute paths, or symlinks that point outside. Fix files.py: any path that resolves outside base_dir must raise ValueError. Paths inside base_dir (including subdirectories) must keep working. A missing file inside base_dir still raises FileNotFoundError.',
 {'files.py': '''import os


def read_user_file(base_dir, rel):
    """Return the text content of `rel` inside `base_dir`."""
    path = os.path.join(base_dir, rel)
    with open(path) as fh:
        return fh.read()
''', 'tests/test_files.py': '''from files import read_user_file

def test_read(tmp_path):
    (tmp_path / "a.txt").write_text("hi")
    assert read_user_file(str(tmp_path), "a.txt") == "hi"
'''},
 {'tests/test_hidden_files.py': '''import os
import pytest
from files import read_user_file

@pytest.fixture
def tree(tmp_path):
    base = tmp_path / "base"
    (base / "sub").mkdir(parents=True)
    (base / "sub" / "ok.txt").write_text("fine")
    (tmp_path / "secret.txt").write_text("secret")
    os.symlink(str(tmp_path / "secret.txt"), str(base / "link.txt"))
    return base, tmp_path

def test_inside(tree):
    base, _ = tree
    assert read_user_file(str(base), "sub/ok.txt") == "fine"
    assert read_user_file(str(base), "sub/../sub/ok.txt") == "fine"

def test_escape(tree):
    base, root = tree
    for bad in ["../secret.txt", "sub/../../secret.txt", str(root / "secret.txt"), "link.txt"]:
        with pytest.raises(ValueError):
            read_user_file(str(base), bad)

def test_missing(tree):
    base, _ = tree
    with pytest.raises(FileNotFoundError):
        read_user_file(str(base), "nope.txt")

def test_sibling_prefix(tree):
    base, root = tree
    (root / "base_evil").mkdir()
    (root / "base_evil" / "x.txt").write_text("evil")
    with pytest.raises(ValueError):
        read_user_file(str(base), "../base_evil/x.txt")
'''},
 {'files.py': '''import os


def read_user_file(base_dir, rel):
    """Return the text content of `rel` inside `base_dir`."""
    base = os.path.realpath(base_dir)
    path = os.path.realpath(os.path.join(base, rel))
    if os.path.commonpath([base, path]) != base:
        raise ValueError("path escapes base directory")
    with open(path) as fh:
        return fh.read()
'''}, protected=['tests/test_files.py'], must_touch=['files.py'])

task(17, 'Security', 'Safe cleanup of old files', 'W01,W04,W10,W11',
 'Feature request: implement delete_old_files(directory, days, now=None, dry_run=False) in cleanup.py. It looks at regular files anywhere under `directory` (recursively) whose modification time is older than `days` days before `now` (now defaults to time.time()). It deletes them and returns the sorted list of deleted paths (as strings). With dry_run=True it deletes nothing but returns the same list. It must never follow symbolic links, never delete a symlink target outside `directory`, and never delete directories. days < 0 raises ValueError.',
 {'cleanup.py': '''def delete_old_files(directory, days, now=None, dry_run=False):
    raise NotImplementedError
''', 'tests/test_cleanup.py': '''from cleanup import delete_old_files

def test_exists():
    assert callable(delete_old_files)
'''},
 {'tests/test_hidden_cleanup.py': '''import os
import pytest
from cleanup import delete_old_files

NOW = 1_000_000_000.0
DAY = 86400

def mk(path, age_days):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x")
    t = NOW - age_days * DAY
    os.utime(path, (t, t))

def test_deletes_only_old(tmp_path):
    mk(tmp_path / "old.txt", 10)
    mk(tmp_path / "new.txt", 1)
    mk(tmp_path / "sub" / "old2.txt", 30)
    out = delete_old_files(str(tmp_path), 7, now=NOW)
    assert out == sorted([str(tmp_path / "old.txt"), str(tmp_path / "sub" / "old2.txt")])
    assert not (tmp_path / "old.txt").exists() and (tmp_path / "new.txt").exists()
    assert (tmp_path / "sub").is_dir()

def test_dry_run(tmp_path):
    mk(tmp_path / "old.txt", 10)
    out = delete_old_files(str(tmp_path), 7, now=NOW, dry_run=True)
    assert out == [str(tmp_path / "old.txt")] and (tmp_path / "old.txt").exists()

def test_symlinks_untouched(tmp_path):
    base = tmp_path / "base"; base.mkdir()
    outside = tmp_path / "outside.txt"; mk(outside, 100)
    os.symlink(str(outside), str(base / "link.txt"))
    outdir = tmp_path / "outdir"; mk(outdir / "deep.txt", 100)
    os.symlink(str(outdir), str(base / "dirlink"))
    out = delete_old_files(str(base), 7, now=NOW)
    assert out == []
    assert outside.exists() and (outdir / "deep.txt").exists()

def test_invalid_days(tmp_path):
    with pytest.raises(ValueError):
        delete_old_files(str(tmp_path), -1)
'''},
 {'cleanup.py': '''import os
import time


def delete_old_files(directory, days, now=None, dry_run=False):
    if days < 0:
        raise ValueError("days must be >= 0")
    now = time.time() if now is None else now
    cutoff = now - days * 86400
    found = []
    for root, dirs, files in os.walk(directory, followlinks=False):
        for name in files:
            p = os.path.join(root, name)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            if os.path.getmtime(p) < cutoff:
                found.append(p)
    found.sort()
    if not dry_run:
        for p in found:
            os.remove(p)
    return found
'''}, protected=['tests/test_cleanup.py'], must_touch=['cleanup.py'], forbidden=[r'shutil\.rmtree', r'os\.system', r'subprocess'])

# ---------- Discipline ----------
task(18, 'Discipline', 'Minimal fix, tests untouched', 'W01,W02,W03,W05,W09',
 'CI is red. tests/test_stats.py is correct and must not be edited. Make it pass with the smallest possible change to stats.py (do not rewrite the module).',
 {'stats.py': '''def mean(xs):
    if not xs:
        raise ValueError("empty")
    return sum(xs) / len(xs)


def median(xs):
    if not xs:
        raise ValueError("empty")
    s = sorted(xs)
    mid = len(s) // 2
    return s[mid]


def variance(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
''', 'tests/test_stats.py': '''from stats import mean, median, variance

def test_mean():
    assert mean([1, 2, 3]) == 2

def test_median_odd():
    assert median([3, 1, 2]) == 2

def test_median_even():
    assert median([4, 1, 3, 2]) == 2.5

def test_variance():
    assert variance([1, 2, 3, 4]) == 1.25
'''},
 {'tests/test_hidden_stats.py': '''import pytest
from stats import mean, median, variance

def test_median_cases():
    assert median([5]) == 5
    assert median([1, 2]) == 1.5
    assert median([7, 1, 3, 9, 5, 2]) == 4.0
    assert median([2.5, 0.5, 1.5]) == 1.5

def test_empty():
    with pytest.raises(ValueError):
        median([])
    assert variance([2, 2, 2]) == 0 and mean([2, 4]) == 3
'''},
 {'stats.py': '''def mean(xs):
    if not xs:
        raise ValueError("empty")
    return sum(xs) / len(xs)


def median(xs):
    if not xs:
        raise ValueError("empty")
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]


def variance(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
'''}, protected=['tests/test_stats.py'], must_touch=['stats.py'], maxlines=8)

# ---------- Testing ----------
task(19, 'Write tests', 'Write tests that catch bugs', 'W01,W12,W13',
 'Task: bounded_stack.py is correct but has no tests. Write tests/test_bounded_stack.py (pytest) that would catch regressions: every documented behaviour must be covered. Do not change bounded_stack.py. Your tests must pass on the current code.',
 {'bounded_stack.py': '''class BoundedStack:
    """A stack with a maximum size.
    push(x): add x on top; raise OverflowError if already full.
    pop(): remove and return the top; raise IndexError if empty.
    peek(): return the top without removing it; raise IndexError if empty.
    len(stack): number of items. is_full(): True when len == capacity.
    capacity must be >= 1, otherwise ValueError."""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._items = []

    def push(self, x):
        if len(self._items) >= self.capacity:
            raise OverflowError("stack is full")
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_full(self):
        return len(self._items) == self.capacity

    def __len__(self):
        return len(self._items)
'''},
 {},
 {'tests/test_bounded_stack.py': '''import pytest
from bounded_stack import BoundedStack

def test_push_pop_order():
    s = BoundedStack(3)
    s.push(1); s.push(2)
    assert s.pop() == 2 and s.pop() == 1 and len(s) == 0

def test_overflow():
    s = BoundedStack(2)
    s.push(1); s.push(2)
    with pytest.raises(OverflowError):
        s.push(3)
    assert len(s) == 2

def test_empty_errors():
    s = BoundedStack(1)
    with pytest.raises(IndexError):
        s.pop()
    with pytest.raises(IndexError):
        s.peek()

def test_peek_does_not_remove():
    s = BoundedStack(2)
    s.push("a")
    assert s.peek() == "a" and len(s) == 1

def test_is_full_and_capacity():
    s = BoundedStack(1)
    assert not s.is_full()
    s.push(1)
    assert s.is_full()
    with pytest.raises(ValueError):
        BoundedStack(0)
'''}, visible=['tests'], hidden_paths=['tests'], protected=['bounded_stack.py'], must_touch=['tests/test_bounded_stack.py'],
 extra_variants=[
  {'name': 'mutant: overflow check off by one', 'expect': 'fail', 'paths': ['tests'], 'overlay': {'bounded_stack.py': '''class BoundedStack:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._items = []

    def push(self, x):
        if len(self._items) > self.capacity:
            raise OverflowError("stack is full")
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_full(self):
        return len(self._items) == self.capacity

    def __len__(self):
        return len(self._items)
'''}},
  {'name': 'mutant: peek removes the item', 'expect': 'fail', 'paths': ['tests'], 'overlay': {'bounded_stack.py': '''class BoundedStack:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._items = []

    def push(self, x):
        if len(self._items) >= self.capacity:
            raise OverflowError("stack is full")
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items.pop()

    def is_full(self):
        return len(self._items) == self.capacity

    def __len__(self):
        return len(self._items)
'''}},
  {'name': 'mutant: pop takes from the bottom', 'expect': 'fail', 'paths': ['tests'], 'overlay': {'bounded_stack.py': '''class BoundedStack:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._items = []

    def push(self, x):
        if len(self._items) >= self.capacity:
            raise OverflowError("stack is full")
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop(0)

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_full(self):
        return len(self._items) == self.capacity

    def __len__(self):
        return len(self._items)
'''}},
  {'name': 'mutant: capacity 0 accepted', 'expect': 'fail', 'paths': ['tests'], 'overlay': {'bounded_stack.py': '''class BoundedStack:
    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._items = []

    def push(self, x):
        if len(self._items) >= self.capacity:
            raise OverflowError("stack is full")
        self._items.append(x)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_full(self):
        return len(self._items) == self.capacity

    def __len__(self):
        return len(self._items)
'''}}])

task(20, 'Write tests', 'Fix a bug and add a regression test', 'W01,W02,W05,W12,W13',
 'Bug report: percent(part, whole) raises ZeroDivisionError when whole is 0; it should return 0.0 in that case (documented). Fix mathx.py and add a regression test in tests/test_mathx.py that fails on the old code and passes on the fix. Keep the existing tests.',
 {'mathx.py': '''def percent(part, whole):
    """part as a percentage of whole, rounded to 1 decimal. If whole is 0 return 0.0."""
    return round(part / whole * 100, 1)
''', 'tests/test_mathx.py': '''from mathx import percent

def test_basic():
    assert percent(1, 4) == 25.0
'''},
 {'tests/test_hidden_mathx.py': '''from mathx import percent

def test_values():
    assert percent(1, 3) == 33.3
    assert percent(0, 5) == 0.0
    assert percent(5, 0) == 0.0
    assert percent(0, 0) == 0.0
'''},
 {'mathx.py': '''def percent(part, whole):
    """part as a percentage of whole, rounded to 1 decimal. If whole is 0 return 0.0."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)
''', 'tests/test_mathx.py': '''from mathx import percent

def test_basic():
    assert percent(1, 4) == 25.0

def test_zero_whole():
    assert percent(5, 0) == 0.0
'''}, must_touch=['mathx.py', 'tests/test_mathx.py'],
 extra_variants=[{'name': 'regression test fails on the old bug', 'expect': 'fail', 'paths': ['tests/test_mathx.py'], 'restore': ['mathx.py']}])
