"""Family 10: timestamp_iso (Tasks 2045 - 2052).

Governing Rule: Rule H09 (Canonical UTC Timestamp Formatting with Millisecond Precision:
format strictly in ISO 8601 UTC with explicit millisecond precision and uppercase 'Z' suffix:
YYYY-MM-DDTHH:MM:SS.sssZ, e.g. "2026-10-25T12:00:00.000Z". Microsecond precision, timezone offsets,
or omission of milliseconds are rejected.)
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_10(add_task):
    # =========================================================================
    # Task 2045: Audit Event Timestamp Normalizer (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2045_repo = {
        "models.py": '''"""Data models for audit events."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class AuditRecord:
    event_id: str
    action: str
    timestamp_str: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return bool(self.event_id and self.action and self.timestamp_str)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.event_id,
            "action": self.action,
            "timestamp": self.timestamp_str,
            "metadata": self.metadata
        }
''',
        "formatter.py": '''"""Event string sanitization and tagging helpers."""
from typing import Dict, Any

def sanitize_action_name(action: str) -> str:
    cleaned = action.strip().lower()
    if not cleaned:
        raise ValueError("Action cannot be empty")
    return cleaned

def build_audit_tag(action: str, category: str = "security") -> str:
    return f"{category}:{action}"
''',
        "audit_service.py": '''"""Audit event serialization service."""
from datetime import datetime
from models import AuditRecord
from formatter import sanitize_action_name, build_audit_tag

def format_audit_event(event_id: str, action: str, dt: datetime) -> AuditRecord:
    """Formats an audit event record.
    Timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond
    precision and uppercase 'Z' suffix: YYYY-MM-DDTHH:MM:SS.sssZ (e.g. 2026-10-25T12:00:00.000Z).
    """
    clean_action = sanitize_action_name(action)
    tag = build_audit_tag(clean_action)
    ts = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    record = AuditRecord(
        event_id=event_id,
        action=clean_action,
        timestamp_str=ts,
        metadata={"tag": tag}
    )
    if not record.is_valid():
        raise ValueError("Invalid record generated")
    return record
''',
        "tests/test_audit.py": '''from datetime import datetime, timezone
from audit_service import format_audit_event

def test_service_execution():
    dt = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
    rec = format_audit_event("EVT-1", "LOGIN", dt)
    assert rec.event_id == "EVT-1"
    assert rec.action == "login"
    assert rec.metadata["tag"] == "security:login"
    assert rec.timestamp_str.endswith("Z")
'''
    }

    t2045_hidden = {
        "tests/test_audit_cases.py": '''from datetime import datetime, timezone
from audit_service import format_audit_event

def test_case_1():
    dt = datetime(2026, 10, 25, 12, 0, 0, 0, tzinfo=timezone.utc)
    rec = format_audit_event("EVT-1", "LOGIN", dt)
    assert rec.timestamp_str == "2026-10-25T12:00:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 8, 30, 15, 123456, tzinfo=timezone.utc)
    rec = format_audit_event("EVT-2", "LOGOUT", dt)
    assert rec.timestamp_str == "2026-10-25T08:30:15.123Z"
'''
    }

    t2045_ref = {
        "audit_service.py": '''"""Audit event serialization service."""
from datetime import datetime, timezone
from models import AuditRecord
from formatter import sanitize_action_name, build_audit_tag

def format_audit_event(event_id: str, action: str, dt: datetime) -> AuditRecord:
    """Formats an audit event record.
    Timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond
    precision and uppercase 'Z' suffix: YYYY-MM-DDTHH:MM:SS.sssZ (e.g. 2026-10-25T12:00:00.000Z).
    """
    clean_action = sanitize_action_name(action)
    tag = build_audit_tag(clean_action)
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    ts = f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"
    record = AuditRecord(
        event_id=event_id,
        action=clean_action,
        timestamp_str=ts,
        metadata={"tag": tag}
    )
    if not record.is_valid():
        raise ValueError("Invalid record generated")
    return record
'''
    }

    t2045_m1 = {
        "audit_service.py": '''"""Audit event serialization service."""
from datetime import datetime, timezone
from models import AuditRecord
from formatter import sanitize_action_name, build_audit_tag

def format_audit_event(event_id: str, action: str, dt: datetime) -> AuditRecord:
    clean_action = sanitize_action_name(action)
    tag = build_audit_tag(clean_action)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return AuditRecord(
        event_id=event_id,
        action=clean_action,
        timestamp_str=ts,
        metadata={"tag": tag}
    )
'''
    }

    t2045_m2 = {
        "audit_service.py": '''"""Audit event serialization service."""
from datetime import datetime, timezone
from models import AuditRecord
from formatter import sanitize_action_name, build_audit_tag

def format_audit_event(event_id: str, action: str, dt: datetime) -> AuditRecord:
    clean_action = sanitize_action_name(action)
    tag = build_audit_tag(clean_action)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return AuditRecord(
        event_id=event_id,
        action=clean_action,
        timestamp_str=ts,
        metadata={"tag": tag}
    )
