"""Family 13: metric_percentiles (Tasks 2069 - 2076).

Governing Rule: Rule H14 (Metric Percentile Estimation via Nearest-Rank Method:
index k = ceil(P / 100 * N) - 1 on sorted arrays. Continuous linear interpolation is prohibited for SLA compliance metrics.)
Competing Alternatives: Continuous linear interpolation, floor/truncation, midpoint rounding.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_13(add_task):
    # =========================================================================
    # Task 2069: Gateway Latency Monitor (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2069_repo = {
        "metric_types.py": '''"""Data models for gateway latency telemetry."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class LatencyRecord:
    endpoint: str
    duration_ms: float

@dataclass
class MetricWindow:
    records: List[LatencyRecord]

    def raw_values(self) -> List[float]:
        return [r.duration_ms for r in self.records]

    def sample_count(self) -> int:
        return len(self.records)
''',
        "metric_summary.py": '''"""Telemetry summary formatter."""
from typing import List, Dict, Any

def format_metric_summary(count: int, percentile_val: float) -> Dict[str, Any]:
    return {"count": count, "percentile_val": percentile_val}
''',
        "latency_calc.py": '''"""Gateway request latency percentile calculation."""
import math
from typing import List, Dict, Any
from metric_types import MetricWindow, LatencyRecord
from metric_summary import format_metric_summary

def compute_percentile(window: MetricWindow, percentile: float) -> float:
    """Calculates metric percentile using nearest-rank method: index k = math.ceil(p / 100 * n) - 1 on sorted values.
    Do not use linear interpolation.
    """
    vals = window.raw_values()
    if not vals:
        raise ValueError("Empty metric window")
    s = sorted(vals)
    n = len(s)
    idx = (percentile / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    if low == high:
        return float(s[low])
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))

def summarize_window(window: MetricWindow, percentile: float) -> Dict[str, Any]:
    val = compute_percentile(window, percentile)
    return format_metric_summary(window.sample_count(), val)
''',
        "tests/test_latency.py": '''from metric_types import MetricWindow, LatencyRecord
from latency_calc import compute_percentile, summarize_window

def test_single_value():
    w = MetricWindow([LatencyRecord("/api", 25.0)])
    assert compute_percentile(w, 50.0) == 25.0
    res = summarize_window(w, 50.0)
    assert res["count"] == 1

def test_identical_values():
    w = MetricWindow([LatencyRecord("/api", 10.0), LatencyRecord("/api", 10.0)])
    assert compute_percentile(w, 90.0) == 10.0
'''
    }

    t2069_hidden = {
        "tests/test_latency_cases.py": '''from metric_types import MetricWindow, LatencyRecord
from latency_calc import compute_percentile

def test_case_1():
    records = [LatencyRecord("/api", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0]]
    w = MetricWindow(records)
    assert compute_percentile(w, 40.0) == 20.0
    assert compute_percentile(w, 50.0) == 30.0
    assert compute_percentile(w, 95.0) == 50.0

def test_case_2():
    records = [LatencyRecord("/api", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]]
    w = MetricWindow(records)
    assert compute_percentile(w, 50.0) == 40.0
    assert compute_percentile(w, 90.0) == 80.0
'''
    }

    t2069_ref = {
        "latency_calc.py": '''"""Gateway request latency percentile calculation."""
import math
from typing import List, Dict, Any
from metric_types import MetricWindow, LatencyRecord
from metric_summary import format_metric_summary

def compute_percentile(window: MetricWindow, percentile: float) -> float:
    """Calculates metric percentile using nearest-rank method: index k = math.ceil(p / 100 * n) - 1 on sorted values.
    Do not use linear interpolation.
    """
    vals = window.raw_values()
    if not vals:
        raise ValueError("Empty metric window")
    s = sorted(vals)
    n = len(s)
    rank = math.ceil((percentile / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])

def summarize_window(window: MetricWindow, percentile: float) -> Dict[str, Any]:
    val = compute_percentile(window, percentile)
    return format_metric_summary(window.sample_count(), val)
'''
    }

    t2069_m1 = {
        "latency_calc.py": '''"""Gateway request latency percentile calculation."""
import math
from typing import List, Dict, Any
from metric_types import MetricWindow, LatencyRecord
from metric_summary import format_metric_summary

def compute_percentile(window: MetricWindow, percentile: float) -> float:
    vals = window.raw_values()
    if not vals:
        raise ValueError("Empty metric window")
    s = sorted(vals)
    n = len(s)
    idx = (percentile / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))

def summarize_window(window: MetricWindow, percentile: float) -> Dict[str, Any]:
    val = compute_percentile(window, percentile)
    return format_metric_summary(window.sample_count(), val)
'''
    }

    t2069_m2 = {
        "latency_calc.py": '''"""Gateway request latency percentile calculation."""
import math
from typing import List, Dict, Any
from metric_types import MetricWindow, LatencyRecord
from metric_summary import format_metric_summary

def compute_percentile(window: MetricWindow, percentile: float) -> float:
    vals = window.raw_values()
    if not vals:
        raise ValueError("Empty metric window")
    s = sorted(vals)
    n = len(s)
    idx = int((percentile / 100.0) * n)
    k = max(0, min(n - 1, idx))
    return float(s[k])

def summarize_window(window: MetricWindow, percentile: float) -> Dict[str, Any]:
    val = compute_percentile(window, percentile)
    return format_metric_summary(window.sample_count(), val)
