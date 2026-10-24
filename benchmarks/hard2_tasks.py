import sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
T = []
def task(tid, name, issue, repo, hidden, ref):
    vis = [p for p in repo if p.startswith('tests/')]
    key = {'visible_paths': vis, 'protected': vis, 'forbidden': [], 'must_touch': [],
           'variants': [{'name': 'hidden tests', 'overlay': hidden, 'expect': 'pass', 'paths': ['tests']}]}
    T.append(dict(id=tid, group='Hard2', name=name, rules='', issue=issue, repo=repo, key=key, ref=ref))

# 201 money
task(201, 'Invoice totals off by a cent',
 'Bug report: invoice totals are sometimes one cent off, for example three items at 19.99 do not total 59.97, and percentage discounts and VAT seem to round the wrong way for some amounts. Find the cause and fix it. Do not change the tests.',
 {'money.py': '''def to_cents(x):
    """Convert a dollar amount (int, float or str such as "1.10") to integer cents. Round half away from zero at the
    cent: 0.285 -> 29, 2.675 -> 268, -1.005 -> -101. Never use binary float arithmetic for the conversion."""
    return int(x * 100)


def fmt(cents):
    """Format integer cents as dollars: 1999 -> "$19.99", 5 -> "$0.05", -150 -> "-$1.50", -5 -> "-$0.05"."""
    return "$%d.%02d" % (cents // 100, cents % 100)
''', 'invoice.py': '''from money import to_cents


def line_total(price, qty):
    """Cents for qty items at a dollar price."""
    return to_cents(price) * qty


def invoice_total(lines, discount_pct=0):
    """lines is a list of (price_in_dollars, qty). discount_pct (0-100, may be fractional) is taken off the subtotal;
    the discount amount is rounded half away from zero to a whole cent. Returns total cents."""
    sub = sum(line_total(p, q) for p, q in lines)
    return sub - int(sub * discount_pct / 100)
''', 'tax.py': '''def vat(cents, rate):
    """VAT in cents on `cents` at fractional `rate` (0.2 = 20%), rounded half away from zero to a whole cent."""
    return int(cents * rate)


def gross(cents, rate):
    """cents plus its VAT."""
    return cents + vat(cents, rate)
''', 'report.py': '''from invoice import invoice_total
from money import fmt
from tax import gross


def invoice_line(lines, discount_pct=0, vat_rate=0.0):
    net = invoice_total(lines, discount_pct)
    return "net %s gross %s" % (fmt(net), fmt(gross(net, vat_rate)))
''', 'tests/test_invoice.py': '''from invoice import invoice_total

def test_three_items():
    assert invoice_total([(19.99, 3)]) == 5997
'''},
 {'tests/test_hidden_money.py': '''import pytest
from money import to_cents, fmt
from invoice import invoice_total, line_total
from tax import vat, gross
from report import invoice_line

def test_to_cents():
    assert to_cents(19.99) == 1999 and to_cents(0.29) == 29 and to_cents(1.1) == 110 and to_cents(0) == 0
    assert to_cents(0.285) == 29 and to_cents(2.675) == 268 and to_cents(-1.005) == -101 and to_cents(-0.285) == -29
    assert to_cents("1.10") == 110 and to_cents("0.005") == 1 and to_cents(5) == 500

def test_fmt():
    assert fmt(1999) == "$19.99" and fmt(5) == "$0.05" and fmt(0) == "$0.00"
    assert fmt(-150) == "-$1.50" and fmt(-5) == "-$0.05" and fmt(-100) == "-$1.00" and fmt(123456) == "$1234.56"

def test_invoice():
    assert invoice_total([(19.99, 3)]) == 5997
    assert invoice_total([(19.99, 3)], 10) == 5397          # discount 599.7 -> 600
    assert invoice_total([(0.1, 3)]) == 30
    assert invoice_total([(10.00, 1)], 12.5) == 875         # 125.0 exactly
    assert invoice_total([(0.05, 1)], 50) == 2              # discount 2.5 -> 3
    assert invoice_total([]) == 0 and line_total(1.15, 3) == 345

def test_vat():
    assert vat(1999, 0.2) == 400 and vat(5, 0.1) == 1 and vat(4, 0.1) == 0 and vat(0, 0.5) == 0
    assert vat(-5, 0.1) == -1 and vat(15, 0.1) == 2 and vat(25, 0.1) == 3 and vat(1000, 0.07) == 70
    assert gross(1999, 0.2) == 2399

def test_report():
    assert invoice_line([(19.99, 3)], 10, 0.2) == "net $53.97 gross $64.76"
'''},
 {'money.py': '''from decimal import Decimal, ROUND_HALF_UP


def _round(d):
    return int(d.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def to_cents(x):
    return _round(Decimal(str(x)) * 100)


def fmt(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return "%s$%d.%02d" % (sign, c // 100, c % 100)
''', 'invoice.py': '''from decimal import Decimal
from money import to_cents, _round


def line_total(price, qty):
    return to_cents(price) * qty


def invoice_total(lines, discount_pct=0):
    sub = sum(line_total(p, q) for p, q in lines)
    return sub - _round(Decimal(sub) * Decimal(str(discount_pct)) / 100)
''', 'tax.py': '''from decimal import Decimal
from money import _round


def vat(cents, rate):
    return _round(Decimal(cents) * Decimal(str(rate)))


def gross(cents, rate):
    return cents + vat(cents, rate)
'''})

