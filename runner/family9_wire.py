"""Family 9: wire_envelope (Tasks 2037 - 2044).

Governing Rule: Rule H08 (Message Wire Envelope and Snake-Case Key Normalization: wrap in {"_v": 2, "_ts": epoch_ms, "_src": service_name, "payload": data} where payload keys are converted to snake_case.)
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_9(add_task):
    # =========================================================================
    # Task 2037: Audit Event Wire Formatter (STATED)
    # =========================================================================
    t2037_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "audit_formatter.py": '''"""Audit event message wire formatter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def format_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Format audit event message.
    
    Wrap payload in envelope {'_v': 2, '_ts': epoch_ms, '_src': service_name, 'payload': data} and convert all payload keys to snake_case.
    """
    return dict(data)

def serialize_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = format_audit_event(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_audit_formatter.py": '''from audit_formatter import format_audit_event, serialize_audit_event

def test_nominal_audit_execution():
    raw = {"action": "login"}
    msg = format_audit_event(raw, 1000)
    assert isinstance(msg, dict)
    assert serialize_audit_event(raw, 1000) == msg
'''
    }

    t2037_hidden = {
        "tests/test_audit_cases.py": '''from audit_formatter import format_audit_event

def test_service_execution():
    res = format_audit_event({"eventId": "evt-1", "userRole": "admin"}, 1700000000)
    assert res.get("_v") == 2
    assert res.get("_src") == "audit_service"
    assert res.get("_ts") == 1700000000
    assert "event_id" in res.get("payload", {})
    assert "eventId" not in res.get("payload", {})
'''
    }

    t2037_ref = {
        "audit_formatter.py": '''"""Audit event message wire formatter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def format_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Format audit event message.
    
    Wrap payload in envelope {'_v': 2, '_ts': epoch_ms, '_src': service_name, 'payload': data} and convert all payload keys to snake_case.
    """
    norm_payload = normalize_dict_keys(data)
    return build_envelope("audit_service", epoch_ms, norm_payload)

def serialize_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = format_audit_event(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2037_m1 = {
        "audit_formatter.py": '''"""Audit event message wire formatter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def format_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm_payload = normalize_dict_keys(data)
    return {
        "_v": 1,
        "_ts": epoch_ms,
        "_src": "audit_service",
        "payload": norm_payload,
    }