'''
    }

    add_task(
        tid=2069,
        family="metric_percentiles",
        name="Gateway Latency Monitor",
        class_tag="STATED",
        issue="Incident INC-7101: SLA reporting gateway latency percentile mismatch on production metrics.",
        traceback_text="FAILED tests/test_latency_cases.py::test_case_1 - AssertionError: assert 26.0 == 20.0",
        traceback_files=["latency_calc.py"],
        repo=t2069_repo,
        hidden=t2069_hidden,
        ref=t2069_ref,
        mutant1=t2069_m1,
        mutant2=t2069_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "latency_calc.py docstring: nearest-rank method", "Yes", "STATED"),
            ("test_case_2", "latency_calc.py docstring: nearest-rank method", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2070: Database Query Duration Monitor (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2070_repo = {
        "query_types.py": '''"""Query metrics data model."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class QueryMetric:
    sql: str
    duration_ms: float

@dataclass
class QueryBatch:
    items: List[QueryMetric]

    def durations(self) -> List[float]:
        return [q.duration_ms for q in self.items]

    def total_queries(self) -> int:
        return len(self.items)
''',
        "query_percentile.py": '''"""Percentile estimation engine for database telemetry."""
import math
from typing import List

def calculate_percentile(values: List[float], p: float) -> float:
    """Calculates percentile across sample values."""
    if not values:
        raise ValueError("Empty values")
    s = sorted(values)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))
''',
        "query_monitor.py": '''"""Query performance SLA monitor."""
from typing import List, Dict, Any
from query_types import QueryBatch, QueryMetric
import query_percentile

def evaluate_sla_breach(batch: QueryBatch, p: float, threshold_ms: float) -> bool:
    """Returns True if percentile duration exceeds threshold."""
    durations = batch.durations()
    p_val = query_percentile.calculate_percentile(durations, p)
    return p_val > threshold_ms

def get_batch_sla_status(batch: QueryBatch, p: float, threshold_ms: float) -> Dict[str, Any]:
    breached = evaluate_sla_breach(batch, p, threshold_ms)
    return {"total": batch.total_queries(), "breached": breached}
''',
        "tests/test_query_monitor.py": '''from query_types import QueryBatch, QueryMetric
from query_monitor import evaluate_sla_breach, get_batch_sla_status

def test_empty_breach():
    b = QueryBatch([QueryMetric("SELECT 1", 5.0)])
    assert not evaluate_sla_breach(b, 50.0, 10.0)
    status = get_batch_sla_status(b, 50.0, 10.0)
    assert status["total"] == 1

def test_over_threshold():
    b = QueryBatch([QueryMetric("SELECT 1", 50.0)])
    assert evaluate_sla_breach(b, 90.0, 20.0)
'''
    }

    t2070_hidden = {
        "tests/test_query_cases.py": '''from query_types import QueryBatch, QueryMetric
from query_percentile import calculate_percentile
from query_monitor import evaluate_sla_breach

def test_case_1():
    durations = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    val = calculate_percentile(durations, 50.0)
    assert val == 40.0

def test_case_2():
    batch = QueryBatch([QueryMetric("SELECT", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]])
    # 50th percentile nearest-rank is 40.0, threshold 42.0 => False
    assert not evaluate_sla_breach(batch, 50.0, 42.0)
    assert evaluate_sla_breach(batch, 90.0, 75.0)
'''
    }

    t2070_ref = {
        "query_percentile.py": '''"""Percentile estimation engine for database telemetry."""
import math
from typing import List

def calculate_percentile(values: List[float], p: float) -> float:
    """Calculates percentile across sample values."""
    if not values:
        raise ValueError("Empty values")
    s = sorted(values)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])
'''
    }

    t2070_m1 = {
        "query_monitor.py": '''"""Query performance SLA monitor."""
from typing import List, Dict, Any
from query_types import QueryBatch, QueryMetric
import query_percentile

def evaluate_sla_breach(batch: QueryBatch, p: float, threshold_ms: float) -> bool:
    durations = batch.durations()
    p_val = query_percentile.calculate_percentile(durations, p)
    return p_val >= threshold_ms

def get_batch_sla_status(batch: QueryBatch, p: float, threshold_ms: float) -> Dict[str, Any]:
    breached = evaluate_sla_breach(batch, p, threshold_ms)
    return {"total": batch.total_queries(), "breached": breached}
'''
    }

    t2070_m2 = {
        "query_percentile.py": '''"""Percentile estimation engine for database telemetry."""
import math
from typing import List

def calculate_percentile(values: List[float], p: float) -> float:
    if not values:
        raise ValueError("Empty values")
    s = sorted(values)
    n = len(s)
    k = (int(p) * n) // 100
    return float(s[max(0, min(n - 1, k))])
'''
    }

    add_task(
        tid=2070,
        family="metric_percentiles",
        name="Database Query Duration Monitor",
        class_tag="TAUGHT",
        issue="Incident INC-7102: Telemetry query latency SLA calculation anomaly in reporting pipeline.",
        traceback_text="FAILED tests/test_query_cases.py::test_case_1 - AssertionError: assert 45.0 == 40.0",
        traceback_files=["query_monitor.py"],
        repo=t2070_repo,
        hidden=t2070_hidden,
        ref=t2070_ref,
        mutant1=t2070_m1,
        mutant2=t2070_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2071: Microservice RPC Response Timer (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2071_repo = {
        "rpc_data.py": '''"""RPC metric types."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class RpcSample:
    service: str
    duration_ms: float

@dataclass
class RpcSeries:
    samples: List[RpcSample]

    def durations(self) -> List[float]:
        return [s.duration_ms for s in self.samples]

    def count(self) -> int:
        return len(self.samples)
