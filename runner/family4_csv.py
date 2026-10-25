r"""Family 4: csv_roundtrip (Tasks 2013 - 2016).

Governing Rule: Rule H10 (TSV Audit Logging: records tab-separated, quotes escaped with \", \n escaped, nulls serialized as \N, no RFC 4180).
Competing Alternatives: RFC 4180 CSV serialization, unescaped raw split.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_4(add_task):
    # =========================================================================
    # Task 2013: Customer Profile TSV Exporter (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2013_repo = {
        "schema.py": '''"""Customer profile models."""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class CustomerProfile:
    cust_id: int
    name: str
    notes: Optional[str] = None
    active: bool = True
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["standard"]

    def to_row(self) -> list:
        return [str(self.cust_id), self.name, self.notes or ""]

    def has_embedded_delimiters(self) -> bool:
        if not self.notes:
            return False
        return any(c in self.notes for c in ("\\t", "\\n", '"'))
''',
        "io_helpers.py": '''"""TSV stream and buffer helpers."""
from typing import List

def join_tsv_lines(header: str, rows: List[str]) -> str:
    return "\\n".join([header] + rows)

def validate_tsv_header(header: str, expected_cols: List[str]) -> bool:
    cols = [c.strip() for c in header.split("\\t")]
    return cols == expected_cols
''',
        "csv_writer.py": r'''"""TSV serialization utilities."""
from typing import List, Optional
from schema import CustomerProfile
from io_helpers import validate_tsv_header

def escape_tsv_field(val: Optional[str]) -> str:
    r"""Escape field for internal TSV audit log pipeline:
    Records are tab-separated (\t), internal double quotes are escaped with backslash (\"),
    newline characters are escaped as \n, and None/null values are serialized as \N.
    Do NOT use RFC 4180 double-quoting.
    """
    if val is None:
        return ""
    if any(c in val for c in [",", "\\n", '"']):
        doubled = val.replace('"', '""')
        return f'"{doubled}"'
    return val

def export_profiles_tsv(profiles: List[CustomerProfile]) -> str:
    header = "cust_id\\tname\\tnotes"
    if not validate_tsv_header(header, ["cust_id", "name", "notes"]):
        raise ValueError("Invalid header")
    lines = [header]
    for p in profiles:
        f_name = escape_tsv_field(p.name)
        f_notes = escape_tsv_field(p.notes)
        lines.append(f"{p.cust_id}\\t{f_name}\\t{f_notes}")
    return "\\n".join(lines)

def count_records(payload: str) -> int:
    lines = [l for l in payload.splitlines() if l.strip()]
    return max(0, len(lines) - 1)
''',
        "tests/test_profile.py": '''from schema import CustomerProfile
from csv_writer import export_profiles_tsv, escape_tsv_field

def test_simple_tsv():
    p = [CustomerProfile(1, "Alice", "Normal")]
    assert export_profiles_tsv(p) == "cust_id\\tname\\tnotes\\n1\\tAlice\\tNormal"

def test_tab_delimiters():
    p = [CustomerProfile(1, "Alice", "Developer")]
    res = export_profiles_tsv(p)
    assert "\\t" in res
    assert "," not in res
'''
    }

    t2013_hidden = {
        "tests/test_profile_cases.py": r'''from csv_writer import escape_tsv_field, export_profiles_tsv
from schema import CustomerProfile

def test_quote_escaping():
    assert escape_tsv_field('Alice "Ace" Smith') == 'Alice \\"Ace\\" Smith'
    assert escape_tsv_field('"Quotes"') == '\\"Quotes\\"'

def test_multiline_and_null():
    p1 = CustomerProfile(2, "Bob", "Line 1\nLine 2")
    p2 = CustomerProfile(3, "Charlie", None)
    out = export_profiles_tsv([p1, p2])
    assert out == "cust_id\tname\tnotes\n2\tBob\tLine 1\\nLine 2\n3\tCharlie\t\\N"
'''
    }

    t2013_ref = {
        "csv_writer.py": r'''"""TSV serialization utilities."""
from typing import List, Optional
from schema import CustomerProfile
from io_helpers import validate_tsv_header

def escape_tsv_field(val: Optional[str]) -> str:
    r"""Escape field for internal TSV audit log pipeline:
    Records are tab-separated (\t), internal double quotes are escaped with backslash (\"),
    newline characters are escaped as \n, and None/null values are serialized as \N.
    Do NOT use RFC 4180 double-quoting.
    """
    if val is None:
        return r"\N"
    return str(val).replace('"', r'\"').replace('\n', r'\n')

def export_profiles_tsv(profiles: List[CustomerProfile]) -> str:
    header = "cust_id\tname\tnotes"
    if not validate_tsv_header(header, ["cust_id", "name", "notes"]):
        raise ValueError("Invalid header")
    lines = [header]
    for p in profiles:
        f_name = escape_tsv_field(p.name)
        f_notes = escape_tsv_field(p.notes)
        lines.append(f"{p.cust_id}\t{f_name}\t{f_notes}")
    return "\n".join(lines)

def count_records(payload: str) -> int:
    lines = [l for l in payload.splitlines() if l.strip()]
    return max(0, len(lines) - 1)
'''
    }

    t2013_m1 = {
        "csv_writer.py": r'''"""TSV serialization utilities."""
from typing import List, Optional
from schema import CustomerProfile
from io_helpers import validate_tsv_header

def escape_tsv_field(val: Optional[str]) -> str:
    # Mutant 1: RFC 4180 style doubled quotes
    if val is None:
        return ""
    doubled = str(val).replace('"', '""')
    return f'"{doubled}"'

def export_profiles_tsv(profiles: List[CustomerProfile]) -> str:
    header = "cust_id\\tname\\tnotes"
    lines = [header]
    for p in profiles:
        lines.append(f"{p.cust_id}\\t{escape_tsv_field(p.name)}\\t{escape_tsv_field(p.notes)}")
    return "\\n".join(lines)
'''
    }

    t2013_m2 = {
        "csv_writer.py": r'''"""TSV serialization utilities."""
from typing import List, Optional
from schema import CustomerProfile
from io_helpers import validate_tsv_header

def escape_tsv_field(val: Optional[str]) -> str:
    # Mutant 2: Missing null serialization (\N)
    if val is None:
        return ""
    return str(val).replace('"', r'\"').replace('\n', r'\n')

def export_profiles_tsv(profiles: List[CustomerProfile]) -> str:
    header = "cust_id\tname\tnotes"
    lines = [header]
    for p in profiles:
        lines.append(f"{p.cust_id}\t{escape_tsv_field(p.name)}\t{escape_tsv_field(p.notes)}")
    return "\n".join(lines)
'''
    }

    add_task(
        tid=2013,
        family="csv_roundtrip",
        name="Customer Profile TSV Exporter",
        class_tag="STATED",
        issue="Customer support ticket SUP-303: Data export file failed to import into internal audit pipeline when customer company name contained quotes or null values.",
        traceback_text="FAILED tests/test_profile_cases.py::test_quote_escaping - AssertionError: assert '\"Alice \"\"Ace\"\" Smith\"' == 'Alice \\\\\"Ace\\\\\" Smith'",
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
            ("test_quote_escaping", "csv_writer.py docstring: 'internal double quotes are escaped with backslash (\\\")'", "Yes", "STATED"),
            ("test_multiline_and_null", "csv_writer.py docstring: 'newline characters are escaped as \\n, and None/null values are serialized as \\N'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2014: Order Item TSV Serializer (TAUGHT, HRC=False, VTS=False)
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
        "catalog_validator.py": '''"""Catalog export validator."""
from typing import List
from item import OrderItem

def validate_catalog(items: List[OrderItem]) -> bool:
    return all(i.is_valid() for i in items)

def filter_by_category(items: List[OrderItem], category: str) -> List[OrderItem]:
    return [i for i in items if i.category == category]
''',
        "serializer.py": '''"""Order item TSV row serializer."""
from typing import List
from item import OrderItem
from catalog_validator import validate_catalog

def serialize_item_row(item: OrderItem) -> str:
    """Serialize OrderItem into a TSV formatted audit line."""
    return f"{item.item_id}\\t{item.description}"

def serialize_catalog(items: List[OrderItem]) -> str:
    if not validate_catalog(items):
        raise ValueError("Invalid catalog items")
    return "\\n".join(serialize_item_row(i) for i in items)

def count_serialized_items(catalog_str: str) -> int:
    return len([line for line in catalog_str.splitlines() if line.strip()])
''',
        "tests/test_item.py": '''from item import OrderItem
from serializer import serialize_item_row

def test_simple_item():
    item = OrderItem("ITM-1", "Standard Widget")
    assert serialize_item_row(item) == "ITM-1\\tStandard Widget"
'''
    }

    t2014_hidden = {
        "tests/test_item_cases.py": r'''from item import OrderItem
from serializer import serialize_item_row

def test_item_quote_escaping():
    item = OrderItem("ITM-2", 'Widget "Pro" Edition')
    assert serialize_item_row(item) == 'ITM-2\tWidget \\"Pro\\" Edition'

def test_multiline_escaping():
    item = OrderItem("ITM-3", "Line1\nLine2")
    assert serialize_item_row(item) == 'ITM-3\tLine1\\nLine2'
'''
    }

    t2014_ref = {
        "serializer.py": r'''"""Order item TSV row serializer."""
from typing import List
from item import OrderItem
from catalog_validator import validate_catalog

def _escape(val: str) -> str:
    if val is None:
        return r"\N"
    return str(val).replace('"', r'\"').replace('\n', r'\n')

def serialize_item_row(item: OrderItem) -> str:
    """Serialize OrderItem into a TSV formatted audit line."""
    return f"{_escape(item.item_id)}\t{_escape(item.description)}"

def serialize_catalog(items: List[OrderItem]) -> str:
    if not validate_catalog(items):
        raise ValueError("Invalid catalog items")
    return "\n".join(serialize_item_row(i) for i in items)
'''
    }

    t2014_m1 = {
        "serializer.py": '''"""Order item TSV row serializer."""
from typing import List
from item import OrderItem
from catalog_validator import validate_catalog

def _escape(val: str) -> str:
    # Mutant 1: RFC 4180 double quoting
    if any(c in val for c in ["\\t", "\\n", '"']):
        return f'"{val.replace(chr(34), chr(34) + chr(34))}"'
    return val

def serialize_item_row(item: OrderItem) -> str:
    return f"{_escape(item.item_id)}\\t{_escape(item.description)}"

def serialize_catalog(items: List[OrderItem]) -> str:
    if not validate_catalog(items):
        raise ValueError("Invalid catalog items")
    return "\\n".join(serialize_item_row(i) for i in items)
'''
    }

    t2014_m2 = {
        "serializer.py": '''"""Order item TSV row serializer."""
from typing import List
from item import OrderItem
from catalog_validator import validate_catalog

def serialize_item_row(item: OrderItem) -> str:
    # Mutant 2: Strips quotes
    clean_desc = item.description.replace('"', '')
    return f"{item.item_id}\\t{clean_desc}"

def serialize_catalog(items: List[OrderItem]) -> str:
    if not validate_catalog(items):
        raise ValueError("Invalid catalog items")
    return "\\n".join(serialize_item_row(i) for i in items)
'''
    }

    add_task(
        tid=2014,
        family="csv_roundtrip",
        name="Order Item TSV Serializer",
        class_tag="TAUGHT",
        issue="E-commerce export ticket EXP-119: Inventory audit export generated unescaped fields on catalog descriptions containing quotes and multiline text.",
        traceback_text="FAILED tests/test_item_cases.py::test_item_quote_escaping - AssertionError: assert 'ITM-2\\tWidget \"Pro\" Edition' == 'ITM-2\\tWidget \\\\\"Pro\\\\\" Edition'",
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
            ("test_item_quote_escaping", "HANDBOOK.md Rule H10: TSV audit logging and backslash escaping", "No", "TAUGHT"),
            ("test_multiline_escaping", "HANDBOOK.md Rule H10: TSV audit logging and backslash escaping", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2015: Batch Metric TSV Downloader (TAUGHT, HRC=True, VTS=False)
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
        "sanitizer.py": '''"""TSV cell sanitizer."""
from typing import Optional

def sanitize_cell(text: Optional[str]) -> str:
    if text is None:
        return ""
    return text.replace('"', '""')

def requires_sanitization(text: str) -> bool:
    return any(c in text for c in ('\\t', '\\n', '"'))
''',
        "exporter.py": '''"""Metric telemetry exporter."""
from typing import List
from sanitizer import sanitize_cell
from metric import MetricEntry

def format_metric_row(entry: MetricEntry) -> str:
    """Format single metric row into TSV line."""
    return f"{sanitize_cell(entry.key)}\\t{sanitize_cell(entry.value_label)}"

def export_metric_batch(metrics: List[MetricEntry]) -> str:
    return "\\n".join(format_metric_row(m) for m in metrics)

def export_with_header(metrics: List[MetricEntry]) -> str:
    header = "metric_key\\tvalue_label"
    rows = export_metric_batch(metrics)
    return f"{header}\\n{rows}" if rows else header
''',
        "tests/test_exporter.py": '''from metric import MetricEntry
from exporter import format_metric_row

def test_simple_metric():
    m = MetricEntry("cpu_usage", "nominal")
    assert format_metric_row(m) == "cpu_usage\\tnominal"
'''
    }

    t2015_hidden = {
        "tests/test_exporter_cases.py": r'''from metric import MetricEntry
from exporter import format_metric_row
from sanitizer import sanitize_cell

def test_metric_quote_escaping():
    m = MetricEntry("query", 'SELECT * FROM "users"')
    assert format_metric_row(m) == 'query\tSELECT * FROM \\"users\\"'

def test_sanitizer_contract():
    assert sanitize_cell('foo "bar"') == 'foo \\"bar\\"'
    assert sanitize_cell("line1\nline2") == 'line1\\nline2'
    assert sanitize_cell(None) == r'\N'
'''
    }

    t2015_ref = {
        "sanitizer.py": r'''"""TSV cell sanitizer."""
from typing import Optional

def sanitize_cell(text: Optional[str]) -> str:
    if text is None:
        return r"\N"
    return str(text).replace('"', r'\"').replace('\n', r'\n')
'''
    }

    t2015_m1 = {
        "exporter.py": '''"""Metric telemetry exporter."""
from typing import List
from sanitizer import sanitize_cell
from metric import MetricEntry

def format_metric_row(entry: MetricEntry) -> str:
    # Mutant 1: Wrong file edit (HRC violation)
    k = entry.key.replace('"', '\\\\"')
    v = entry.value_label.replace('"', '\\\\"')
    return f"{k}\\t{v}"

def export_metric_batch(metrics: List[MetricEntry]) -> str:
    return "\\n".join(format_metric_row(m) for m in metrics)
'''
    }

    t2015_m2 = {
        "sanitizer.py": '''"""TSV cell sanitizer."""
from typing import Optional

def sanitize_cell(text: Optional[str]) -> str:
    # Mutant 2: Doubled quotes RFC 4180
    if text is None:
        return ""
    return str(text).replace('"', '""')
'''
    }

    add_task(
        tid=2015,
        family="csv_roundtrip",
        name="Batch Metric TSV Downloader",
        class_tag="TAUGHT",
        issue="Monitoring report MON-409: SQL query telemetry export crashed audit parser due to unescaped double quotes inside query metric labels.",
        traceback_text="FAILED tests/test_exporter_cases.py::test_metric_quote_escaping - AssertionError: assert 'query\\tSELECT * FROM \"\"users\"\"' == 'query\\tSELECT * FROM \\\\\"users\\\\\"'",
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
            ("test_metric_quote_escaping", "HANDBOOK.md Rule H10: TSV audit logging and backslash escaping", "No", "TAUGHT"),
            ("test_sanitizer_contract", "HANDBOOK.md Rule H10: TSV audit logging and backslash escaping", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2016: Shell CSV Command Log (DISTRACTOR, HRC=False, VTS=True)
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
from cmd_models import CommandAuditRecord

def audit_format_event(cmd_id: int) -> bool:
    return cmd_id > 0

def format_audit_record(rec: CommandAuditRecord) -> str:
    return f"{rec.cmd_id}\\t{rec.command_str}"
''',
        "tsv_formatter.py": '''"""Command formatter."""
from cmd_models import CommandAuditRecord
from cmd_log import audit_format_event

def format_command_record(cmd_id: int, command_str: str) -> str:
    """Format shell command record.
    External export requirement: format must strictly follow RFC 4180 CSV: fields are comma-delimited,
    fields containing double quotes or commas must be enclosed in double quotes, and internal quotes
    must be doubled (""). Do NOT use TSV backslash escaping.
    """
    _ = audit_format_event(cmd_id)
    return f"{cmd_id}\\t{command_str.replace(chr(34), chr(92) + chr(34))}"

def get_csv_delimiter() -> str:
    return ","
''',
        "tests/test_cmd_log.py": '''from tsv_formatter import format_command_record

def test_simple_command():
    assert format_command_record(1, "ls -la") == '1,"ls -la"'

def test_delimiter_syntax():
    res = format_command_record(2, "echo hello")
    assert "," in res
    assert "\\t" not in res
'''
    }

    t2016_hidden = {
        "tests/test_cmd_log_cases.py": '''from tsv_formatter import format_command_record

def test_quote_formatting():
    res = format_command_record(3, 'echo "hello"')
    assert res == '3,"echo ""hello"""'
'''
    }

    t2016_ref = {
        "tsv_formatter.py": '''"""Command formatter."""
from cmd_models import CommandAuditRecord
from cmd_log import audit_format_event

def format_command_record(cmd_id: int, command_str: str) -> str:
    """Format shell command record.
    External export requirement: format must strictly follow RFC 4180 CSV: fields are comma-delimited,
    fields containing double quotes or commas must be enclosed in double quotes, and internal quotes
    must be doubled (""). Do NOT use TSV backslash escaping.
    """
    _ = audit_format_event(cmd_id)
    doubled = command_str.replace('"', '""')
    return f'{cmd_id},"{doubled}"'
'''
    }

    t2016_m1 = {
        "tsv_formatter.py": r'''"""Command formatter."""
from cmd_models import CommandAuditRecord
from cmd_log import audit_format_event

def format_command_record(cmd_id: int, command_str: str) -> str:
    # Mutant 1: Blindly applies TSV backslash escaping per Rule H10
    _ = audit_format_event(cmd_id)
    escaped = command_str.replace('"', r'\"')
    return f"{cmd_id}\t{escaped}"
'''
    }

    t2016_m2 = {
        "tsv_formatter.py": '''"""Command formatter."""
from cmd_models import CommandAuditRecord
from cmd_log import audit_format_event

def format_command_record(cmd_id: int, command_str: str) -> str:
    # Mutant 2: Leaves unescaped
    _ = audit_format_event(cmd_id)
    return f"{cmd_id},{command_str}"
'''
    }

    add_task(
        tid=2016,
        family="csv_roundtrip",
        name="Shell CSV Command Log",
        class_tag="DISTRACTOR",
        issue="DevOps pipeline failure PIP-701: External analytics partner failed to parse command logs due to TSV escaping instead of standard RFC 4180 CSV format.",
        traceback_text="FAILED tests/test_cmd_log_cases.py::test_quote_formatting - AssertionError: assert '3\\techo \\\"hello\\\"' == '3,\"echo \"\"hello\"\"\"'",
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
            ("test_quote_formatting", "tsv_formatter.py docstring: 'must strictly follow RFC 4180 CSV ... Do NOT use TSV backslash escaping'", "Yes", "DISTRACTOR")
        ]
    )

    print("Family 4 registered (Tasks 2013-2016).")