# 202 config merge
task(202, 'Config overrides lose sibling keys',
 'Bug report: when a user config overrides one nested setting, the other settings next to it disappear, and setting an environment override to "false" still turns the feature on. Find the cause and fix it. Do not change the tests.',
 {'confmerge.py': '''def deep_merge(base, override):
    """Return a NEW dict: base merged with override. Nested dicts merge recursively; any other value in override replaces
    the base value (lists are replaced, not concatenated). A value of None in override REMOVES that key from the result.
    Neither input is modified and the result shares no mutable containers with either input."""
    result = dict(base)
    result.update(override)
    return result
''', 'envparse.py': '''def parse_value(text):
    """Convert an environment string: "true"/"yes"/"on"/"1" (any case, surrounding spaces ignored) -> True,
    "false"/"no"/"off"/"0" -> False, a decimal integer like "42" or "-7" -> int, a decimal number like "2.5" -> float,
    "" or "null"/"none" (any case) -> None, anything else -> the stripped string unchanged. Note "1" and "0" are booleans."""
    return bool(text)
''', 'settings.py': '''from confmerge import deep_merge
from envparse import parse_value

DEFAULTS = {"db": {"host": "localhost", "port": 5432, "opts": {"ssl": False}}, "debug": False, "tags": ["a"]}


def load(user_cfg, env):
    """DEFAULTS < user_cfg < env. env keys look like APP__DB__PORT=5433 and map to the nested path ["db", "port"] (lower-cased,
    split on "__"); values go through parse_value."""
    cfg = deep_merge(DEFAULTS, user_cfg)
    over = {}
    for k, v in env.items():
        if not k.startswith("APP__"):
            continue
        path = k[5:].lower().split("__")
        cur = over
        for p in path[:-1]:
            cur = cur.setdefault(p, {})
        cur[path[-1]] = parse_value(v)
    return deep_merge(cfg, over)
''', 'tests/test_settings.py': '''from settings import load

def test_nested_override_keeps_siblings():
    cfg = load({"db": {"port": 1}}, {})
    assert cfg["db"]["host"] == "localhost" and cfg["db"]["port"] == 1
'''},
 {'tests/test_hidden_settings.py': '''import copy
import pytest
from confmerge import deep_merge
from envparse import parse_value
from settings import load, DEFAULTS

def test_deep_levels():
    base = {"a": {"b": {"c": 1, "d": 2}, "e": 3}, "f": 4}
    out = deep_merge(base, {"a": {"b": {"c": 9}}})
    assert out == {"a": {"b": {"c": 9, "d": 2}, "e": 3}, "f": 4}

def test_replace_not_concat_and_type_change():
    assert deep_merge({"l": [1, 2]}, {"l": [3]}) == {"l": [3]}
    assert deep_merge({"a": {"b": 1}}, {"a": 5}) == {"a": 5}
    assert deep_merge({"a": 5}, {"a": {"b": 1}}) == {"a": {"b": 1}}

def test_none_removes():
    assert deep_merge({"a": 1, "b": 2}, {"a": None}) == {"b": 2}
    assert deep_merge({"a": {"x": 1, "y": 2}}, {"a": {"x": None}}) == {"a": {"y": 2}}
    assert deep_merge({"a": 1}, {"zzz": None}) == {"a": 1}

def test_no_mutation_no_sharing():
    base = {"a": {"b": [1]}, "c": {"d": 1}}
    over = {"x": {"y": [2]}}
    b0, o0 = copy.deepcopy(base), copy.deepcopy(over)
    out = deep_merge(base, over)
    out["a"]["b"].append(99); out["x"]["y"].append(99); out["c"]["d"] = 5
    assert base == b0 and over == o0

def test_parse_value():
    for t in ("true", "TRUE", " Yes ", "on", "1"):
        assert parse_value(t) is True
    for t in ("false", "False", "no", " OFF", "0"):
        assert parse_value(t) is False
    assert parse_value("42") == 42 and type(parse_value("42")) is int
    assert parse_value("-7") == -7 and parse_value("2.5") == 2.5 and type(parse_value("2.5")) is float
    for t in ("", "  ", "null", "NONE", "None"):
        assert parse_value(t) is None
    assert parse_value("  hello ") == "hello" and parse_value("1.2.3") == "1.2.3" and parse_value("0x10") == "0x10"

def test_load():
    cfg = load({"db": {"port": 1}}, {"APP__DB__OPTS__SSL": "true", "APP__DEBUG": "false", "OTHER": "x", "APP__TAGS": "b"})
    assert cfg["db"] == {"host": "localhost", "port": 1, "opts": {"ssl": True}}
    assert cfg["debug"] is False and cfg["tags"] == "b"
    cfg2 = load({}, {"APP__DB__PORT": "5433", "APP__DB__HOST": "null"})
    assert cfg2["db"]["port"] == 5433 and "host" not in cfg2["db"]
    assert DEFAULTS["db"]["port"] == 5432 and DEFAULTS["db"]["opts"] == {"ssl": False}
    cfg2["db"]["opts"]["ssl"] = True
    assert DEFAULTS["db"]["opts"] == {"ssl": False}
'''},
 {'confmerge.py': '''import copy


def deep_merge(base, override):
    result = copy.deepcopy(base)
    for k, v in override.items():
        if v is None:
            result.pop(k, None)
        elif isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        elif isinstance(v, dict):
            result[k] = deep_merge({}, v)
        else:
            result[k] = copy.deepcopy(v)
    return result
''', 'envparse.py': '''import re


def parse_value(text):
    s = text.strip()
    low = s.lower()
    if low in ("true", "yes", "on", "1"):
        return True
    if low in ("false", "no", "off", "0"):
        return False
    if low in ("", "null", "none"):
        return None
    if re.fullmatch(r"-?\\d+", s):
        return int(s)
    if re.fullmatch(r"-?\\d+\\.\\d+", s):
        return float(s)
    return s
'''})