''',
        "rpc_formatter.py": '''"""RPC metric output formatter."""
from typing import Dict, Any

def format_rpc_stat(service: str, count: int, percentile_ms: float) -> Dict[str, Any]:
    return {"service": service, "count": count, "percentile_ms": percentile_ms}
''',
        "rpc_calc.py": '''"""Microservice RPC duration percentile calculator."""
import math
from typing import List, Dict, Any
from rpc_data import RpcSeries, RpcSample
from rpc_formatter import format_rpc_stat

def compute_rpc_percentile(series: RpcSeries, p: float) -> float:
    """Calculates SLA percentile for RPC responses."""
    vals = series.durations()
    if not vals:
        raise ValueError("No RPC samples available")
    s = sorted(vals)
    n = len(s)
    idx = int(round((p / 100.0) * (n - 1)))
    return float(s[idx])

def build_rpc_report(service_name: str, series: RpcSeries, p: float) -> Dict[str, Any]:
    val = compute_rpc_percentile(series, p)
    return format_rpc_stat(service_name, series.count(), val)
''',
        "tests/test_rpc.py": '''from rpc_data import RpcSeries, RpcSample
from rpc_calc import compute_rpc_percentile, build_rpc_report

def test_single_rpc():
    s = RpcSeries([RpcSample("auth", 15.0)])
    assert compute_rpc_percentile(s, 90.0) == 15.0
    rep = build_rpc_report("auth", s, 90.0)
    assert rep["count"] == 1

def test_equal_rpc():
    s = RpcSeries([RpcSample("auth", 20.0), RpcSample("auth", 20.0)])
    assert compute_rpc_percentile(s, 50.0) == 20.0
'''
    }

    t2071_hidden = {
        "tests/test_rpc_cases.py": '''from rpc_data import RpcSeries, RpcSample
from rpc_calc import compute_rpc_percentile

def test_case_1():
    samples = [RpcSample("billing", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]]
    series = RpcSeries(samples)
    # n=10, p=30: rank = ceil(0.30 * 10) = 3 -> k=2 -> 30.0
    assert compute_rpc_percentile(series, 30.0) == 30.0

def test_case_2():
    samples = [RpcSample("billing", v) for v in [12.0, 15.0, 20.0, 24.0, 30.0, 36.0, 40.0, 50.0]]
    series = RpcSeries(samples)
    # n=8, p=25: rank = ceil(0.25 * 8) = 2 -> k=1 -> 15.0
    assert compute_rpc_percentile(series, 25.0) == 15.0
    # n=8, p=75: rank = ceil(0.75 * 8) = 6 -> k=5 -> 36.0
    assert compute_rpc_percentile(series, 75.0) == 36.0
'''
    }

    t2071_ref = {
        "rpc_calc.py": '''"""Microservice RPC duration percentile calculator."""
import math
from typing import List, Dict, Any
from rpc_data import RpcSeries, RpcSample
from rpc_formatter import format_rpc_stat

def compute_rpc_percentile(series: RpcSeries, p: float) -> float:
    """Calculates SLA percentile for RPC responses."""
    vals = series.durations()
    if not vals:
        raise ValueError("No RPC samples available")
    s = sorted(vals)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])

def build_rpc_report(service_name: str, series: RpcSeries, p: float) -> Dict[str, Any]:
    val = compute_rpc_percentile(series, p)
    return format_rpc_stat(service_name, series.count(), val)
'''
    }

    t2071_m1 = {
        "rpc_calc.py": '''"""Microservice RPC duration percentile calculator."""
import math
from typing import List, Dict, Any
from rpc_data import RpcSeries, RpcSample
from rpc_formatter import format_rpc_stat

def compute_rpc_percentile(series: RpcSeries, p: float) -> float:
    vals = series.durations()
    if not vals:
        raise ValueError("No RPC samples available")
    s = sorted(vals)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))

def build_rpc_report(service_name: str, series: RpcSeries, p: float) -> Dict[str, Any]:
    val = compute_rpc_percentile(series, p)
    return format_rpc_stat(service_name, series.count(), val)
'''
    }

    t2071_m2 = {
        "rpc_calc.py": '''"""Microservice RPC duration percentile calculator."""
import math
from typing import List, Dict, Any
from rpc_data import RpcSeries, RpcSample
from rpc_formatter import format_rpc_stat

def compute_rpc_percentile(series: RpcSeries, p: float) -> float:
    vals = series.durations()
    if not vals:
        raise ValueError("No RPC samples available")
    s = sorted(vals)
    n = len(s)
    k = math.floor((p / 100.0) * n)
    return float(s[max(0, min(n - 1, k))])

def build_rpc_report(service_name: str, series: RpcSeries, p: float) -> Dict[str, Any]:
    val = compute_rpc_percentile(series, p)
    return format_rpc_stat(service_name, series.count(), val)