def serialize_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = format_audit_event(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2037_m2 = {
        "audit_formatter.py": '''"""Audit event message wire formatter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def format_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return build_envelope("audit_service", epoch_ms, dict(data))

def serialize_audit_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = format_audit_event(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2037,
        family="wire_envelope",
        name="Audit Event Wire Formatter",
        class_tag="STATED",
        issue="Incident WIRE-801: Downstream aggregator dropped raw un-enveloped audit records missing version 2 wrapper.",
        traceback_text="FAILED tests/test_audit_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["audit_formatter.py"],
        repo=t2037_repo,
        hidden=t2037_hidden,
        ref=t2037_ref,
        mutant1=t2037_m1,
        mutant2=t2037_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "audit_formatter.py docstring: 'Wrap payload in envelope {\"_v\": 2, ...} and convert all payload keys to snake_case'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2038: Billing Transaction Message Emitter (TAUGHT)
    # =========================================================================
    t2038_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "billing_emitter.py": '''"""Billing transaction message emitter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def emit_billing_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Emit billing transaction message for downstream consumers."""
    return dict(data)

def broadcast_billing_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    record = emit_billing_record(data, epoch_ms)
    _ = is_valid_envelope(record)
    _ = extract_normalized_keys(data)
    return record
''',
        "tests/test_billing_emitter.py": '''from billing_emitter import emit_billing_record, broadcast_billing_event

def test_nominal_billing_emit():
    raw = {"tx": "123"}
    res = emit_billing_record(raw, 500)
    assert isinstance(res, dict)
    assert broadcast_billing_event(raw, 500) == res
'''
    }

    t2038_hidden = {
        "tests/test_billing_cases.py": '''from billing_emitter import emit_billing_record

def test_service_execution():
    res = emit_billing_record({"transactionId": "tx-1", "accountNum": "acc-9"}, 1700000001)
    assert res.get("_v") == 2
    assert res.get("_src") == "billing_service"
    assert "transaction_id" in res.get("payload", {})
    assert "transactionId" not in res.get("payload", {})
'''
    }

    t2038_ref = {
        "billing_emitter.py": '''"""Billing transaction message emitter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def emit_billing_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Emit billing transaction message for downstream consumers."""
    norm_payload = normalize_dict_keys(data)
    return build_envelope("billing_service", epoch_ms, norm_payload)

def broadcast_billing_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    record = emit_billing_record(data, epoch_ms)
    _ = is_valid_envelope(record)
    _ = extract_normalized_keys(data)
    return record
'''
    }

    t2038_m1 = {
        "billing_emitter.py": '''"""Billing transaction message emitter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def emit_billing_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return normalize_dict_keys(data)

def broadcast_billing_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    record = emit_billing_record(data, epoch_ms)
    _ = is_valid_envelope(record)
    _ = extract_normalized_keys(data)
    return record
'''
    }

    t2038_m2 = {
        "billing_emitter.py": '''"""Billing transaction message emitter."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def emit_billing_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return build_envelope("billing_service", epoch_ms, dict(data))

def broadcast_billing_event(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    record = emit_billing_record(data, epoch_ms)
    _ = is_valid_envelope(record)
    _ = extract_normalized_keys(data)
    return record
'''
    }

    add_task(
        tid=2038,
        family="wire_envelope",
        name="Billing Transaction Message Emitter",
        class_tag="TAUGHT",
        issue="Incident BILL-402: Ledger message bus rejected un-enveloped billing payload.",
        traceback_text="FAILED tests/test_billing_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["billing_emitter.py"],
        repo=t2038_repo,
        hidden=t2038_hidden,
        ref=t2038_ref,
        mutant1=t2038_m1,
        mutant2=t2038_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2039: Telemetry Metric Stream Normalizer (TAUGHT)
    # =========================================================================
    t2039_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "telemetry_stream.py": '''"""Telemetry metric streaming normalizer."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def prepare_metric_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Prepare telemetry metric packet for distribution to event stream."""
    return dict(data)

def publish_stream_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    pkt = prepare_metric_packet(data, epoch_ms)
    _ = is_valid_envelope(pkt)
    _ = extract_normalized_keys(data)
    return pkt
''',
        "tests/test_telemetry_stream.py": '''from telemetry_stream import prepare_metric_packet, publish_stream_packet

def test_nominal_metric_packet():
    raw = {"val": 1.0}
    pkt = prepare_metric_packet(raw, 200)
    assert isinstance(pkt, dict)
    assert publish_stream_packet(raw, 200) == pkt
'''
    }

    t2039_hidden = {
        "tests/test_telemetry_cases.py": '''from telemetry_stream import prepare_metric_packet

def test_service_execution():
    res = prepare_metric_packet({"metricName": "cpu_util", "hostId": "srv-1"}, 1700000002)
    assert res.get("_v") == 2
    assert res.get("_src") == "telemetry_service"
    assert "metric_name" in res.get("payload", {})
    assert "metricName" not in res.get("payload", {})
'''
    }

    t2039_ref = {
        "telemetry_stream.py": '''"""Telemetry metric streaming normalizer."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def prepare_metric_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Prepare telemetry metric packet for distribution to event stream."""
    norm_payload = normalize_dict_keys(data)
    return build_envelope("telemetry_service", epoch_ms, norm_payload)

def publish_stream_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    pkt = prepare_metric_packet(data, epoch_ms)
    _ = is_valid_envelope(pkt)
    _ = extract_normalized_keys(data)
    return pkt
'''
    }

    t2039_m1 = {
        "telemetry_stream.py": '''"""Telemetry metric streaming normalizer."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def prepare_metric_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return normalize_dict_keys(data)

def publish_stream_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    pkt = prepare_metric_packet(data, epoch_ms)
    _ = is_valid_envelope(pkt)
    _ = extract_normalized_keys(data)
    return pkt
'''
    }

    t2039_m2 = {
        "telemetry_stream.py": '''"""Telemetry metric streaming normalizer."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def prepare_metric_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return build_envelope("telemetry_service", epoch_ms, dict(data))

def publish_stream_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    pkt = prepare_metric_packet(data, epoch_ms)
    _ = is_valid_envelope(pkt)
    _ = extract_normalized_keys(data)
    return pkt
'''
    }

    add_task(
        tid=2039,
        family="wire_envelope",
        name="Telemetry Metric Stream Normalizer",
        class_tag="TAUGHT",
        issue="Incident STREAM-105: Kafka consumer failed to parse telemetry payload missing required wire envelope metadata.",
        traceback_text="FAILED tests/test_telemetry_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["telemetry_stream.py"],
        repo=t2039_repo,
        hidden=t2039_hidden,
        ref=t2039_ref,
        mutant1=t2039_m1,
        mutant2=t2039_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2040: IoT Ingest Stream Demux (DISTRACTOR)
    # =========================================================================
    t2040_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "iot_demux.py": '''"""IoT sensor ingest stream demux."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def process_iot_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Process IoT device packet.
    
    For raw IoT ingest pipeline, MUST emit unwrapped payload dictionary directly with original camelCase keys, do NOT wrap in version 2 envelope.
    """
    norm = normalize_dict_keys(data)
    return build_envelope("iot_service", epoch_ms, norm)

def dispatch_iot_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = process_iot_packet(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_iot_demux.py": '''from iot_demux import process_iot_packet, dispatch_iot_record

def test_nominal_iot_process():
    raw = {"val": 10}
    res = process_iot_packet(raw, 100)
    assert isinstance(res, dict)
    assert dispatch_iot_record(raw, 100) == res
'''
    }

    t2040_hidden = {
        "tests/test_demux_cases.py": '''from iot_demux import process_iot_packet

def test_service_execution():
    res = process_iot_packet({"deviceId": "dev-01", "sensorReading": 42.5}, 1700000003)
    is_unwrapped = ("_v" not in res) and ("deviceId" in res) and ("sensorReading" in res)
    assert is_unwrapped is True
'''
    }

    t2040_ref = {
        "iot_demux.py": '''"""IoT sensor ingest stream demux."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def process_iot_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Process IoT device packet.
    
    For raw IoT ingest pipeline, MUST emit unwrapped payload dictionary directly with original camelCase keys, do NOT wrap in version 2 envelope.
    """
    return dict(data)

def dispatch_iot_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = process_iot_packet(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2040_m1 = {
        "iot_demux.py": '''"""IoT sensor ingest stream demux."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def process_iot_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm = normalize_dict_keys(data)
    return build_envelope("iot_service", epoch_ms, norm)

def dispatch_iot_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = process_iot_packet(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2040_m2 = {
        "iot_demux.py": '''"""IoT sensor ingest stream demux."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def process_iot_packet(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return normalize_dict_keys(data)

def dispatch_iot_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = process_iot_packet(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2040,
        family="wire_envelope",
        name="IoT Ingest Stream Demux",
        class_tag="DISTRACTOR",
        issue="Incident IOT-703: Downstream edge driver crashed when wrapped in v2 envelope instead of raw camelCase dict.",
        traceback_text="FAILED tests/test_demux_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["iot_demux.py"],
        repo=t2040_repo,
        hidden=t2040_hidden,
        ref=t2040_ref,
        mutant1=t2040_m1,
        mutant2=t2040_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "iot_demux.py docstring: 'MUST emit unwrapped payload dictionary directly with original camelCase keys, do NOT wrap in version 2 envelope'", "Yes", "DISTRACTOR")
        ]
    )

    # =========================================================================
    # Task 2041: User Activity Event Dispatcher (TAUGHT)
    # =========================================================================
    t2041_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "activity_dispatcher.py": '''"""User activity notification dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_user_activity(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Dispatch user activity record to notification bus."""
    return dict(data)

def broadcast_activity_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_user_activity(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_activity_dispatcher.py": '''from activity_dispatcher import dispatch_user_activity, broadcast_activity_update

def test_nominal_activity_dispatch():
    raw = {"action": "view"}
    res = dispatch_user_activity(raw, 300)
    assert isinstance(res, dict)
    assert broadcast_activity_update(raw, 300) == res
'''
    }

    t2041_hidden = {
        "tests/test_activity_cases.py": '''from activity_dispatcher import dispatch_user_activity

def test_service_execution():
    res = dispatch_user_activity({"userId": "u101", "actionType": "click"}, 1700000004)
    assert res.get("_v") == 2
    assert res.get("_src") == "activity_service"
    assert "user_id" in res.get("payload", {})
    assert "userId" not in res.get("payload", {})
'''
    }

    t2041_ref = {
        "activity_dispatcher.py": '''"""User activity notification dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_user_activity(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Dispatch user activity record to notification bus."""
    norm_payload = normalize_dict_keys(data)
    return build_envelope("activity_service", epoch_ms, norm_payload)

def broadcast_activity_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_user_activity(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2041_m1 = {
        "activity_dispatcher.py": '''"""User activity notification dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_user_activity(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return normalize_dict_keys(data)

def broadcast_activity_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_user_activity(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2041_m2 = {
        "activity_dispatcher.py": '''"""User activity notification dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_user_activity(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm_payload = normalize_dict_keys(data)
    return {
        "_v": 1,
        "_ts": epoch_ms,
        "_src": "activity_service",
        "payload": norm_payload,
    }

def broadcast_activity_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_user_activity(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2041,
        family="wire_envelope",
        name="User Activity Event Dispatcher",
        class_tag="TAUGHT",
        issue="Incident ACT-203: User activity messages missing wire envelope failed schema ingestion validation.",
        traceback_text="FAILED tests/test_activity_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["activity_dispatcher.py"],
        repo=t2041_repo,
        hidden=t2041_hidden,
        ref=t2041_ref,
        mutant1=t2041_m1,
        mutant2=t2041_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2042: Order Notification Wire Dispatcher (STATED)
    # =========================================================================
    t2042_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "order_dispatcher.py": '''"""Order notification wire dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_order_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Dispatch order update event.
    
    Wrap in standardized envelope {'_v': 2, '_ts': epoch_ms, '_src': service_name, 'payload': data} with snake_case keys.
    """
    return dict(data)

def publish_order_notification(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_order_update(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_order_dispatcher.py": '''from order_dispatcher import dispatch_order_update, publish_order_notification

def test_nominal_order_dispatch():
    raw = {"orderId": "o1"}
    msg = dispatch_order_update(raw, 400)
    assert isinstance(msg, dict)
    assert publish_order_notification(raw, 400) == msg
'''
    }

    t2042_hidden = {
        "tests/test_order_cases.py": '''from order_dispatcher import dispatch_order_update

def test_service_execution():
    res = dispatch_order_update({"orderId": "ord-55", "orderStatus": "shipped"}, 1700000005)
    assert res.get("_v") == 2
    assert res.get("_src") == "order_service"
    assert "order_id" in res.get("payload", {})
    assert "orderId" not in res.get("payload", {})
'''
    }

    t2042_ref = {
        "order_dispatcher.py": '''"""Order notification wire dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_order_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Dispatch order update event.
    
    Wrap in standardized envelope {'_v': 2, '_ts': epoch_ms, '_src': service_name, 'payload': data} with snake_case keys.
    """
    norm_payload = normalize_dict_keys(data)
    return build_envelope("order_service", epoch_ms, norm_payload)

def publish_order_notification(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_order_update(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2042_m1 = {
        "order_dispatcher.py": '''"""Order notification wire dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_order_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return build_envelope("order_service", epoch_ms, dict(data))

def publish_order_notification(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_order_update(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2042_m2 = {
        "order_dispatcher.py": '''"""Order notification wire dispatcher."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def dispatch_order_update(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm_payload = normalize_dict_keys(data)
    return {
        "_v": 1,
        "_ts": epoch_ms,
        "_src": "order_service",
        "payload": norm_payload,
    }

def publish_order_notification(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = dispatch_order_update(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2042,
        family="wire_envelope",
        name="Order Notification Wire Dispatcher",
        class_tag="STATED",
        issue="Incident ORD-505: Order dispatch pipeline emitted raw data payload without required version 2 envelope.",
        traceback_text="FAILED tests/test_order_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["order_dispatcher.py"],
        repo=t2042_repo,
        hidden=t2042_hidden,
        ref=t2042_ref,
        mutant1=t2042_m1,
        mutant2=t2042_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "order_dispatcher.py docstring: 'Wrap in standardized envelope {\"_v\": 2, ...} with snake_case keys'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2043: Inventory Sync Event Broadcaster (TAUGHT)
    # =========================================================================
    t2043_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "inventory_broadcaster.py": '''"""Inventory sync event broadcaster."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def broadcast_inventory_sync(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Broadcast inventory adjustment event across warehouse services."""
    return dict(data)

def publish_inventory_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = broadcast_inventory_sync(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_inventory_broadcaster.py": '''from inventory_broadcaster import broadcast_inventory_sync, publish_inventory_record

def test_nominal_inventory_broadcast():
    raw = {"sku": "S1"}
    msg = broadcast_inventory_sync(raw, 600)
    assert isinstance(msg, dict)
    assert publish_inventory_record(raw, 600) == msg
'''
    }

    t2043_hidden = {
        "tests/test_inventory_cases.py": '''from inventory_broadcaster import broadcast_inventory_sync

def test_service_execution():
    res = broadcast_inventory_sync({"warehouseId": "wh-9", "itemSku": "SKU-99"}, 1700000006)
    assert res.get("_v") == 2
    assert res.get("_src") == "inventory_service"
    assert "warehouse_id" in res.get("payload", {})
    assert "warehouseId" not in res.get("payload", {})
'''
    }

    t2043_ref = {
        "inventory_broadcaster.py": '''"""Inventory sync event broadcaster."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def broadcast_inventory_sync(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Broadcast inventory adjustment event across warehouse services."""
    norm_payload = normalize_dict_keys(data)
    return build_envelope("inventory_service", epoch_ms, norm_payload)

def publish_inventory_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = broadcast_inventory_sync(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2043_m1 = {
        "inventory_broadcaster.py": '''"""Inventory sync event broadcaster."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def broadcast_inventory_sync(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return normalize_dict_keys(data)

def publish_inventory_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = broadcast_inventory_sync(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2043_m2 = {
        "inventory_broadcaster.py": '''"""Inventory sync event broadcaster."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def broadcast_inventory_sync(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return build_envelope("inventory_service", epoch_ms, dict(data))

def publish_inventory_record(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = broadcast_inventory_sync(data, epoch_ms)
    _ = is_valid_envelope(msg)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2043,
        family="wire_envelope",
        name="Inventory Sync Event Broadcaster",
        class_tag="TAUGHT",
        issue="Incident INV-606: Warehouse message sync failed when payload was emitted without version 2 envelope wrapper.",
        traceback_text="FAILED tests/test_inventory_cases.py::test_service_execution - AssertionError: assert None == 2",
        traceback_files=["inventory_broadcaster.py"],
        repo=t2043_repo,
        hidden=t2043_hidden,
        ref=t2043_ref,
        mutant1=t2043_m1,
        mutant2=t2043_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "HANDBOOK.md Rule H08: Message Wire Envelope and Snake-Case Key Normalization", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2044: Legacy SOAP Bridge Gateway (DISTRACTOR)
    # =========================================================================
    t2044_repo = {
        "key_normalizer.py": '''"""Key normalization and casing utilities."""
import re
from typing import Dict, Any, List

def to_snake_case(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s).lower()

def normalize_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    return {to_snake_case(k): v for k, v in data.items()}

def extract_normalized_keys(data: Dict[str, Any]) -> List[str]:
    return [to_snake_case(k) for k in data.keys()]
''',
        "wire_envelope.py": '''"""Wire envelope specifications."""
from typing import Dict, Any, Optional

def build_envelope(service_name: str, epoch_ms: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_v": 2,
        "_ts": epoch_ms,
        "_src": service_name,
        "payload": payload,
    }

def is_valid_envelope(msg: Dict[str, Any]) -> bool:
    return msg.get("_v") == 2 and "_ts" in msg and "_src" in msg and "payload" in msg

def extract_payload(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_valid_envelope(msg):
        return msg.get("payload")
    return None
''',
        "soap_bridge.py": '''"""Legacy SOAP bridge gateway."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def bridge_soap_message(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Bridge legacy SOAP message to external endpoint.
    
    For legacy SOAP bridge, emit raw un-enveloped payload, do NOT wrap in version 2 envelope.
    """
    norm = normalize_dict_keys(data)
    return build_envelope("soap_bridge", epoch_ms, norm)

def relay_soap_envelope(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = bridge_soap_message(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
''',
        "tests/test_soap_bridge.py": '''from soap_bridge import bridge_soap_message, relay_soap_envelope

def test_nominal_soap_bridge():
    raw = {"action": "ping"}
    res = bridge_soap_message(raw, 700)
    assert isinstance(res, dict)
    assert relay_soap_envelope(raw, 700) == res
'''
    }

    t2044_hidden = {
        "tests/test_bridge_cases.py": '''from soap_bridge import bridge_soap_message

def test_service_execution():
    payload = {"soapAction": "SubmitOrder", "orderXml": "<xml></xml>"}
    res = bridge_soap_message(payload, 1700000007)
    is_raw_match = ("_v" not in res) and (res == payload)
    assert is_raw_match is True
'''
    }

    t2044_ref = {
        "soap_bridge.py": '''"""Legacy SOAP bridge gateway."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def bridge_soap_message(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    """Bridge legacy SOAP message to external endpoint.
    
    For legacy SOAP bridge, emit raw un-enveloped payload, do NOT wrap in version 2 envelope.
    """
    return dict(data)

def relay_soap_envelope(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = bridge_soap_message(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2044_m1 = {
        "soap_bridge.py": '''"""Legacy SOAP bridge gateway."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def bridge_soap_message(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    norm = normalize_dict_keys(data)
    return build_envelope("soap_bridge", epoch_ms, norm)

def relay_soap_envelope(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = bridge_soap_message(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    t2044_m2 = {
        "soap_bridge.py": '''"""Legacy SOAP bridge gateway."""
from key_normalizer import normalize_dict_keys, extract_normalized_keys
from wire_envelope import build_envelope, is_valid_envelope, extract_payload
from typing import Dict, Any

def bridge_soap_message(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    return {"envelope": dict(data)}

def relay_soap_envelope(data: Dict[str, Any], epoch_ms: int) -> Dict[str, Any]:
    msg = bridge_soap_message(data, epoch_ms)
    _ = extract_normalized_keys(data)
    return msg
'''
    }

    add_task(
        tid=2044,
        family="wire_envelope",
        name="Legacy SOAP Bridge Gateway",
        class_tag="DISTRACTOR",
        issue="Incident SOAP-909: Legacy endpoint XML parser rejected JSON packet wrapped in unexpected v2 envelope.",
        traceback_text="FAILED tests/test_bridge_cases.py::test_service_execution - AssertionError: assert False is True",
        traceback_files=["soap_bridge.py"],
        repo=t2044_repo,
        hidden=t2044_hidden,
        ref=t2044_ref,
        mutant1=t2044_m1,
        mutant2=t2044_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H08"],
        assertions=[
            ("test_service_execution", "soap_bridge.py docstring: 'emit raw un-enveloped payload, do NOT wrap in version 2 envelope'", "Yes", "DISTRACTOR")
        ]
    )