# 203 dates/schedule
task(203, 'Recurring events skip or repeat days',
 'Bug report: monthly recurring events on the 31st vanish in short months, weekly events drift an hour after the clocks change, and the "next occurrence" shown to users is sometimes the current one. Find the cause and fix it. Do not change the tests.',
 {'recur.py': '''from datetime import datetime, timedelta


def next_occurrence(start, rule, after):
    """start: naive datetime of the first occurrence. rule: "daily", "weekly" or "monthly". Return the first occurrence
    STRICTLY after `after` (a naive datetime), or start itself if start > after. Occurrences are start + n periods, n>=0.
    Weekly = same weekday and wall-clock time every 7 days. Monthly = same day-of-month and time each month; if the month
    is too short use that month's LAST day (31 Jan -> 28/29 Feb -> 31 Mar, always counted from the ORIGINAL start day, so
    the day returns to 31 in March). Raise ValueError for an unknown rule."""
    cur = start
    while cur <= after:
        if rule == "daily":
            cur += timedelta(days=1)
        elif rule == "weekly":
            cur += timedelta(days=7)
        elif rule == "monthly":
            cur = cur.replace(month=cur.month % 12 + 1)
        else:
            raise ValueError(rule)
    return cur
''', 'calendar_view.py': '''from recur import next_occurrence


def upcoming(start, rule, after, n):
    """The next n occurrences strictly after `after`, as a list."""
    out = []
    cur = after
    for _ in range(n):
        cur = next_occurrence(start, rule, cur)
        out.append(cur)
    return out
''', 'tests/test_recur.py': '''from datetime import datetime
from recur import next_occurrence

def test_monthly_31():
    assert next_occurrence(datetime(2024, 1, 31, 9), "monthly", datetime(2024, 1, 31, 9)) == datetime(2024, 2, 29, 9)
'''},
 {'tests/test_hidden_recur.py': '''from datetime import datetime as D
import pytest
from recur import next_occurrence as n
from calendar_view import upcoming

def test_monthly_clamp_and_return():
    s = D(2023, 1, 31, 9)
    assert n(s, "monthly", D(2023, 1, 31, 9)) == D(2023, 2, 28, 9)
    assert n(s, "monthly", D(2023, 2, 28, 9)) == D(2023, 3, 31, 9)
    assert n(s, "monthly", D(2023, 3, 31, 9)) == D(2023, 4, 30, 9)
    assert n(s, "monthly", D(2023, 11, 30, 9)) == D(2023, 12, 31, 9)
    assert n(s, "monthly", D(2023, 12, 31, 9)) == D(2024, 1, 31, 9)
    assert n(s, "monthly", D(2024, 1, 31, 9)) == D(2024, 2, 29, 9)

def test_strictly_after_and_before_start():
    s = D(2024, 5, 10, 8, 30)
    assert n(s, "daily", D(2024, 1, 1)) == s
    assert n(s, "daily", s) == D(2024, 5, 11, 8, 30)
    assert n(s, "daily", D(2024, 5, 10, 8, 29, 59)) == s
    assert n(s, "weekly", D(2024, 5, 16)) == D(2024, 5, 17, 8, 30)
    assert n(s, "weekly", D(2024, 5, 17, 8, 30)) == D(2024, 5, 24, 8, 30)

def test_year_rollover_and_unknown():
    assert n(D(2023, 12, 15, 1), "monthly", D(2023, 12, 15, 1)) == D(2024, 1, 15, 1)
    assert n(D(2023, 12, 31), "monthly", D(2024, 1, 31)) == D(2024, 2, 29)
    with pytest.raises(ValueError):
        n(D(2024, 1, 1), "yearly", D(2024, 1, 2))

def test_upcoming():
    s = D(2023, 1, 31, 9)
    assert upcoming(s, "monthly", D(2023, 1, 1), 4) == [D(2023, 1, 31, 9), D(2023, 2, 28, 9), D(2023, 3, 31, 9), D(2023, 4, 30, 9)]
    assert upcoming(D(2024, 3, 1), "daily", D(2024, 2, 28, 12), 3) == [D(2024, 3, 1), D(2024, 3, 2), D(2024, 3, 3)]
    assert upcoming(D(2024, 3, 1), "weekly", D(2024, 3, 8), 0) == []
'''},
 {'recur.py': '''import calendar
from datetime import datetime, timedelta


def _month_add(start, k):
    m = start.month - 1 + k
    y = start.year + m // 12
    m = m % 12 + 1
    d = min(start.day, calendar.monthrange(y, m)[1])
    return start.replace(year=y, month=m, day=d)


def next_occurrence(start, rule, after):
    if rule not in ("daily", "weekly", "monthly"):
        raise ValueError(rule)
    if start > after:
        return start
    if rule == "monthly":
        k = 1
        while True:
            c = _month_add(start, k)
            if c > after:
                return c
            k += 1
    step = 1 if rule == "daily" else 7
    periods = (after - start) // timedelta(days=step) + 1
    return start + timedelta(days=step * periods)
'''})