'''
    }

    add_task(
        tid=2071,
        family="metric_percentiles",
        name="Microservice RPC Response Timer",
        class_tag="TAUGHT",
        issue="Incident INC-7103: Microservice telemetry collector reports inconsistent RPC duration percentiles.",
        traceback_text="FAILED tests/test_rpc_cases.py::test_case_1 - AssertionError: assert 20.0 == 30.0",
        traceback_files=["rpc_calc.py"],
        repo=t2071_repo,
        hidden=t2071_hidden,
        ref=t2071_ref,
        mutant1=t2071_m1,
        mutant2=t2071_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H14: Nearest-rank metric percentile estimation", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H14: Nearest-rank metric percentile estimation", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2072: Audio Stream Buffer Telemetry (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2072_repo = {
        "audio_types.py": '''"""Audio telemetry models."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class BufferSample:
    channel_id: str
    fill_ratio: float

@dataclass
class AudioStreamSnapshot:
    samples: List[BufferSample]

    def ratios(self) -> List[float]:
        return [s.fill_ratio for s in self.samples]

    def channel_count(self) -> int:
        return len(self.samples)
''',
        "audio_formatter.py": '''"""Audio telemetry reporter formatter."""
from typing import Dict, Any

def format_buffer_stat(channels: int, percentile_val: float) -> Dict[str, Any]:
    return {"channels": channels, "percentile_val": percentile_val}
''',
        "audio_metrics.py": '''"""Audio buffer level metric processor."""
import math
from typing import List, Dict, Any
from audio_types import AudioStreamSnapshot, BufferSample
from audio_formatter import format_buffer_stat

def compute_buffer_percentile(snapshot: AudioStreamSnapshot, p: float) -> float:
    """Compute percentile using continuous linear interpolation (numpy-style: index = (p / 100.0) * (len(samples) - 1)).
    Do not use nearest-rank method for audio buffer metrics.
    """
    vals = snapshot.ratios()
    if not vals:
        raise ValueError("Empty snapshot")
    s = sorted(vals)
    n = len(s)
    # Nearest rank erroneously used here
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])

def evaluate_audio_buffer(snapshot: AudioStreamSnapshot, p: float) -> Dict[str, Any]:
    val = compute_buffer_percentile(snapshot, p)
    return format_buffer_stat(snapshot.channel_count(), val)
''',
        "tests/test_audio.py": '''from audio_types import AudioStreamSnapshot, BufferSample
from audio_metrics import compute_buffer_percentile, evaluate_audio_buffer

def test_single_sample():
    s = AudioStreamSnapshot([BufferSample("c1", 0.5)])
    assert compute_buffer_percentile(s, 50.0) == 0.5
    res = evaluate_audio_buffer(s, 50.0)
    assert res["channels"] == 1

def test_identical_samples():
    s = AudioStreamSnapshot([BufferSample("c1", 0.4), BufferSample("c2", 0.4)])
    assert compute_buffer_percentile(s, 90.0) == 0.4
'''
    }

    t2072_hidden = {
        "tests/test_buffer_cases.py": '''from audio_types import AudioStreamSnapshot, BufferSample
from audio_metrics import compute_buffer_percentile

def test_case_1():
    samples = [BufferSample("ch", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0]]
    snap = AudioStreamSnapshot(samples)
    # Linear interpolation: n=5, p=40: idx = 0.40 * 4 = 1.6 -> 20.0 + 0.6 * 10 = 26.0
    assert compute_buffer_percentile(snap, 40.0) == 26.0

def test_case_2():
    samples = [BufferSample("ch", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0]]
    snap = AudioStreamSnapshot(samples)
    # Linear interpolation: n=5, p=75: idx = 0.75 * 4 = 3.0 -> 40.0
    assert compute_buffer_percentile(snap, 75.0) == 40.0
'''
    }

    t2072_ref = {
        "audio_metrics.py": '''"""Audio buffer level metric processor."""
import math
from typing import List, Dict, Any
from audio_types import AudioStreamSnapshot, BufferSample
from audio_formatter import format_buffer_stat

def compute_buffer_percentile(snapshot: AudioStreamSnapshot, p: float) -> float:
    """Compute percentile using continuous linear interpolation (numpy-style: index = (p / 100.0) * (len(samples) - 1)).
    Do not use nearest-rank method for audio buffer metrics.
    """
    vals = snapshot.ratios()
    if not vals:
        raise ValueError("Empty snapshot")
    s = sorted(vals)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    if low == high:
        return float(s[low])
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))

def evaluate_audio_buffer(snapshot: AudioStreamSnapshot, p: float) -> Dict[str, Any]:
    val = compute_buffer_percentile(snapshot, p)
    return format_buffer_stat(snapshot.channel_count(), val)
'''
    }

    t2072_m1 = {
        "audio_metrics.py": '''"""Audio buffer level metric processor."""
import math
from typing import List, Dict, Any
from audio_types import AudioStreamSnapshot, BufferSample
from audio_formatter import format_buffer_stat

def compute_buffer_percentile(snapshot: AudioStreamSnapshot, p: float) -> float:
    vals = snapshot.ratios()
    if not vals:
        raise ValueError("Empty snapshot")
    s = sorted(vals)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])

def evaluate_audio_buffer(snapshot: AudioStreamSnapshot, p: float) -> Dict[str, Any]:
    val = compute_buffer_percentile(snapshot, p)
    return format_buffer_stat(snapshot.channel_count(), val)
'''
    }

    t2072_m2 = {
        "audio_metrics.py": '''"""Audio buffer level metric processor."""
import math
from typing import List, Dict, Any
from audio_types import AudioStreamSnapshot, BufferSample
from audio_formatter import format_buffer_stat

def compute_buffer_percentile(snapshot: AudioStreamSnapshot, p: float) -> float:
    vals = snapshot.ratios()
    if not vals:
        raise ValueError("Empty snapshot")
    s = sorted(vals)
    n = len(s)
    k = int((p / 100.0) * n)
    return float(s[max(0, min(n - 1, k))])

def evaluate_audio_buffer(snapshot: AudioStreamSnapshot, p: float) -> Dict[str, Any]:
    val = compute_buffer_percentile(snapshot, p)
    return format_buffer_stat(snapshot.channel_count(), val)
'''
    }

    add_task(
        tid=2072,
        family="metric_percentiles",
        name="Audio Stream Buffer Telemetry",
        class_tag="DISTRACTOR",
        issue="Incident INC-7104: Media server audio buffer occupancy telemetry reports non-continuous quantile steps.",
        traceback_text="FAILED tests/test_buffer_cases.py::test_case_1 - AssertionError: assert 20.0 == 26.0",
        traceback_files=["audio_metrics.py"],
        repo=t2072_repo,
        hidden=t2072_hidden,
        ref=t2072_ref,
        mutant1=t2072_m1,
        mutant2=t2072_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "audio_metrics.py docstring: Continuous linear interpolation", "Yes", "DISTRACTOR"),
            ("test_case_2", "audio_metrics.py docstring: Continuous linear interpolation", "Yes", "DISTRACTOR")
        ]
    )

    # =========================================================================
    # Task 2073: Cache Lookup Latency Reporter (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2073_repo = {
        "cache_types.py": '''"""Cache latency monitoring types."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CacheSample:
    cache_name: str
    latency_us: float