'''
    }

    add_task(
        tid=2045,
        family="timestamp_iso",
        name="Audit Event Timestamp Normalizer",
        class_tag="STATED",
        issue="Incident INC-9101: Audit log reconciliation failed schema verification because timestamps lacked explicit millisecond precision.",
        traceback_text="FAILED tests/test_audit_cases.py::test_case_1 - AssertionError: assert '2026-10-25T12:00:00Z' == '2026-10-25T12:00:00.000Z'",
        traceback_files=["audit_service.py"],
        repo=t2045_repo,
        hidden=t2045_hidden,
        ref=t2045_ref,
        mutant1=t2045_m1,
        mutant2=t2045_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "audit_service.py docstring: 'explicit millisecond precision and uppercase Z suffix'", "Yes", "STATED"),
            ("test_case_2", "audit_service.py docstring: 'explicit millisecond precision and uppercase Z suffix'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2046: Telemetry Log Serializer (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2046_repo = {
        "telemetry_codec.py": '''"""Timestamp serialization codec for telemetry records."""
from datetime import datetime, timezone

def encode_iso_timestamp(dt: datetime) -> str:
    """Encode timestamp into standard format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_timestamp_range(dt: datetime) -> bool:
    return dt.year >= 2020
''',
        "metrics_collector.py": '''"""Metrics tagging and categorization utilities."""
from typing import Dict, Any

def build_metric_tags(service: str, env: str) -> Dict[str, str]:
    if not service:
        raise ValueError("Service name required")
    return {
        "service": service.lower(),
        "env": env.lower(),
        "tier": "backend"
    }

def format_metric_key(service: str, metric_name: str) -> str:
    return f"{service}.{metric_name}"
''',
        "log_pipeline.py": '''"""Telemetry log aggregation pipeline."""
from datetime import datetime
from typing import Dict, Any
from telemetry_codec import encode_iso_timestamp, validate_timestamp_range
from metrics_collector import build_metric_tags, format_metric_key

def export_telemetry_batch(service: str, metric_name: str, value: float, dt: datetime) -> Dict[str, Any]:
    if not validate_timestamp_range(dt):
        raise ValueError("Timestamp out of supported range")
    tags = build_metric_tags(service, "production")
    key = format_metric_key(service, metric_name)
    ts_str = encode_iso_timestamp(dt)
    return {
        "key": key,
        "metric": metric_name,
        "value": float(value),
        "tags": tags,
        "timestamp": ts_str
    }
''',
        "tests/test_pipeline.py": '''from datetime import datetime, timezone
from log_pipeline import export_telemetry_batch

def test_service_execution():
    dt = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
    batch = export_telemetry_batch("auth_svc", "cpu_load", 0.75, dt)
    assert batch["metric"] == "cpu_load"
    assert batch["tags"]["env"] == "production"
    assert batch["key"] == "auth_svc.cpu_load"
'''
    }

    t2046_hidden = {
        "tests/test_pipeline_cases.py": '''from datetime import datetime, timezone
from log_pipeline import export_telemetry_batch
from telemetry_codec import encode_iso_timestamp

def test_case_1():
    dt = datetime(2026, 10, 25, 12, 0, 0, 0, tzinfo=timezone.utc)
    batch = export_telemetry_batch("auth_svc", "cpu_load", 0.75, dt)
    assert batch["timestamp"] == "2026-10-25T12:00:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 14, 20, 10, 500000, tzinfo=timezone.utc)
    assert encode_iso_timestamp(dt) == "2026-10-25T14:20:10.500Z"
'''
    }

    t2046_ref = {
        "telemetry_codec.py": '''"""Timestamp serialization codec for telemetry records."""
from datetime import datetime, timezone

def encode_iso_timestamp(dt: datetime) -> str:
    """Encode timestamp into standard format."""
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    return f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"

def validate_timestamp_range(dt: datetime) -> bool:
    return dt.year >= 2020
'''
    }

    t2046_m1 = {
        "telemetry_codec.py": '''"""Timestamp serialization codec for telemetry records."""
from datetime import datetime, timezone

def encode_iso_timestamp(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def validate_timestamp_range(dt: datetime) -> bool:
    return dt.year >= 2020
'''
    }

    t2046_m2 = {
        "telemetry_codec.py": '''"""Timestamp serialization codec for telemetry records."""
from datetime import datetime, timezone

def encode_iso_timestamp(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return str(int(utc_dt.timestamp()))

def validate_timestamp_range(dt: datetime) -> bool:
    return dt.year >= 2020
'''
    }

    add_task(
        tid=2046,
        family="timestamp_iso",
        name="Telemetry Log Serializer",
        class_tag="TAUGHT",
        issue="Incident INC-9102: Ingestion workers rejected telemetry log exports due to non-standard timestamp format.",
        traceback_text="FAILED tests/test_pipeline_cases.py::test_case_1 - AssertionError: assert '2026-10-25 12:00:00' == '2026-10-25T12:00:00.000Z'",
        traceback_files=["log_pipeline.py"],
        repo=t2046_repo,
        hidden=t2046_hidden,
        ref=t2046_ref,
        mutant1=t2046_m1,
        mutant2=t2046_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2047: Webhook Delivery Envelope (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2047_repo = {
        "envelope_schema.py": '''"""Schema definitions for webhook payloads."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class WebhookEnvelope:
    topic: str
    body: Dict[str, Any]
    sent_at: str
    headers: Dict[str, str] = field(default_factory=dict)

    def is_dispatched(self) -> bool:
        return bool(self.topic and self.sent_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "body": self.body,
            "sent_at": self.sent_at,
            "headers": self.headers
        }