# 204 text wrapping/CSV
task(204, 'Exported CSV breaks on some customers',
 'Bug report: some rows in the CSV export end up split across several lines or shifted by a column, and re-importing the export gives different data than we exported (names with commas, quotes or line breaks, and values starting with = are the worst). Find the cause and fix it. Do not change the tests.',
 {'csvio.py': '''def write_row(fields):
    """Encode one record as a CSV line WITHOUT trailing newline. Fields are str/int/float/None. None -> empty field.
    A field is quoted (with double quotes, inner quotes doubled) iff it contains a comma, a double quote, CR or LF, or has
    leading/trailing spaces. Numbers use str(). Spreadsheet-injection guard: a str field starting with =, +, - or @
    (but a str that parses as a plain number such as "-5" is left alone) gets a leading apostrophe prepended BEFORE quoting."""
    return ",".join(str(f) for f in fields)


def read_rows(text):
    """Parse CSV text (rows separated by \\n or \\r\\n, quoted fields may contain commas, quotes (doubled) and newlines) into a
    list of lists of str. A trailing newline does not create an empty row. An empty field is "". Raise ValueError on an
    unterminated quote."""
    return [line.split(",") for line in text.splitlines()]
''', 'export.py': '''from csvio import write_row

HEADER = ["id", "name", "note", "amount"]


def export(customers):
    """customers: list of dicts with id, name, note, amount (note/amount may be None). Returns the CSV text, header first,
    every line ending in \\n."""
    lines = [write_row(HEADER)]
    for c in customers:
        lines.append(write_row([c["id"], c["name"], c.get("note"), c.get("amount")]))
    return "\\n".join(lines) + "\\n"
''', 'tests/test_export.py': '''from export import export

def test_comma_name():
    assert export([{"id": 1, "name": "Smith, J", "note": None, "amount": 2}]).splitlines()[1] == '1,"Smith, J",,2'
'''},
 {'tests/test_hidden_csv.py': '''import pytest
from csvio import write_row, read_rows
from export import export

def test_write():
    assert write_row(["a", "b"]) == "a,b"
    assert write_row(["a,b", 'say "hi"', None, 3, 2.5]) == '"a,b","say ""hi""",,3,2.5'
    assert write_row(["line1\\nline2", "cr\\rx"]) == '"line1\\nline2","cr\\rx"'
    assert write_row([" pad", "pad ", "ok"]) == '" pad","pad ",ok'
    assert write_row([""]) == "" and write_row([None, None]) == ","

def test_injection_guard():
    assert write_row(["=1+1"]) == "'=1+1"
    assert write_row(["+cmd", "@x", "-y"]) == "'+cmd,'@x,'-y"
    assert write_row(["-5", "+3.5", "-0.25"]) == "-5,+3.5,-0.25"
    assert write_row(["=a,b"]) == '"\\'=a,b"'
    assert write_row([-5, "a=b"]) == "-5,a=b"

def test_read():
    assert read_rows("a,b\\n1,2\\n") == [["a", "b"], ["1", "2"]]
    assert read_rows('"a,b","say ""hi"""\\r\\n"x\\ny",z') == [["a,b", 'say "hi"'], ["x\\ny", "z"]]
    assert read_rows("a,,c\\n,,\\n") == [["a", "", "c"], ["", "", ""]]
    assert read_rows("") == [] and read_rows("\\n") == [[""]]
    assert read_rows('""\\n') == [[""]]
    with pytest.raises(ValueError):
        read_rows('"abc')

def test_roundtrip():
    rows = [["a,b", 'q"q', "x\\ny", " sp ", ""], ["1", "2", "3", "4", "5"]]
    text = "\\n".join(write_row(r) for r in rows) + "\\n"
    assert read_rows(text) == rows

def test_export():
    cs = [{"id": 1, "name": "O'Neil, Pat", "note": 'He said "no"\\nthen left', "amount": 12.5},
          {"id": 2, "name": "=SUM(A1)", "note": None, "amount": None}]
    out = export(cs)
    assert out.endswith("\\n") and out.startswith("id,name,note,amount\\n")
    back = read_rows(out)
    assert back[1] == ["1", "O'Neil, Pat", 'He said "no"\\nthen left', "12.5"]
    assert back[2] == ["2", "'=SUM(A1)", "", ""]
    assert len(back) == 3
'''},
 {'csvio.py': '''import re

_NUM = re.compile(r"^[+-]?\\d+(\\.\\d+)?$")


def _enc(f):
    if f is None:
        return ""
    if isinstance(f, str):
        if f and f[0] in "=+-@" and not _NUM.match(f):
            f = "'" + f
        s = f
    else:
        s = str(f)
    if any(ch in s for ch in ',"\\r\\n') or s != s.strip(" "):
        return '"' + s.replace('"', '""') + '"'
    return s


def write_row(fields):
    return ",".join(_enc(f) for f in fields)


def read_rows(text):
    rows, row, field, i, n = [], [], [], 0, len(text)
    inq = False
    started = False
    while i < n:
        ch = text[i]
        if inq:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"'); i += 1
                else:
                    inq = False
            else:
                field.append(ch)
        elif ch == '"':
            inq = True; started = True
        elif ch == ",":
            row.append("".join(field)); field = []; started = True
        elif ch in "\\r\\n":
            if ch == "\\r" and i + 1 < n and text[i + 1] == "\\n":
                i += 1
            row.append("".join(field)); rows.append(row); row, field, started = [], [], False
        else:
            field.append(ch); started = True
        i += 1
    if inq:
        raise ValueError("unterminated quote")
    if started or field or row:
        row.append("".join(field)); rows.append(row)
    return rows
'''})