@dataclass
class CacheReport:
    samples: List[CacheSample]

    def latencies(self) -> List[float]:
        return [s.latency_us for s in self.samples]

    def record_count(self) -> int:
        return len(self.samples)
''',
        "cache_percentile.py": '''"""Cache lookup quantile engine."""
import math
from typing import List

def get_quantile(latencies: List[float], q: float) -> float:
    """Calculates latency quantile for cache cluster."""
    if not latencies:
        raise ValueError("No latency records")
    s = sorted(latencies)
    n = len(s)
    idx = (q / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))
''',
        "cache_reporter.py": '''"""Cache latency SLA evaluation reporter."""
from typing import List, Dict, Any
from cache_types import CacheReport, CacheSample
import cache_percentile

def check_cache_sla(report: CacheReport, percentile: float, max_us: float) -> Dict[str, float]:
    """Evaluates percentile latency and returns status."""
    lats = report.latencies()
    val = cache_percentile.get_quantile(lats, percentile)
    return {"percentile_us": val, "compliant": float(val <= max_us)}

def summarize_cache_metrics(report: CacheReport, percentile: float) -> Dict[str, Any]:
    lats = report.latencies()
    val = cache_percentile.get_quantile(lats, percentile)
    return {"records": report.record_count(), "quantile_us": val}
''',
        "tests/test_cache_reporter.py": '''from cache_types import CacheReport, CacheSample
from cache_reporter import check_cache_sla, summarize_cache_metrics

def test_compliant_sample():
    r = CacheReport([CacheSample("redis-1", 10.0)])
    res = check_cache_sla(r, 50.0, 20.0)
    assert res["compliant"] == 1.0
    summary = summarize_cache_metrics(r, 50.0)
    assert summary["records"] == 1
'''
    }

    t2073_hidden = {
        "tests/test_cache_cases.py": '''from cache_types import CacheReport, CacheSample
from cache_percentile import get_quantile
from cache_reporter import check_cache_sla

def test_case_1():
    # n=8, q=50: rank = ceil(0.50 * 8) = 4 -> k=3 -> 40.0
    lats = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    assert get_quantile(lats, 50.0) == 40.0

def test_case_2():
    samples = [CacheSample("r", v) for v in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]]
    rep = CacheReport(samples)
    res = check_cache_sla(rep, 50.0, 45.0)
    assert res["percentile_us"] == 40.0
    assert res["compliant"] == 1.0
'''
    }

    t2073_ref = {
        "cache_percentile.py": '''"""Cache lookup quantile engine."""
import math
from typing import List

def get_quantile(latencies: List[float], q: float) -> float:
    """Calculates latency quantile for cache cluster."""
    if not latencies:
        raise ValueError("No latency records")
    s = sorted(latencies)
    n = len(s)
    rank = math.ceil((q / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])
'''
    }

    t2073_m1 = {
        "cache_reporter.py": '''"""Cache latency SLA evaluation reporter."""
from typing import List, Dict, Any
from cache_types import CacheReport, CacheSample
import cache_percentile

def check_cache_sla(report: CacheReport, percentile: float, max_us: float) -> Dict[str, float]:
    lats = report.latencies()
    val = cache_percentile.get_quantile(lats, percentile)
    return {"percentile_us": float(round(val)), "compliant": float(val <= max_us)}

def summarize_cache_metrics(report: CacheReport, percentile: float) -> Dict[str, Any]:
    lats = report.latencies()
    val = cache_percentile.get_quantile(lats, percentile)
    return {"records": report.record_count(), "quantile_us": float(round(val))}
'''
    }

    t2073_m2 = {
        "cache_percentile.py": '''"""Cache lookup quantile engine."""
import math
from typing import List

def get_quantile(latencies: List[float], q: float) -> float:
    if not latencies:
        raise ValueError("No latency records")
    s = sorted(latencies)
    n = len(s)
    k = int((q / 100.0) * n)
    return float(s[max(0, min(n - 1, k))])