''',
        "signature_utils.py": '''"""Webhook signature computation and hashing."""
import hashlib
from typing import Dict, Any

def compute_payload_hash(topic: str) -> str:
    return hashlib.sha256(topic.encode("utf-8")).hexdigest()[:12]

def generate_delivery_headers(topic: str) -> Dict[str, str]:
    digest = compute_payload_hash(topic)
    return {"X-Webhook-Signature": digest, "X-Webhook-Version": "1.0"}

def verify_delivery_signature(topic: str, signature: str) -> bool:
    return compute_payload_hash(topic) == signature
''',
        "webhook_sender.py": '''"""Webhook delivery payload construction."""
from datetime import datetime, timezone
from typing import Dict, Any
from envelope_schema import WebhookEnvelope
from signature_utils import generate_delivery_headers

def build_webhook_payload(topic: str, data: Dict[str, Any], dt: datetime) -> WebhookEnvelope:
    hdrs = generate_delivery_headers(topic)
    ts = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    env = WebhookEnvelope(topic=topic, body=data, sent_at=ts, headers=hdrs)
    if not env.is_dispatched():
        raise ValueError("Invalid envelope state")
    return env
''',
        "tests/test_webhook.py": '''from datetime import datetime, timezone
from webhook_sender import build_webhook_payload

def test_service_execution():
    dt = datetime(2026, 10, 25, 10, 0, 0, 100000, tzinfo=timezone.utc)
    env = build_webhook_payload("user.created", {"user_id": 42}, dt)
    assert env.topic == "user.created"
    assert env.body["user_id"] == 42
    assert env.sent_at.endswith("Z")
    assert "X-Webhook-Signature" in env.headers
'''
    }

    t2047_hidden = {
        "tests/test_webhook_cases.py": '''from datetime import datetime, timezone
from webhook_sender import build_webhook_payload

def test_case_1():
    dt = datetime(2026, 10, 25, 10, 0, 0, 0, tzinfo=timezone.utc)
    env = build_webhook_payload("user.created", {"id": 1}, dt)
    assert env.sent_at == "2026-10-25T10:00:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 10, 0, 0, 987654, tzinfo=timezone.utc)
    env = build_webhook_payload("user.updated", {"id": 2}, dt)
    assert env.sent_at == "2026-10-25T10:00:00.987Z"
'''
    }

    t2047_ref = {
        "webhook_sender.py": '''"""Webhook delivery payload construction."""
from datetime import datetime, timezone
from typing import Dict, Any
from envelope_schema import WebhookEnvelope
from signature_utils import generate_delivery_headers

def build_webhook_payload(topic: str, data: Dict[str, Any], dt: datetime) -> WebhookEnvelope:
    hdrs = generate_delivery_headers(topic)
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    ts = f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"
    env = WebhookEnvelope(topic=topic, body=data, sent_at=ts, headers=hdrs)
    if not env.is_dispatched():
        raise ValueError("Invalid envelope state")
    return env
'''
    }

    t2047_m1 = {
        "webhook_sender.py": '''"""Webhook delivery payload construction."""
from datetime import datetime, timezone
from typing import Dict, Any
from envelope_schema import WebhookEnvelope
from signature_utils import generate_delivery_headers

def build_webhook_payload(topic: str, data: Dict[str, Any], dt: datetime) -> WebhookEnvelope:
    hdrs = generate_delivery_headers(topic)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return WebhookEnvelope(topic=topic, body=data, sent_at=ts, headers=hdrs)
'''
    }

    t2047_m2 = {
        "webhook_sender.py": '''"""Webhook delivery payload construction."""
from datetime import datetime, timezone
from typing import Dict, Any
from envelope_schema import WebhookEnvelope
from signature_utils import generate_delivery_headers

def build_webhook_payload(topic: str, data: Dict[str, Any], dt: datetime) -> WebhookEnvelope:
    hdrs = generate_delivery_headers(topic)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.isoformat()
    return WebhookEnvelope(topic=topic, body=data, sent_at=ts, headers=hdrs)
'''
    }

    add_task(
        tid=2047,
        family="timestamp_iso",
        name="Webhook Delivery Envelope",
        class_tag="TAUGHT",
        issue="Incident INC-9103: Webhook payload timestamp format rejected by subscriber gateways.",
        traceback_text="FAILED tests/test_webhook_cases.py::test_case_1 - AssertionError: assert '2026-10-25T10:00:00.000000Z' == '2026-10-25T10:00:00.000Z'",
        traceback_files=["webhook_sender.py"],
        repo=t2047_repo,
        hidden=t2047_hidden,
        ref=t2047_ref,
        mutant1=t2047_m1,
        mutant2=t2047_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2048: High-Throughput Stream Ingestion (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2048_repo = {
        "stream_packet.py": '''"""Packet representations for binary streaming."""
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class StreamPacket:
    stream_id: str
    data: Any
    timestamp: int
    attributes: Dict[str, str] = field(default_factory=dict)

    def packet_size(self) -> int:
        return len(str(self.data))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "data": self.data,
            "timestamp": self.timestamp,
            "attributes": self.attributes
        }