# 205 permissions
task(205, 'Users keep access after being removed',
 'Bug report: users removed from a group still reach the group documents, a "deny" on a folder is sometimes ignored for files inside it, and admins in nested groups are not recognised. Find the cause and fix it. Do not change the tests.',
 {'groups.py': '''class Groups:
    """Group membership. Groups may contain users and other groups (nesting). Cycles must not hang."""

    def __init__(self):
        self.members = {}

    def add(self, group, member):
        self.members.setdefault(group, set()).add(member)

    def remove(self, group, member):
        """Remove member from group; removing a non-member is a no-op. An emptied group still exists."""
        self.members.setdefault(group, set())

    def groups_of(self, user):
        """Set of all groups the user belongs to, directly or through nested groups."""
        return {g for g, m in self.members.items() if user in m}
''', 'acl.py': '''def allowed(groups, acl, user, path, action):
    """acl: list of (path_prefix, subject, action, effect) with effect "allow" or "deny"; subject is a user name or group
    name. A rule applies if its prefix is a path-segment prefix of path ("/a" covers "/a" and "/a/b" but NOT "/ab"; "/" covers
    everything), its action equals `action` or is "*", and its subject is the user or one of the user's groups (nested
    included). The MOST SPECIFIC (longest) matching prefix decides; at equal length deny beats allow. No match -> False."""
    best = None
    for prefix, subject, act, effect in acl:
        if not path.startswith(prefix):
            continue
        if act != action:
            continue
        if subject != user and subject not in groups.groups_of(user):
            continue
        if best is None or len(prefix) > best[0]:
            best = (len(prefix), effect)
    return best is not None and best[1] == "allow"
''', 'docs.py': '''from acl import allowed


def can_read(groups, acl, user, path):
    return allowed(groups, acl, user, path, "read")


def can_admin(groups, acl, user, path):
    return allowed(groups, acl, user, path, "admin")
''', 'tests/test_groups.py': '''from groups import Groups

def test_remove():
    g = Groups(); g.add("eng", "bob"); g.remove("eng", "bob")
    assert g.groups_of("bob") == set()
'''},
 {'tests/test_hidden_acl.py': '''from groups import Groups
from acl import allowed
from docs import can_read, can_admin

def mk():
    g = Groups()
    g.add("eng", "bob"); g.add("staff", "eng"); g.add("all", "staff"); g.add("all", "all")
    return g

def test_remove_and_nested():
    g = mk()
    assert g.groups_of("bob") == {"eng", "staff", "all"}
    g.remove("eng", "bob")
    assert g.groups_of("bob") == set()
    g.remove("eng", "ghost"); g.remove("nogroup", "x")
    assert g.groups_of("eng") == {"staff", "all"}
    g.add("eng", "bob"); g.remove("staff", "eng")
    assert g.groups_of("bob") == {"eng"}

def test_cycle():
    g = Groups(); g.add("a", "b"); g.add("b", "a"); g.add("a", "u")
    assert g.groups_of("u") == {"a", "b"}

def test_segment_prefix():
    g = mk()
    acl = [("/a", "bob", "read", "allow")]
    assert allowed(g, acl, "bob", "/a", "read") and allowed(g, acl, "bob", "/a/b", "read")
    assert not allowed(g, acl, "bob", "/ab", "read") and not allowed(g, acl, "bob", "/", "read")
    assert allowed(g, [("/", "bob", "read", "allow")], "bob", "/x/y", "read")
    assert allowed(g, [("/a/", "bob", "read", "allow")], "bob", "/a/b", "read") is True

def test_specific_wins_deny_ties():
    g = mk()
    acl = [("/", "all", "read", "allow"), ("/priv", "bob", "read", "deny"), ("/priv/pub", "staff", "read", "allow")]
    assert can_read(g, acl, "bob", "/x") and not can_read(g, acl, "bob", "/priv/a")
    assert can_read(g, acl, "bob", "/priv/pub/f") and not can_read(g, acl, "bob", "/priv/pubx")
    acl2 = [("/d", "bob", "read", "allow"), ("/d", "eng", "read", "deny")]
    assert not can_read(g, acl2, "bob", "/d/f")
    assert not can_read(g, list(reversed(acl2)), "bob", "/d/f")

def test_wildcard_and_nested_admin():
    g = mk()
    acl = [("/", "all", "*", "allow"), ("/s", "all", "admin", "deny")]
    assert can_admin(g, acl, "bob", "/x") and can_read(g, acl, "bob", "/s")
    assert not can_admin(g, acl, "bob", "/s/t")
    assert not can_read(g, acl, "stranger", "/x")
    assert not allowed(g, [], "bob", "/x", "read")
'''},
 {'groups.py': '''class Groups:
    def __init__(self):
        self.members = {}

    def add(self, group, member):
        self.members.setdefault(group, set()).add(member)

    def remove(self, group, member):
        self.members.setdefault(group, set()).discard(member)

    def groups_of(self, user):
        seen = set()
        frontier = [user]
        while frontier:
            x = frontier.pop()
            for g, m in self.members.items():
                if x in m and g not in seen:
                    seen.add(g)
                    frontier.append(g)
        return seen
''', 'acl.py': '''def _covers(prefix, path):
    if prefix == "/":
        return True
    p = prefix.rstrip("/")
    return path == p or path.startswith(p + "/")


def allowed(groups, acl, user, path, action):
    mine = groups.groups_of(user)
    best = None
    for prefix, subject, act, effect in acl:
        if not _covers(prefix, path):
            continue
        if act != action and act != "*":
            continue
        if subject != user and subject not in mine:
            continue
        key = (len(prefix.rstrip("/")), effect == "deny")
        if best is None or key > best:
            best = key
    return best is not None and not best[1]
'''})