'''
    }

    add_task(
        tid=2073,
        family="metric_percentiles",
        name="Cache Lookup Latency Reporter",
        class_tag="TAUGHT",
        issue="Incident INC-7105: Cache cluster SLA audit reports disagreement on latency percentiles.",
        traceback_text="FAILED tests/test_cache_cases.py::test_case_1 - AssertionError: assert 45.0 == 40.0",
        traceback_files=["cache_reporter.py"],
        repo=t2073_repo,
        hidden=t2073_hidden,
        ref=t2073_ref,
        mutant1=t2073_m1,
        mutant2=t2073_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2074: Network Packet Jitter Evaluator (STATED, HRC=True, VTS=False)
    # =========================================================================
    t2074_repo = {
        "jitter_types.py": '''"""Packet jitter data structures."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class JitterSample:
    flow_id: str
    jitter_ms: float

@dataclass
class JitterStream:
    items: List[JitterSample]

    def raw_jitters(self) -> List[float]:
        return [j.jitter_ms for j in self.items]

    def sample_count(self) -> int:
        return len(self.items)
''',
        "jitter_core.py": '''"""Low-level jitter percentile calculation engine."""
import math
from typing import List

def evaluate_jitter_percentile(values: List[float], p: float) -> float:
    """Calculates percentile values across observed samples."""
    if not values:
        raise ValueError("No jitter values")
    s = sorted(values)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))
''',
        "jitter_evaluator.py": '''"""Network jitter SLA evaluation service."""
from typing import List, Dict, Any
from jitter_types import JitterStream, JitterSample
import jitter_core

def check_jitter_sla(stream: JitterStream, p: float, max_jitter: float) -> bool:
    """SLA compliance requires nearest-rank percentile estimation: index k = math.ceil(p / 100 * n) - 1 on sorted values.
    Returns True if compliance limit is respected.
    """
    vals = stream.raw_jitters()
    percentile_val = jitter_core.evaluate_jitter_percentile(vals, p)
    return percentile_val <= max_jitter

def get_stream_jitter_metrics(stream: JitterStream, p: float) -> Dict[str, Any]:
    vals = stream.raw_jitters()
    q = jitter_core.evaluate_jitter_percentile(vals, p)
    return {"count": stream.sample_count(), "jitter_p": q}
''',
        "tests/test_jitter.py": '''from jitter_types import JitterStream, JitterSample
from jitter_evaluator import check_jitter_sla, get_stream_jitter_metrics

def test_single_packet():
    s = JitterStream([JitterSample("f1", 2.0)])
    assert check_jitter_sla(s, 95.0, 5.0)
    metrics = get_stream_jitter_metrics(s, 95.0)
    assert metrics["count"] == 1

def test_identical_packets():
    s = JitterStream([JitterSample("f1", 4.0), JitterSample("f1", 4.0)])
    assert check_jitter_sla(s, 50.0, 4.0)
'''
    }

    t2074_hidden = {
        "tests/test_jitter_cases.py": '''from jitter_types import JitterStream, JitterSample
from jitter_core import evaluate_jitter_percentile
from jitter_evaluator import check_jitter_sla

def test_case_1():
    # n=6, p=50: rank = ceil(0.50 * 6) = 3 -> k=2 -> 20.0
    vals = [12.0, 15.0, 20.0, 24.0, 30.0, 36.0]
    assert evaluate_jitter_percentile(vals, 50.0) == 20.0

def test_case_2():
    stream = JitterStream([JitterSample("f", v) for v in [12.0, 15.0, 20.0, 24.0, 30.0, 36.0]])
    # 50th percentile is 20.0, max_jitter 19.0 => False
    assert not check_jitter_sla(stream, 50.0, 19.0)
    assert check_jitter_sla(stream, 50.0, 20.0)
'''
    }

    t2074_ref = {
        "jitter_core.py": '''"""Low-level jitter percentile calculation engine."""
import math
from typing import List

def evaluate_jitter_percentile(values: List[float], p: float) -> float:
    """Calculates percentile values across observed samples."""
    if not values:
        raise ValueError("No jitter values")
    s = sorted(values)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])
'''
    }

    t2074_m1 = {
        "jitter_evaluator.py": '''"""Network jitter SLA evaluation service."""
from typing import List, Dict, Any
from jitter_types import JitterStream, JitterSample
import jitter_core

def check_jitter_sla(stream: JitterStream, p: float, max_jitter: float) -> bool:
    vals = stream.raw_jitters()
    percentile_val = jitter_core.evaluate_jitter_percentile(vals, p)
    return percentile_val < max_jitter

def get_stream_jitter_metrics(stream: JitterStream, p: float) -> Dict[str, Any]:
    vals = stream.raw_jitters()
    q = jitter_core.evaluate_jitter_percentile(vals, p)
    return {"count": stream.sample_count(), "jitter_p": q}
'''
    }

    t2074_m2 = {
        "jitter_core.py": '''"""Low-level jitter percentile calculation engine."""
import math
from typing import List

def evaluate_jitter_percentile(values: List[float], p: float) -> float:
    if not values:
        raise ValueError("No jitter values")
    s = sorted(values)
    n = len(s)
    k = math.floor((p / 100.0) * n)
    return float(s[max(0, min(n - 1, k))])
'''
    }

    add_task(
        tid=2074,
        family="metric_percentiles",
        name="Network Packet Jitter Evaluator",
        class_tag="STATED",
        issue="Incident INC-7106: WAN link jitter compliance calculation failed SLA validation check.",
        traceback_text="FAILED tests/test_jitter_cases.py::test_case_1 - AssertionError: assert 22.0 == 20.0",
        traceback_files=["jitter_evaluator.py"],
        repo=t2074_repo,
        hidden=t2074_hidden,
        ref=t2074_ref,
        mutant1=t2074_m1,
        mutant2=t2074_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "jitter_evaluator.py docstring: nearest-rank method", "Yes", "STATED"),
            ("test_case_2", "jitter_evaluator.py docstring: nearest-rank method", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2075: Storage IO Wait Time Tracker (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2075_repo = {
        "io_types.py": '''"""Storage IO latency telemetry schemas."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class IoWaitSample:
    device: str
    wait_ms: float