''',
        "channel_filter.py": '''"""Channel validation filters and router."""
def is_valid_channel(channel: str) -> bool:
    return len(channel) > 0 and channel.isalnum()

def derive_channel_partition(channel: str) -> int:
    return hash(channel) % 16
''',
        "stream_ingest.py": '''"""High-throughput stream packet ingest."""
from datetime import datetime
from stream_packet import StreamPacket
from channel_filter import is_valid_channel, derive_channel_partition

def ingest_packet(channel: str, payload: str, dt: datetime) -> StreamPacket:
    """Ingest real-time packet for stream processing.
    Local requirement: Timestamps must be formatted as Unix epoch integer seconds (int(dt.timestamp())).
    Performance critical: do NOT use ISO 8601 string formatting.
    """
    if not is_valid_channel(channel):
        raise ValueError("Invalid channel")
    partition = str(derive_channel_partition(channel))
    ts = str(dt)
    return StreamPacket(
        stream_id=channel,
        data=payload,
        timestamp=ts,
        attributes={"partition": partition}
    )
''',
        "tests/test_stream.py": '''from datetime import datetime, timezone
from stream_ingest import ingest_packet

def test_service_execution():
    dt = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
    pkt = ingest_packet("chan1", "sample_data", dt)
    assert pkt.stream_id == "chan1"
    assert pkt.data == "sample_data"
    assert "partition" in pkt.attributes
'''
    }

    t2048_hidden = {
        "tests/test_stream_cases.py": '''from datetime import datetime, timezone
from stream_ingest import ingest_packet

def test_case_1():
    dt = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
    pkt = ingest_packet("chan1", "sample_data", dt)
    assert pkt.timestamp == 1792929600
    assert isinstance(pkt.timestamp, int)

def test_case_2():
    dt = datetime(2026, 10, 25, 12, 0, 10, 500000, tzinfo=timezone.utc)
    pkt = ingest_packet("chan2", "payload_b", dt)
    assert pkt.timestamp == 1792929610
    assert isinstance(pkt.timestamp, int)
'''
    }

    t2048_ref = {
        "stream_ingest.py": '''"""High-throughput stream packet ingest."""
from datetime import datetime
from stream_packet import StreamPacket
from channel_filter import is_valid_channel, derive_channel_partition

def ingest_packet(channel: str, payload: str, dt: datetime) -> StreamPacket:
    """Ingest real-time packet for stream processing.
    Local requirement: Timestamps must be formatted as Unix epoch integer seconds (int(dt.timestamp())).
    Performance critical: do NOT use ISO 8601 string formatting.
    """
    if not is_valid_channel(channel):
        raise ValueError("Invalid channel")
    partition = str(derive_channel_partition(channel))
    ts = int(dt.timestamp())
    return StreamPacket(
        stream_id=channel,
        data=payload,
        timestamp=ts,
        attributes={"partition": partition}
    )
'''
    }

    t2048_m1 = {
        "stream_ingest.py": '''"""High-throughput stream packet ingest."""
from datetime import datetime, timezone
from stream_packet import StreamPacket
from channel_filter import is_valid_channel, derive_channel_partition

def ingest_packet(channel: str, payload: str, dt: datetime) -> StreamPacket:
    if not is_valid_channel(channel):
        raise ValueError("Invalid channel")
    partition = str(derive_channel_partition(channel))
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    ts = f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"
    return StreamPacket(
        stream_id=channel,
        data=payload,
        timestamp=ts,
        attributes={"partition": partition}
    )
'''
    }

    t2048_m2 = {
        "stream_ingest.py": '''"""High-throughput stream packet ingest."""
from datetime import datetime
from stream_packet import StreamPacket
from channel_filter import is_valid_channel, derive_channel_partition

def ingest_packet(channel: str, payload: str, dt: datetime) -> StreamPacket:
    if not is_valid_channel(channel):
        raise ValueError("Invalid channel")
    partition = str(derive_channel_partition(channel))
    ts = float(dt.timestamp())
    return StreamPacket(
        stream_id=channel,
        data=payload,
        timestamp=ts,
        attributes={"partition": partition}
    )
'''
    }

    add_task(
        tid=2048,
        family="timestamp_iso",
        name="High-Throughput Stream Ingestion",
        class_tag="DISTRACTOR",
        issue="Incident INC-9104: Stream consumer crashed on unexpected string timestamp; stream processor requires integer epoch.",
        traceback_text="FAILED tests/test_stream_cases.py::test_case_1 - AssertionError: assert '2026-10-25 12:00:00+00:00' == 1792929600",
        traceback_files=["stream_ingest.py"],
        repo=t2048_repo,
        hidden=t2048_hidden,
        ref=t2048_ref,
        mutant1=t2048_m1,
        mutant2=t2048_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "stream_ingest.py docstring: 'Timestamps must be formatted as Unix epoch integer seconds'", "Yes", "DISTRACTOR"),
            ("test_case_2", "stream_ingest.py docstring: 'Timestamps must be formatted as Unix epoch integer seconds'", "Yes", "DISTRACTOR"),
        ]
    )

    # =========================================================================
    # Task 2049: Database Snapshot Metadata Generator (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2049_repo = {
        "snapshot_manifest.py": '''"""Snapshot manifest timestamp formatting."""
