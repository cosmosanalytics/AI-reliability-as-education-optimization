"""Family 4: csv_roundtrip (Tasks 2013 - 2016).

Governing Rule: Rule H10 (RFC 4180 CSV Serialization: double quotes escaped with \"\", fields with delimiters quoted).
Competing Alternatives: Backslash escaping \\", unquoted raw split.
Target: 40-120 non-test lines across 3-4 files.
"""

def register_family_4(add_task):
    # =========================================================================
    # Task 2013: Customer Profile CSV Exporter (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2013_repo = {
        "schema.py": '''"""Customer profile models."""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class CustomerProfile:
    cust_id: int
    name: str
    notes: str
    active: bool = True
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["standard"]

    def to_row(self) -> list:
        return [str(self.cust_id), self.name, self.notes]

    def has_embedded_delimiters(self) -> bool:
        return any(c in self.notes for c in (",", "\\n", '"'))
''',
        "csv_writer.py": '''"""CSV serialization utilities."""
from typing import List
from schema import CustomerProfile

def escape_csv_field(val: str) -> str:
    """Escape CSV field per RFC 4180:
    If field contains comma, newline, or double quote, wrap in double quotes and escape internal quotes by doubling ("").
    """
    if any(c in val for c in [",", "\\n", '"']):
        escaped = val.replace('"', '\\"')
        return f'"{escaped}"'
    return val

def export_profiles_csv(profiles: List[CustomerProfile]) -> str:
    lines = ["cust_id,name,notes"]
    for p in profiles:
        f_name = escape_csv_field(p.name)
        f_notes = escape_csv_field(p.notes)
        lines.append(f"{p.cust_id},{f_name},{f_notes}")
    return "\\n".join(lines)

def count_records(csv_payload: str) -> int:
    lines = [l for l in csv_payload.splitlines() if l.strip()]
    return max(0, len(lines) - 1)
''',
        "io_helpers.py": '''"""CSV stream and buffer helpers."""
from typing import List

def join_csv_lines(header: str, rows: List[str]) -> str:
    return "\\n".join([header] + rows)

def validate_csv_header(header: str, expected_cols: List[str]) -> bool:
    cols = [c.strip() for c in header.split(",")]
    return cols == expected_cols
''',
        "tests/test_profile.py": '''from schema import CustomerProfile
from csv_writer import export_profiles_csv, escape_csv_field

def test_simple_csv():
    p = [CustomerProfile(1, "Alice", "Normal")]
    assert export_profiles_csv(p) == "cust_id,name,notes\\n1,Alice,Normal"

def test_comma_escaping_visible():
    assert escape_csv_field("Hello, World") == '"Hello, World"'
'''
    }

    t2013_hidden = {
        "tests/test_profile_hidden.py": '''from csv_writer import escape_csv_field, export_profiles_csv
from schema import CustomerProfile

def test_rfc4180_quote_doubling():
    assert escape_csv_field('Alice "Ace" Smith') == '"Alice ""Ace"" Smith"'
    assert escape_csv_field('"Quotes"') == '"""Quotes"""'

def test_multiline_csv():
    p = [CustomerProfile(2, "Bob", "Line 1\\nLine 2")]
    out = export_profiles_csv(p)
    assert out == 'cust_id,name,notes\\n2,Bob,"Line 1\\nLine 2"'
'''
    }

    t2013_ref = {
        "csv_writer.py": '''"""CSV serialization utilities."""
from typing import List
from schema import CustomerProfile

def escape_csv_field(val: str) -> str:
    """Escape CSV field per RFC 4180:
    If field contains comma, newline, or double quote, wrap in double quotes and escape internal quotes by doubling ("").
    """
    if any(c in val for c in [",", "\\n", '"']):
        doubled = val.replace('"', '""')
        return f'"{doubled}"'
    return val

def export_profiles_csv(profiles: List[CustomerProfile]) -> str:
    lines = ["cust_id,name,notes"]
    for p in profiles:
        f_name = escape_csv_field(p.name)
        f_notes = escape_csv_field(p.notes)
        lines.append(f"{p.cust_id},{f_name},{f_notes}")
    return "\\n".join(lines)
'''
    }

    t2013_m1 = {
        "csv_writer.py": '''"""CSV serialization utilities."""
from typing import List
from schema import CustomerProfile

def escape_csv_field(val: str) -> str:
    if any(c in val for c in [",", "\\n", '"']):
        return f'"{val.replace(chr(34), chr(92) + chr(34))}"'
    return val

def export_profiles_csv(profiles: List[CustomerProfile]) -> str:
    lines = ["cust_id,name,notes"]
    for p in profiles:
        lines.append(f"{p.cust_id},{escape_csv_field(p.name)},{escape_csv_field(p.notes)}")
    return "\\n".join(lines)
'''
    }

    t2013_m2 = {
        "csv_writer.py": '''"""CSV serialization utilities."""
from typing import List
from schema import CustomerProfile

def escape_csv_field(val: str) -> str:
    return f'"{val}"'

def export_profiles_csv(profiles: List[CustomerProfile]) -> str:
    lines = ["cust_id,name,notes"]
    for p in profiles:
        lines.append(f"{p.cust_id},{escape_csv_field(p.name)},{escape_csv_field(p.notes)}")
    return "\\n".join(lines)
'''
    }

    add_task(
        tid=2013,
        family="csv_roundtrip",
        name="Customer Profile CSV Exporter",
        class_tag="STATED",
        issue="Customer support ticket SUP-303: Data export file failed to import into standard spreadsheet software when customer company name contained quotes.",
        traceback_text="FAILED tests/test_profile_hidden.py::test_rfc4180_quote_doubling - AssertionError: RFC 4180 parsing failure at csv_writer.py:12: embedded quote was backslash escaped instead of doubled",
        traceback_files=["csv_writer.py"],
        repo=t2013_repo,
        hidden=t2013_hidden,
        ref=t2013_ref,
        mutant1=t2013_m1,
        mutant2=t2013_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H10"],
        assertions=[
            ("test_rfc4180_quote_doubling", "csv_writer.py docstring: 'wrap in double quotes and escape internal quotes by doubling (\"\")'", "Yes", "STATED"),
            ("test_multiline_csv", "csv_writer.py docstring: 'If field contains comma, newline, or double quote'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2014: Order Item CSV Serializer (TAUGHT, HRC=False, VTS=False)
    # =========================================================================
    t2014_repo = {
        "item.py": '''"""Item definition for order exports."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class OrderItem:
    item_id: str
    description: str
    sku: str = "GENERIC"
    category: str = "general"

    def is_valid(self) -> bool:
        return bool(self.item_id and self.description)

    def summary(self) -> str:
        return f"{self.item_id} ({self.sku})"

    def formatted_label(self) -> str:
        return f"[{self.category.upper()}] {self.description}"
''',
        "serializer.py": '''"""Order item CSV row serializer."""
from typing import List
from item import OrderItem

def serialize_item_row(item: OrderItem) -> str:
    """Serialize OrderItem into a CSV formatted line."""
    return f"{item.item_id},{item.description}"

def serialize_catalog(items: List[OrderItem]) -> str:
    return "\\n".join(serialize_item_row(i) for i in items)

def count_serialized_items(catalog_str: str) -> int:
    return len([line for line in catalog_str.splitlines() if line.strip()])
''',
        "catalog_validator.py": '''"""Catalog export validator."""
from typing import List
from item import OrderItem

def validate_catalog(items: List[OrderItem]) -> bool:
    return all(i.is_valid() for i in items)

def filter_by_category(items: List[OrderItem], category: str) -> List[OrderItem]:
    return [i for i in items if i.category == category]
''',
        "tests/test_item.py": '''from item import OrderItem
from serializer import serialize_item_row

def test_simple_item():
    item = OrderItem("ITM-1", "Standard Widget")
    assert serialize_item_row(item) == "ITM-1,Standard Widget"
'''
    }

    t2014_hidden = {
        "tests/test_item_hidden.py": '''from item import OrderItem
from serializer import serialize_item_row

def test_rfc4180_embedded_quotes_taught():
    item = OrderItem("ITM-2", 'Widget "Pro" Edition')
    assert serialize_item_row(item) == 'ITM-2,"Widget ""Pro"" Edition"'

def test_comma_enclosure():
    item = OrderItem("ITM-3", "Gadget, Type A")
    assert serialize_item_row(item) == 'ITM-3,"Gadget, Type A"'
'''
    }

    t2014_ref = {
        "serializer.py": '''"""Order item CSV row serializer."""
from typing import List
from item import OrderItem

def _escape(val: str) -> str:
    if any(c in val for c in [",", "\\n", '"']):
        return f'"{val.replace(chr(34), chr(34) + chr(34))}"'
    return val

def serialize_item_row(item: OrderItem) -> str:
    """Serialize OrderItem into a CSV formatted line."""
    return f"{_escape(item.item_id)},{_escape(item.description)}"

def serialize_catalog(items: List[OrderItem]) -> str:
    return "\\n".join(serialize_item_row(i) for i in items)
'''
    }

    t2014_m1 = {
        "serializer.py": '''"""Order item CSV row serializer."""
from typing import List
from item import OrderItem

def _escape(val: str) -> str:
    if any(c in val for c in [",", "\\n", '"']):
        return f'"{val.replace(chr(34), chr(92) + chr(34))}"'
    return val

def serialize_item_row(item: OrderItem) -> str:
    return f"{_escape(item.item_id)},{_escape(item.description)}"

def serialize_catalog(items: List[OrderItem]) -> str:
    return "\\n".join(serialize_item_row(i) for i in items)
'''
    }

    t2014_m2 = {
        "serializer.py": '''"""Order item CSV row serializer."""
from typing import List
from item import OrderItem

def serialize_item_row(item: OrderItem) -> str:
    clean_desc = item.description.replace('"', '')
    return f"{item.item_id},{clean_desc}"

def serialize_catalog(items: List[OrderItem]) -> str:
    return "\\n".join(serialize_item_row(i) for i in items)
'''
    }

    add_task(
        tid=2014,
        family="csv_roundtrip",
        name="Order Item CSV Serializer",
        class_tag="TAUGHT",
        issue="E-commerce export ticket EXP-119: CSV inventory export generated unquoted fields on catalog descriptions containing commas and inch measurement quotes.",
        traceback_text="FAILED tests/test_item_hidden.py::test_rfc4180_embedded_quotes_taught - AssertionError: CSV formatting error at serializer.py:9: embedded quote not escaped via RFC 4180 standard",
        traceback_files=["serializer.py"],
        repo=t2014_repo,
        hidden=t2014_hidden,
        ref=t2014_ref,
        mutant1=t2014_m1,
        mutant2=t2014_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H10"],
        assertions=[
            ("test_rfc4180_embedded_quotes_taught", "HANDBOOK.md Rule H10: RFC 4180 CSV serialization", "No", "TAUGHT"),
            ("test_comma_enclosure", "HANDBOOK.md Rule H10: RFC 4180 CSV serialization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2015: Batch Metric CSV Downloader (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2015_repo = {
        "metric.py": '''"""Telemetry metric entry."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class MetricEntry:
    key: str
    value_label: str
    sample_rate: float = 1.0
    unit: str = "count"

    def is_high_volume(self) -> bool:
        return self.sample_rate > 0.5

    def to_metric_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "label": self.value_label,
            "rate": self.sample_rate,
            "unit": self.unit,
        }
''',
        "exporter.py": '''"""Metric telemetry exporter."""
from typing import List
from sanitizer import sanitize_cell
from metric import MetricEntry

def format_metric_row(entry: MetricEntry) -> str:
    """Format single metric row into CSV line."""
    return f"{sanitize_cell(entry.key)},{sanitize_cell(entry.value_label)}"

def export_metric_batch(metrics: List[MetricEntry]) -> str:
    return "\\n".join(format_metric_row(m) for m in metrics)

def export_with_header(metrics: List[MetricEntry]) -> str:
    header = "metric_key,value_label"
    rows = export_metric_batch(metrics)
    return f"{header}\\n{rows}" if rows else header
''',
        "sanitizer.py": '''"""CSV cell sanitizer."""
def sanitize_cell(text: str) -> str:
    return text.replace('"', '\\"')

def requires_sanitization(text: str) -> bool:
    return any(c in text for c in (',', '\\n', '"'))
''',
        "tests/test_exporter.py": '''from metric import MetricEntry
from exporter import format_metric_row

def test_simple_metric():
    m = MetricEntry("cpu_usage", "nominal")
    assert format_metric_row(m) == "cpu_usage,nominal"
'''
    }

    t2015_hidden = {
        "tests/test_exporter_hidden.py": '''from metric import MetricEntry
from exporter import format_metric_row
from sanitizer import sanitize_cell

def test_rfc4180_metric_quotes():
    m = MetricEntry("query", 'SELECT * FROM "users"')
    assert format_metric_row(m) == 'query,"SELECT * FROM ""users"""'

def test_sanitizer_direct():
    assert sanitize_cell('foo "bar"') == '"foo ""bar"""'
    assert sanitize_cell('a,b') == '"a,b"'
'''
    }

    t2015_ref = {
        "sanitizer.py": '''"""CSV cell sanitizer."""
def sanitize_cell(text: str) -> str:
    if any(c in text for c in [",", "\\n", '"']):
        return f'"{text.replace(chr(34), chr(34) + chr(34))}"'
    return text
'''
    }

    t2015_m1 = {
        "exporter.py": '''"""Metric telemetry exporter."""
from typing import List
from sanitizer import sanitize_cell
from metric import MetricEntry

def format_metric_row(entry: MetricEntry) -> str:
    k = f'"{entry.key.replace(chr(34), chr(34) + chr(34))}"' if any(c in entry.key for c in [',', '\\n', '"']) else entry.key
    v = f'"{entry.value_label.replace(chr(34), chr(34) + chr(34))}"' if any(c in entry.value_label for c in [',', '\\n', '"']) else entry.value_label
    return f"{k},{v}"

def export_metric_batch(metrics: List[MetricEntry]) -> str:
    return "\\n".join(format_metric_row(m) for m in metrics)
'''
    }

    t2015_m2 = {
        "sanitizer.py": '''"""CSV cell sanitizer."""
def sanitize_cell(text: str) -> str:
    if any(c in text for c in [",", "\\n", '"']):
        return f'"{text.replace(chr(34), chr(92) + chr(34))}"'
    return text
'''
    }

    add_task(
        tid=2015,
        family="csv_roundtrip",
        name="Batch Metric CSV Downloader",
        class_tag="TAUGHT",
        issue="Monitoring report MON-409: SQL query telemetry export crashed BI import parser due to unescaped double quotes inside query metric labels.",
        traceback_text="FAILED tests/test_exporter_hidden.py::test_rfc4180_metric_quotes - AssertionError: Sanitization failure at exporter.py:9: SQL metric quotes were backslash escaped instead of doubled",
        traceback_files=["exporter.py"],
        repo=t2015_repo,
        hidden=t2015_hidden,
        ref=t2015_ref,
        mutant1=t2015_m1,
        mutant2=t2015_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H10"],
        assertions=[
            ("test_rfc4180_metric_quotes", "HANDBOOK.md Rule H10: RFC 4180 CSV serialization", "No", "TAUGHT"),
            ("test_sanitizer_direct", "HANDBOOK.md Rule H10: RFC 4180 CSV serialization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2016: Shell TSV Command Log (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2016_repo = {
        "cmd_models.py": '''"""Shell command log data structures."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CommandAuditRecord:
    cmd_id: int
    command_str: str
    exit_code: int = 0
    host: str = "worker-01"

    def is_success(self) -> bool:
        return self.exit_code == 0

    def to_record(self) -> Dict[str, Any]:
        return {
            "id": self.cmd_id,
            "cmd": self.command_str,
            "rc": self.exit_code,
            "host": self.host,
        }
''',
        "cmd_log.py": '''"""Shell command log generator."""
from tsv_formatter import format_tsv_command
from cmd_models import CommandAuditRecord

def build_log_line(cmd_id: int, command_str: str) -> str:
    """Format shell command into pipe-delimited TSV record."""
    return format_tsv_command(cmd_id, command_str)

def format_audit_record(rec: CommandAuditRecord) -> str:
    return build_log_line(rec.cmd_id, rec.command_str)

def batch_format_audit(records: list) -> str:
    return "\\n".join(format_audit_record(r) for r in records)
''',
        "tsv_formatter.py": '''"""TSV command formatter."""
def format_tsv_command(cmd_id: int, command_str: str) -> str:
    """Format shell command record.
    Unix pipe format: fields must be tab-delimited and internal quotes must be backslash-escaped (\\")
    for Bash compatibility. Do NOT use RFC 4180 double-quoting.
    """
    return f"{cmd_id},{command_str}"

def get_tsv_delimiter() -> str:
    return "\\t"
''',
        "tests/test_cmd_log.py": '''from cmd_log import build_log_line

def test_simple_command():
    assert build_log_line(1, "ls -la") == "1\\tls -la"

def test_visible_tabs_sensitive():
    res = build_log_line(2, "echo hello")
    assert "\\t" in res
    assert "," not in res
'''
    }

    t2016_hidden = {
        "tests/test_cmd_log_hidden.py": '''from cmd_log import build_log_line

def test_bash_backslash_quoting_distractor():
    res = build_log_line(3, 'echo "hello"')
    assert res == '3\\techo \\"hello\\"'
'''
    }

    t2016_ref = {
        "tsv_formatter.py": '''"""TSV command formatter."""
def format_tsv_command(cmd_id: int, command_str: str) -> str:
    """Format shell command record.
    Unix pipe format: fields must be tab-delimited and internal quotes must be backslash-escaped (\\")
    for Bash compatibility. Do NOT use RFC 4180 double-quoting.
    """
    escaped = command_str.replace('"', '\\"')
    return f"{cmd_id}\\t{escaped}"
'''
    }

    t2016_m1 = {
        "tsv_formatter.py": '''"""TSV command formatter."""
def format_tsv_command(cmd_id: int, command_str: str) -> str:
    doubled = command_str.replace('"', '""')
    return f'{cmd_id}\\t"{doubled}"'
'''
    }

    t2016_m2 = {
        "tsv_formatter.py": '''"""TSV command formatter."""
def format_tsv_command(cmd_id: int, command_str: str) -> str:
    return f"{cmd_id},{command_str}"
'''
    }

    add_task(
        tid=2016,
        family="csv_roundtrip",
        name="Shell TSV Command Log",
        class_tag="DISTRACTOR",
        issue="DevOps pipeline failure PIP-701: Audit command log consumer failed to parse Bash execution records due to invalid delimiter syntax.",
        traceback_text="FAILED tests/test_cmd_log_hidden.py::test_bash_backslash_quoting_distractor - AssertionError: Bash pipe parsing failure at tsv_formatter.py:9: command log did not use required backslash quote escaping",
        traceback_files=["tsv_formatter.py"],
        repo=t2016_repo,
        hidden=t2016_hidden,
        ref=t2016_ref,
        mutant1=t2016_m1,
        mutant2=t2016_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H10"],
        assertions=[
            ("test_bash_backslash_quoting_distractor", "tsv_formatter.py docstring: 'fields must be tab-delimited and internal quotes must be backslash-escaped (\\\") ... Do NOT use RFC 4180'", "Yes", "DISTRACTOR")
        ]
    )

    print("Family 4 registered (Tasks 2013-2016).")