@dataclass
class IoBatch:
    samples: List[IoWaitSample]

    def times(self) -> List[float]:
        return [s.wait_ms for s in self.samples]

    def count(self) -> int:
        return len(self.samples)
''',
        "io_summary.py": '''"""Storage wait summary formatter."""
from typing import Dict, Any

def format_io_summary(device_count: int, percentile_ms: float) -> Dict[str, Any]:
    return {"device_count": device_count, "percentile_ms": percentile_ms}
''',
        "io_calc.py": '''"""Disk IO wait time percentile calculation."""
import math
from typing import List, Dict, Any
from io_types import IoBatch, IoWaitSample
from io_summary import format_io_summary

def compute_io_percentile(batch: IoBatch, p: float) -> float:
    """Computes storage wait percentile."""
    times = batch.times()
    if not times:
        raise ValueError("Empty IO batch")
    s = sorted(times)
    n = len(s)
    idx = int((p / 100.0) * (n - 1))
    return float(s[idx])

def summarize_io_batch(batch: IoBatch, p: float) -> Dict[str, Any]:
    val = compute_io_percentile(batch, p)
    return format_io_summary(batch.count(), val)
''',
        "tests/test_io.py": '''from io_types import IoBatch, IoWaitSample
from io_calc import compute_io_percentile, summarize_io_batch

def test_single_io():
    b = IoBatch([IoWaitSample("sda", 5.0)])
    assert compute_io_percentile(b, 50.0) == 5.0
    summary = summarize_io_batch(b, 50.0)
    assert summary["device_count"] == 1

def test_equal_io():
    b = IoBatch([IoWaitSample("sda", 12.0), IoWaitSample("sda", 12.0)])
    assert compute_io_percentile(b, 90.0) == 12.0
'''
    }

    t2075_hidden = {
        "tests/test_io_cases.py": '''from io_types import IoBatch, IoWaitSample
from io_calc import compute_io_percentile

def test_case_1():
    # n=5, p=95: rank = ceil(0.95 * 5) = 5 -> k=4 -> 500.0
    samples = [IoWaitSample("sda", v) for v in [100.0, 200.0, 300.0, 400.0, 500.0]]
    b = IoBatch(samples)
    assert compute_io_percentile(b, 95.0) == 500.0

def test_case_2():
    # n=5, p=30: rank = ceil(0.30 * 5) = 2 -> k=1 -> 200.0
    samples = [IoWaitSample("sda", v) for v in [100.0, 200.0, 300.0, 400.0, 500.0]]
    b = IoBatch(samples)
    assert compute_io_percentile(b, 30.0) == 200.0
'''
    }

    t2075_ref = {
        "io_calc.py": '''"""Disk IO wait time percentile calculation."""
import math
from typing import List, Dict, Any
from io_types import IoBatch, IoWaitSample
from io_summary import format_io_summary

def compute_io_percentile(batch: IoBatch, p: float) -> float:
    """Computes storage wait percentile."""
    times = batch.times()
    if not times:
        raise ValueError("Empty IO batch")
    s = sorted(times)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])

def summarize_io_batch(batch: IoBatch, p: float) -> Dict[str, Any]:
    val = compute_io_percentile(batch, p)
    return format_io_summary(batch.count(), val)
'''
    }

    t2075_m1 = {
        "io_calc.py": '''"""Disk IO wait time percentile calculation."""
import math
from typing import List, Dict, Any
from io_types import IoBatch, IoWaitSample
from io_summary import format_io_summary

def compute_io_percentile(batch: IoBatch, p: float) -> float:
    times = batch.times()
    if not times:
        raise ValueError("Empty IO batch")
    s = sorted(times)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))

def summarize_io_batch(batch: IoBatch, p: float) -> Dict[str, Any]:
    val = compute_io_percentile(batch, p)
    return format_io_summary(batch.count(), val)
'''
    }

    t2075_m2 = {
        "io_calc.py": '''"""Disk IO wait time percentile calculation."""
import math
from typing import List, Dict, Any
from io_types import IoBatch, IoWaitSample
from io_summary import format_io_summary

def compute_io_percentile(batch: IoBatch, p: float) -> float:
    times = batch.times()
    if not times:
        raise ValueError("Empty IO batch")
    s = sorted(times)
    n = len(s)
    k = int(round((p / 100.0) * n))
    return float(s[max(0, min(n - 1, k))])

def summarize_io_batch(batch: IoBatch, p: float) -> Dict[str, Any]:
    val = compute_io_percentile(batch, p)
    return format_io_summary(batch.count(), val)
'''
    }

    add_task(
        tid=2075,
        family="metric_percentiles",
        name="Storage IO Wait Time Tracker",
        class_tag="TAUGHT",
        issue="Incident INC-7107: Storage volume performance monitoring reports inaccurate wait time quantiles.",
        traceback_text="FAILED tests/test_io_cases.py::test_case_1 - AssertionError: assert 400.0 == 500.0",
        traceback_files=["io_calc.py"],
        repo=t2075_repo,
        hidden=t2075_hidden,
        ref=t2075_ref,
        mutant1=t2075_m1,
        mutant2=t2075_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H14: Metric percentile nearest-rank method", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2076: Model Training Loss Reporter (DISTRACTOR, HRC=True, VTS=False)
    # =========================================================================
    t2076_repo = {
        "loss_types.py": '''"""Training loss telemetry structures."""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class LossEntry:
    step: int
    loss_val: float