from datetime import datetime, timezone

def format_snapshot_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_snapshot_epoch(dt: datetime) -> int:
    return int(dt.timestamp())
''',
        "storage_allocator.py": '''"""Storage volume allocator and metrics."""
from typing import Dict, Any

def calculate_block_count(size_mb: int) -> int:
    return size_mb * 256

def estimate_checksum_length(blocks: int) -> int:
    return blocks // 16

def get_volume_tier(size_mb: int) -> str:
    return "high_capacity" if size_mb > 1000 else "standard"

def is_valid_size(size_mb: int) -> bool:
    return size_mb > 0
''',
        "snapshot_manager.py": '''"""Snapshot manifest coordinator."""
from datetime import datetime
from typing import Dict, Any
from snapshot_manifest import format_snapshot_timestamp, parse_snapshot_epoch
from storage_allocator import calculate_block_count, estimate_checksum_length, get_volume_tier

def create_snapshot_manifest(snapshot_id: str, size_mb: int, dt: datetime) -> Dict[str, Any]:
    blocks = calculate_block_count(size_mb)
    chk_len = estimate_checksum_length(blocks)
    tier = get_volume_tier(size_mb)
    epoch_sec = parse_snapshot_epoch(dt)
    ts = format_snapshot_timestamp(dt)
    return {
        "snapshot_id": snapshot_id,
        "blocks": blocks,
        "checksum_len": chk_len,
        "tier": tier,
        "epoch": epoch_sec,
        "created_at": ts
    }
''',
        "tests/test_snapshot.py": '''from datetime import datetime, timezone
from snapshot_manager import create_snapshot_manifest

def test_service_execution():
    dt = datetime(2026, 10, 25, 6, 0, 0, tzinfo=timezone.utc)
    manifest = create_snapshot_manifest("snp-100", 10, dt)
    assert manifest["snapshot_id"] == "snp-100"
    assert manifest["blocks"] == 2560
    assert manifest["created_at"].endswith("Z")
'''
    }

    t2049_hidden = {
        "tests/test_snapshot_cases.py": '''from datetime import datetime, timezone
from snapshot_manager import create_snapshot_manifest
from snapshot_manifest import format_snapshot_timestamp

def test_case_1():
    dt = datetime(2026, 10, 25, 6, 0, 0, 0, tzinfo=timezone.utc)
    manifest = create_snapshot_manifest("snp-100", 10, dt)
    assert manifest["created_at"] == "2026-10-25T06:00:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 7, 15, 30, 450000, tzinfo=timezone.utc)
    assert format_snapshot_timestamp(dt) == "2026-10-25T07:15:30.450Z"
'''
    }

    t2049_ref = {
        "snapshot_manifest.py": '''"""Snapshot manifest timestamp formatting."""
from datetime import datetime, timezone