# 206 rate/usage ledger
task(206, 'Usage reports disagree with the ledger',
 'Bug report: the monthly usage report does not match the sum of the ledger entries; entries made late on the last day of a month are counted in the next month, refunds make the totals go up, and a customer with no usage is missing from the report instead of showing zero. Find the cause and fix it. Do not change the tests.',
 {'ledger.py': '''from datetime import datetime


class Ledger:
    """Append-only usage ledger. Entries: (customer, timestamp (naive datetime), units (int, negative for refunds))."""

    def __init__(self):
        self.entries = []

    def record(self, customer, ts, units):
        """Record an entry. Reject (ValueError) a units value of 0, a non-int units (bools too), a non-datetime ts or an empty
        customer name."""
        self.entries.append((customer, ts, abs(units)))

    def customers(self):
        """Sorted list of every customer that ever had an entry."""
        return sorted({c for c, _, _ in self.entries})
''', 'period.py': '''from datetime import datetime


def month_bounds(year, month):
    """Return (start, end) with start = first instant of the month and end = first instant of the NEXT month; an entry
    belongs to the month iff start <= ts < end. month 1..12, otherwise ValueError."""
    start = datetime(year, month, 1)
    end = datetime(year, month + 1, 1)
    return start, end
''', 'usage_report.py': '''from period import month_bounds


def monthly_report(ledger, year, month, customers=None):
    """Dict customer -> net units for the month (refunds subtract). Includes every customer in `customers` (default:
    all customers in the ledger) with 0 when they have no entries that month."""
    start, end = month_bounds(year, month)
    out = {}
    for c, ts, u in ledger.entries:
        if start <= ts <= end:
            out[c] = out.get(c, 0) + u
    return out
''', 'tests/test_usage.py': '''from datetime import datetime
from ledger import Ledger
from usage_report import monthly_report

def test_refund():
    l = Ledger(); l.record("a", datetime(2024, 1, 5), 10); l.record("a", datetime(2024, 1, 6), -3)
    assert monthly_report(l, 2024, 1) == {"a": 7}
'''},
 {'tests/test_hidden_usage.py': '''from datetime import datetime as D
import pytest
from ledger import Ledger
from period import month_bounds
from usage_report import monthly_report

def test_bounds():
    assert month_bounds(2024, 2) == (D(2024, 2, 1), D(2024, 3, 1))
    assert month_bounds(2024, 12) == (D(2024, 12, 1), D(2025, 1, 1))
    for m in (0, 13, -1):
        with pytest.raises(ValueError):
            month_bounds(2024, m)

def test_record_validation():
    l = Ledger()
    for args in [("a", D(2024, 1, 1), 0), ("a", D(2024, 1, 1), 1.5), ("a", D(2024, 1, 1), True),
                 ("a", "2024-01-01", 1), ("", D(2024, 1, 1), 1), ("a", None, 1)]:
        with pytest.raises(ValueError):
            l.record(*args)
    assert l.entries == []
    l.record("a", D(2024, 1, 1), -4)
    assert l.entries == [("a", D(2024, 1, 1), -4)]

def test_report_edges():
    l = Ledger()
    l.record("a", D(2024, 1, 31, 23, 59, 59), 5)
    l.record("a", D(2024, 2, 1, 0, 0, 0), 7)
    l.record("a", D(2024, 1, 1, 0, 0, 0), 1)
    l.record("b", D(2024, 1, 15), 10); l.record("b", D(2024, 1, 16), -4)
    l.record("c", D(2023, 12, 31, 23, 59, 59), 9)
    assert monthly_report(l, 2024, 1) == {"a": 6, "b": 6, "c": 0}
    assert monthly_report(l, 2024, 2) == {"a": 7, "b": 0, "c": 0}
    assert monthly_report(l, 2023, 12) == {"a": 0, "b": 0, "c": 9}
    assert monthly_report(l, 2024, 1, customers=["b", "zed"]) == {"b": 6, "zed": 0}
    assert monthly_report(Ledger(), 2024, 1) == {}
    l2 = Ledger(); l2.record("q", D(2024, 12, 31, 23), 2)
    assert monthly_report(l2, 2024, 12) == {"q": 2}

def test_customers_sorted():
    l = Ledger(); l.record("b", D(2024, 1, 1), 1); l.record("a", D(2024, 1, 1), 1); l.record("b", D(2024, 1, 2), 1)
    assert l.customers() == ["a", "b"]
'''},
 {'ledger.py': '''from datetime import datetime


class Ledger:
    def __init__(self):
        self.entries = []

    def record(self, customer, ts, units):
        if not isinstance(customer, str) or not customer:
            raise ValueError("customer")
        if not isinstance(ts, datetime):
            raise ValueError("ts")
        if type(units) is not int or units == 0:
            raise ValueError("units")
        self.entries.append((customer, ts, units))

    def customers(self):
        return sorted({c for c, _, _ in self.entries})
''', 'period.py': '''from datetime import datetime


def month_bounds(year, month):
    if not (isinstance(month, int) and 1 <= month <= 12):
        raise ValueError("month")
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return start, end
''', 'usage_report.py': '''from period import month_bounds


def monthly_report(ledger, year, month, customers=None):
    start, end = month_bounds(year, month)
    names = ledger.customers() if customers is None else list(customers)
    out = {c: 0 for c in names}
    for c, ts, u in ledger.entries:
        if c in out and start <= ts < end:
            out[c] += u
    return out
'''})

# generator
GEN = r'''
import sys; sys.path.insert(0,'/tmp/claude-0/hard2')
import hard2_tasks as h
head = open('/tmp/claude-0/hard/tickets/h101.md').read().split('\n\n')[0]
import os; os.makedirs('/tmp/claude-0/hard2/tickets', exist_ok=True)
for t in h.T:
    body = head + '\n\n' + t['issue'] + '\n\nREPOSITORY FILES:\n' + ''.join('=== FILE: %s ===\n%s\n=== END ===\n' % (p, c.rstrip('\n')) for p, c in t['repo'].items())
    open('/tmp/claude-0/hard2/tickets/h%d.md' % t['id'], 'w').write(body)
print([t['id'] for t in h.T])
'''
# open('/tmp/claude-0/hard2/gen_tickets.py','w').write(GEN)