@dataclass
class EpochLossRecord:
    entries: List[LossEntry]

    def values(self) -> List[float]:
        return [e.loss_val for e in self.entries]

    def step_count(self) -> int:
        return len(self.entries)
''',
        "loss_math.py": '''"""Loss distribution percentile calculator."""
import math
from typing import List

def calculate_loss_percentile(losses: List[float], p: float) -> float:
    """Calculates training loss percentile."""
    if not losses:
        raise ValueError("No loss values")
    s = sorted(losses)
    n = len(s)
    # Erroneous nearest-rank logic in distractor task
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])
''',
        "loss_reporter.py": '''"""Model loss telemetry evaluation service."""
from typing import List, Dict, Any
from loss_types import EpochLossRecord, LossEntry
import loss_math

def report_loss_summary(record: EpochLossRecord, percentile: float) -> Dict[str, float]:
    """Continuous loss distribution requires continuous linear interpolation (numpy-style).
    Do not use nearest-rank method.
    """
    vals = record.values()
    q = loss_math.calculate_loss_percentile(vals, percentile)
    return {"quantile": q}

def get_epoch_overview(record: EpochLossRecord, percentile: float) -> Dict[str, Any]:
    summary = report_loss_summary(record, percentile)
    return {"steps": record.step_count(), "loss_quantile": summary["quantile"]}
''',
        "tests/test_loss.py": '''from loss_types import EpochLossRecord, LossEntry
from loss_reporter import report_loss_summary, get_epoch_overview

def test_single_loss():
    r = EpochLossRecord([LossEntry(1, 0.45)])
    res = report_loss_summary(r, 50.0)
    assert res["quantile"] == 0.45
    overview = get_epoch_overview(r, 50.0)
    assert overview["steps"] == 1

def test_identical_losses():
    r = EpochLossRecord([LossEntry(1, 0.2), LossEntry(2, 0.2)])
    res = report_loss_summary(r, 90.0)
    assert res["quantile"] == 0.2
'''
    }

    t2076_hidden = {
        "tests/test_loss_cases.py": '''from loss_types import EpochLossRecord, LossEntry
from loss_math import calculate_loss_percentile
from loss_reporter import report_loss_summary

def test_case_1():
    # Linear interpolation: n=6, p=75: idx = 0.75 * 5 = 3.75 -> 24.0 + 0.75 * 6.0 = 28.5
    vals = [12.0, 15.0, 20.0, 24.0, 30.0, 36.0]
    assert calculate_loss_percentile(vals, 75.0) == 28.5

def test_case_2():
    entries = [LossEntry(i, v) for i, v in enumerate([12.0, 15.0, 20.0, 24.0, 30.0, 36.0])]
    rec = EpochLossRecord(entries)
    res = report_loss_summary(rec, 75.0)
    assert res["quantile"] == 28.5
'''
    }

    t2076_ref = {
        "loss_math.py": '''"""Loss distribution percentile calculator."""
import math
from typing import List

def calculate_loss_percentile(losses: List[float], p: float) -> float:
    """Calculates training loss percentile."""
    if not losses:
        raise ValueError("No loss values")
    s = sorted(losses)
    n = len(s)
    idx = (p / 100.0) * (n - 1)
    low = int(math.floor(idx))
    high = int(math.ceil(idx))
    if low == high:
        return float(s[low])
    frac = idx - low
    return float(s[low] + frac * (s[high] - s[low]))
'''
    }

    t2076_m1 = {
        "loss_math.py": '''"""Loss distribution percentile calculator."""
import math
from typing import List

def calculate_loss_percentile(losses: List[float], p: float) -> float:
    if not losses:
        raise ValueError("No loss values")
    s = sorted(losses)
    n = len(s)
    rank = math.ceil((p / 100.0) * n)
    k = max(0, min(n - 1, rank - 1))
    return float(s[k])
'''
    }

    t2076_m2 = {
        "loss_reporter.py": '''"""Model loss telemetry evaluation service."""
from typing import List, Dict, Any
from loss_types import EpochLossRecord, LossEntry
import loss_math

def report_loss_summary(record: EpochLossRecord, percentile: float) -> Dict[str, float]:
    vals = record.values()
    q = loss_math.calculate_loss_percentile(vals, percentile)
    return {"quantile": float(round(q))}

def get_epoch_overview(record: EpochLossRecord, percentile: float) -> Dict[str, Any]:
    summary = report_loss_summary(record, percentile)
    return {"steps": record.step_count(), "loss_quantile": summary["quantile"]}
'''
    }

    add_task(
        tid=2076,
        family="metric_percentiles",
        name="Model Training Loss Reporter",
        class_tag="DISTRACTOR",
        issue="Incident INC-7108: Model evaluation service loss summary reports discontinuous step values.",
        traceback_text="FAILED tests/test_loss_cases.py::test_case_1 - AssertionError: assert 30.0 == 28.5",
        traceback_files=["loss_reporter.py"],
        repo=t2076_repo,
        hidden=t2076_hidden,
        ref=t2076_ref,
        mutant1=t2076_m1,
        mutant2=t2076_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H14"],
        assertions=[
            ("test_case_1", "loss_reporter.py docstring: Continuous linear interpolation", "Yes", "DISTRACTOR"),
            ("test_case_2", "loss_reporter.py docstring: Continuous linear interpolation", "Yes", "DISTRACTOR")
        ]
    )

    print("Family 13 registered (Tasks 2069-2076).")