def format_snapshot_timestamp(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    return f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"

def parse_snapshot_epoch(dt: datetime) -> int:
    return int(dt.timestamp())
'''
    }

    t2049_m1 = {
        "snapshot_manifest.py": '''"""Snapshot manifest timestamp formatting."""
from datetime import datetime, timezone

def format_snapshot_timestamp(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def parse_snapshot_epoch(dt: datetime) -> int:
    return int(dt.timestamp())
'''
    }

    t2049_m2 = {
        "snapshot_manifest.py": '''"""Snapshot manifest timestamp formatting."""
from datetime import datetime, timezone

def format_snapshot_timestamp(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    return f"{utc_dt.strftime('%Y-%m-%d %H:%M:%S')}.{ms:03d}"

def parse_snapshot_epoch(dt: datetime) -> int:
    return int(dt.timestamp())
'''
    }

    add_task(
        tid=2049,
        family="timestamp_iso",
        name="Database Snapshot Metadata Generator",
        class_tag="TAUGHT",
        issue="Incident INC-9105: Automated replication service failed reading backup metadata timestamp.",
        traceback_text="FAILED tests/test_snapshot_cases.py::test_case_1 - AssertionError: assert '2026-10-25T06:00:00Z' == '2026-10-25T06:00:00.000Z'",
        traceback_files=["snapshot_manager.py"],
        repo=t2049_repo,
        hidden=t2049_hidden,
        ref=t2049_ref,
        mutant1=t2049_m1,
        mutant2=t2049_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2050: API Gateway Request Journal (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2050_repo = {
        "journal_entry.py": '''"""Journal entry models for gateway traffic."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class JournalEntry:
    request_id: str
    status_code: int
    logged_at: str
    context: Dict[str, Any] = field(default_factory=dict)

    def is_successful(self) -> bool:
        return 200 <= self.status_code < 300
''',
        "status_catalog.py": '''"""HTTP status code categorization and tags."""
def is_error_status(status_code: int) -> bool:
    return status_code >= 400

def get_status_label(status_code: int) -> str:
    if status_code < 300:
        return "success"
    if status_code < 400:
        return "redirect"
    return "client_or_server_error"
''',
        "journal_writer.py": '''"""API gateway request journal writer."""
from datetime import datetime
from journal_entry import JournalEntry
from status_catalog import is_error_status, get_status_label

def record_request(request_id: str, status_code: int, dt: datetime) -> JournalEntry:
    """Records incoming HTTP request journal entry.
    Timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond
    precision and uppercase 'Z' suffix: YYYY-MM-DDTHH:MM:SS.sssZ.
    """
    _ = is_error_status(status_code)
    label = get_status_label(status_code)
    ts = dt.strftime("%Y-%m-%d %H:%M:%S")
    return JournalEntry(
        request_id=request_id,
        status_code=status_code,
        logged_at=ts,
        context={"label": label}
    )
''',
        "tests/test_journal.py": '''from datetime import datetime, timezone
from journal_writer import record_request

def test_service_execution():
    dt = datetime(2026, 10, 25, 15, 30, 0, tzinfo=timezone.utc)
    entry = record_request("req-99", 200, dt)
    assert entry.request_id == "req-99"
    assert entry.status_code == 200
    assert entry.context["label"] == "success"
'''
    }

    t2050_hidden = {
        "tests/test_journal_cases.py": '''from datetime import datetime, timezone
from journal_writer import record_request

def test_case_1():
    dt = datetime(2026, 10, 25, 15, 30, 0, 0, tzinfo=timezone.utc)
    entry = record_request("req-99", 200, dt)
    assert entry.logged_at == "2026-10-25T15:30:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 15, 30, 0, 789123, tzinfo=timezone.utc)
    entry = record_request("req-100", 404, dt)
    assert entry.logged_at == "2026-10-25T15:30:00.789Z"
'''
    }

    t2050_ref = {
        "journal_writer.py": '''"""API gateway request journal writer."""
from datetime import datetime, timezone
from journal_entry import JournalEntry
from status_catalog import is_error_status, get_status_label

def record_request(request_id: str, status_code: int, dt: datetime) -> JournalEntry:
    """Records incoming HTTP request journal entry.
    Timestamps must be formatted strictly in ISO 8601 UTC with explicit millisecond
    precision and uppercase 'Z' suffix: YYYY-MM-DDTHH:MM:SS.sssZ.
    """
    _ = is_error_status(status_code)
    label = get_status_label(status_code)
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    ts = f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"
    return JournalEntry(
        request_id=request_id,
        status_code=status_code,
        logged_at=ts,
        context={"label": label}
    )
'''
    }

    t2050_m1 = {
        "journal_writer.py": '''"""API gateway request journal writer."""
from datetime import datetime, timezone
from journal_entry import JournalEntry
from status_catalog import is_error_status, get_status_label

def record_request(request_id: str, status_code: int, dt: datetime) -> JournalEntry:
    _ = is_error_status(status_code)
    label = get_status_label(status_code)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return JournalEntry(
        request_id=request_id,
        status_code=status_code,
        logged_at=ts,
        context={"label": label}
    )
'''
    }

    t2050_m2 = {
        "journal_writer.py": '''"""API gateway request journal writer."""
from datetime import datetime, timezone
from journal_entry import JournalEntry
from status_catalog import is_error_status, get_status_label

def record_request(request_id: str, status_code: int, dt: datetime) -> JournalEntry:
    _ = is_error_status(status_code)
    label = get_status_label(status_code)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return JournalEntry(
        request_id=request_id,
        status_code=status_code,
        logged_at=ts,
        context={"label": label}
    )
'''
    }

    add_task(
        tid=2050,
        family="timestamp_iso",
        name="API Gateway Request Journal",
        class_tag="STATED",
        issue="Incident INC-9106: Central SIEM pipeline discarded access log records with unparsed timestamps.",
        traceback_text="FAILED tests/test_journal_cases.py::test_case_1 - AssertionError: assert '2026-10-25 15:30:00' == '2026-10-25T15:30:00.000Z'",
        traceback_files=["journal_writer.py"],
        repo=t2050_repo,
        hidden=t2050_hidden,
        ref=t2050_ref,
        mutant1=t2050_m1,
        mutant2=t2050_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "journal_writer.py docstring: 'explicit millisecond precision and uppercase Z suffix'", "Yes", "STATED"),
            ("test_case_2", "journal_writer.py docstring: 'explicit millisecond precision and uppercase Z suffix'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2051: Security Token Exchange Ledger (TAUGHT, HRC=True, VTS=True)
    # =========================================================================
    t2051_repo = {
        "token_codec.py": '''"""Token issuance time encoding."""
from datetime import datetime, timezone

def serialize_issuance_time(dt: datetime) -> str:
    return dt.isoformat()

def compute_token_expiry_epoch(dt: datetime, lifetime_seconds: int = 3600) -> int:
    return int(dt.timestamp()) + lifetime_seconds
''',
        "vault_registry.py": '''"""Vault client identifier verification and attributes."""
from typing import Dict, Any

def verify_client_scope(client_id: str) -> bool:
    return bool(client_id and client_id.startswith("cli_"))

def get_client_domain(client_id: str) -> str:
    return f"{client_id}.internal"

def get_client_role(client_id: str) -> str:
    return "admin" if "admin" in client_id else "worker"
''',
        "ledger_service.py": '''"""Token exchange ledger service."""
from datetime import datetime
from typing import Dict, Any
from token_codec import serialize_issuance_time, compute_token_expiry_epoch
from vault_registry import verify_client_scope, get_client_domain, get_client_role

def record_token_issuance(token_id: str, client_id: str, dt: datetime) -> Dict[str, Any]:
    if not verify_client_scope(client_id):
        raise ValueError("Invalid client scope")
    domain = get_client_domain(client_id)
    role = get_client_role(client_id)
    exp = compute_token_expiry_epoch(dt)
    ts = serialize_issuance_time(dt)
    return {
        "token_id": token_id,
        "client_id": client_id,
        "domain": domain,
        "role": role,
        "expires_epoch": exp,
        "issued_at": ts
    }
''',
        "tests/test_ledger.py": '''from datetime import datetime, timezone
from ledger_service import record_token_issuance

def test_service_execution():
    dt = datetime(2026, 10, 25, 18, 0, 0, tzinfo=timezone.utc)
    rec = record_token_issuance("tok-55", "cli_backend", dt)
    assert rec["token_id"] == "tok-55"
    assert rec["client_id"] == "cli_backend"
    assert rec["domain"] == "cli_backend.internal"
'''
    }

    t2051_hidden = {
        "tests/test_ledger_cases.py": '''from datetime import datetime, timezone
from ledger_service import record_token_issuance
from token_codec import serialize_issuance_time

def test_case_1():
    dt = datetime(2026, 10, 25, 18, 0, 0, 0, tzinfo=timezone.utc)
    rec = record_token_issuance("tok-55", "cli_backend", dt)
    assert rec["issued_at"] == "2026-10-25T18:00:00.000Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 18, 0, 0, 250000, tzinfo=timezone.utc)
    assert serialize_issuance_time(dt) == "2026-10-25T18:00:00.250Z"
'''
    }

    t2051_ref = {
        "token_codec.py": '''"""Token issuance time encoding."""
from datetime import datetime, timezone

def serialize_issuance_time(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    return f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"

def compute_token_expiry_epoch(dt: datetime, lifetime_seconds: int = 3600) -> int:
    return int(dt.timestamp()) + lifetime_seconds
'''
    }

    t2051_m1 = {
        "token_codec.py": '''"""Token issuance time encoding."""
from datetime import datetime, timezone

def serialize_issuance_time(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def compute_token_expiry_epoch(dt: datetime, lifetime_seconds: int = 3600) -> int:
    return int(dt.timestamp()) + lifetime_seconds
'''
    }

    t2051_m2 = {
        "token_codec.py": '''"""Token issuance time encoding."""
from datetime import datetime, timezone

def serialize_issuance_time(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

def compute_token_expiry_epoch(dt: datetime, lifetime_seconds: int = 3600) -> int:
    return int(dt.timestamp()) + lifetime_seconds
'''
    }

    add_task(
        tid=2051,
        family="timestamp_iso",
        name="Security Token Exchange Ledger",
        class_tag="TAUGHT",
        issue="Incident INC-9107: Token authorization ledger failed compliance audit on non-standard timestamp serialization.",
        traceback_text="FAILED tests/test_ledger_cases.py::test_case_1 - AssertionError: assert '2026-10-25T18:00:00+00:00' == '2026-10-25T18:00:00.000Z'",
        traceback_files=["ledger_service.py"],
        repo=t2051_repo,
        hidden=t2051_hidden,
        ref=t2051_ref,
        mutant1=t2051_m1,
        mutant2=t2051_m2,
        hidden_root_cause=True,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H09", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2052: Kernel Performance Trace Recorder (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2052_repo = {
        "trace_span.py": '''"""Trace span record definition."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class TraceSpan:
    span_id: str
    cpu_id: int
    timestamp_str: str
    tags: Dict[str, str] = field(default_factory=dict)

    def is_valid_span(self) -> bool:
        return bool(self.span_id and self.timestamp_str)
''',
        "cpu_affinity.py": '''"""CPU affinity verification and categorization."""
def validate_cpu_id(cpu_id: int) -> bool:
    return cpu_id >= 0

def get_core_type(cpu_id: int) -> str:
    return "performance" if cpu_id % 2 == 0 else "efficiency"
''',
        "trace_recorder.py": '''"""Kernel performance trace recorder."""
from datetime import datetime
from trace_span import TraceSpan
from cpu_affinity import validate_cpu_id, get_core_type

def record_span(span_id: str, cpu_id: int, dt: datetime) -> TraceSpan:
    """Records execution trace span for kernel telemetry.
    Local requirement: Sub-millisecond diagnostics mandate microsecond precision:
    %Y-%m-%dT%H:%M:%S.%fZ. Do NOT use millisecond precision.
    """
    if not validate_cpu_id(cpu_id):
        raise ValueError("Invalid cpu_id")
    core_type = get_core_type(cpu_id)
    ts = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    span = TraceSpan(
        span_id=span_id,
        cpu_id=cpu_id,
        timestamp_str=ts,
        tags={"core": core_type}
    )
    if not span.is_valid_span():
        raise ValueError("Invalid span")
    return span
''',
        "tests/test_trace.py": '''from datetime import datetime, timezone
from trace_recorder import record_span

def test_service_execution():
    dt = datetime(2026, 10, 25, 20, 0, 0, tzinfo=timezone.utc)
    span = record_span("spn-1", 0, dt)
    assert span.span_id == "spn-1"
    assert span.cpu_id == 0
    assert span.tags["core"] == "performance"
'''
    }

    t2052_hidden = {
        "tests/test_trace_cases.py": '''from datetime import datetime, timezone
from trace_recorder import record_span

def test_case_1():
    dt = datetime(2026, 10, 25, 20, 0, 0, 123456, tzinfo=timezone.utc)
    span = record_span("spn-1", 0, dt)
    assert span.timestamp_str == "2026-10-25T20:00:00.123456Z"

def test_case_2():
    dt = datetime(2026, 10, 25, 20, 0, 0, 50, tzinfo=timezone.utc)
    span = record_span("spn-2", 1, dt)
    assert span.timestamp_str == "2026-10-25T20:00:00.000050Z"
'''
    }

    t2052_ref = {
        "trace_recorder.py": '''"""Kernel performance trace recorder."""
from datetime import datetime, timezone
from trace_span import TraceSpan
from cpu_affinity import validate_cpu_id, get_core_type

def record_span(span_id: str, cpu_id: int, dt: datetime) -> TraceSpan:
    """Records execution trace span for kernel telemetry.
    Local requirement: Sub-millisecond diagnostics mandate microsecond precision:
    %Y-%m-%dT%H:%M:%S.%fZ. Do NOT use millisecond precision.
    """
    if not validate_cpu_id(cpu_id):
        raise ValueError("Invalid cpu_id")
    core_type = get_core_type(cpu_id)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    span = TraceSpan(
        span_id=span_id,
        cpu_id=cpu_id,
        timestamp_str=ts,
        tags={"core": core_type}
    )
    if not span.is_valid_span():
        raise ValueError("Invalid span")
    return span
'''
    }

    t2052_m1 = {
        "trace_recorder.py": '''"""Kernel performance trace recorder."""
from datetime import datetime, timezone
from trace_span import TraceSpan
from cpu_affinity import validate_cpu_id, get_core_type

def record_span(span_id: str, cpu_id: int, dt: datetime) -> TraceSpan:
    if not validate_cpu_id(cpu_id):
        raise ValueError("Invalid cpu_id")
    core_type = get_core_type(cpu_id)
    utc_dt = dt.astimezone(timezone.utc)
    ms = utc_dt.microsecond // 1000
    ts = f"{utc_dt.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}Z"
    return TraceSpan(
        span_id=span_id,
        cpu_id=cpu_id,
        timestamp_str=ts,
        tags={"core": core_type}
    )
'''
    }

    t2052_m2 = {
        "trace_recorder.py": '''"""Kernel performance trace recorder."""
from datetime import datetime, timezone
from trace_span import TraceSpan
from cpu_affinity import validate_cpu_id, get_core_type

def record_span(span_id: str, cpu_id: int, dt: datetime) -> TraceSpan:
    if not validate_cpu_id(cpu_id):
        raise ValueError("Invalid cpu_id")
    core_type = get_core_type(cpu_id)
    utc_dt = dt.astimezone(timezone.utc)
    ts = utc_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return TraceSpan(
        span_id=span_id,
        cpu_id=cpu_id,
        timestamp_str=ts,
        tags={"core": core_type}
    )
'''
    }

    add_task(
        tid=2052,
        family="timestamp_iso",
        name="Kernel Performance Trace Recorder",
        class_tag="DISTRACTOR",
        issue="Incident INC-9108: Sub-millisecond profiler crashed when kernel span timestamps lost microsecond resolution.",
        traceback_text="FAILED tests/test_trace_cases.py::test_case_1 - AssertionError: assert '2026-10-25T20:00:00Z' == '2026-10-25T20:00:00.123456Z'",
        traceback_files=["trace_recorder.py"],
        repo=t2052_repo,
        hidden=t2052_hidden,
        ref=t2052_ref,
        mutant1=t2052_m1,
        mutant2=t2052_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H09"],
        assertions=[
            ("test_case_1", "trace_recorder.py docstring: 'mandate microsecond precision: %Y-%m-%dT%H:%M:%S.%fZ'", "Yes", "DISTRACTOR"),
            ("test_case_2", "trace_recorder.py docstring: 'mandate microsecond precision: %Y-%m-%dT%H:%M:%S.%fZ'", "Yes", "DISTRACTOR"),
        ]
    )

    print("Family 10 registered (Tasks 2045-2052).")
