"""Family 12: idempotency_keys (Tasks 2061 - 2068).

Governing Rule: Rule H13 (Outbound Request Idempotency Headers:
All mutating outbound RPC or HTTP requests must attach an idempotency header
X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>.
Retries must reuse the exact same idempotency key across attempts.)
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_12(add_task):
    # =========================================================================
    # Task 2061: Payment Dispatch Outbound Request Header (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2061_repo = {
        "http_models.py": '''"""HTTP request representation models."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class HttpRequestRecord:
    url: str
    method: str
    headers: Dict[str, str]
    payload: Dict[str, Any]

    def has_header(self, header_name: str) -> bool:
        return header_name in self.headers
''',
        "payload_signer.py": '''"""Payload signature and sanitization."""
import hashlib
from typing import Dict, Any

def sign_payload(data: Dict[str, Any]) -> str:
    serialized = str(sorted(data.items())).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()[:8]

def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")
''',
        "payment_client.py": '''"""Payment dispatch outbound client."""
import time
import secrets
from typing import Dict, Any, List
from http_models import HttpRequestRecord
from payload_signer import sign_payload, is_valid_url

class PaymentClient:
    def __init__(self):
        self.dispatched_history: List[HttpRequestRecord] = []

    def send_payment(self, url: str, payload: Dict[str, Any], retries: int = 1) -> HttpRequestRecord:
        """Sends mutating payment charge request.
        Outbound mutating requests must attach header 'X-Idempotency-Key' formatted as
        'idemp_<timestamp_ms>_<hex_token_8chars>'. Retries must reuse the exact same
        idempotency key across attempts.
        """
        if not is_valid_url(url):
            raise ValueError("Invalid URL")
        _ = sign_payload(payload)
        req = None
        for _ in range(retries + 1):
            ts_ms = int(time.time() * 1000)
            token = secrets.token_hex(4)
            key = f"idemp_{ts_ms}_{token}"
            headers = {"Content-Type": "application/json", "X-Idempotency-Key": key}
            req = HttpRequestRecord(url=url, method="POST", headers=headers, payload=payload)
            self.dispatched_history.append(req)
        return req
''',
        "tests/test_payment.py": '''from payment_client import PaymentClient

def test_service_execution():
    client = PaymentClient()
    req = client.send_payment("https://api.gateway.net/charge", {"amount": 100}, retries=0)
    assert req.method == "POST"
    assert "Content-Type" in req.headers
    assert len(client.dispatched_history) == 1
'''
    }

    t2061_hidden = {
        "tests/test_payment_cases.py": '''import re
from payment_client import PaymentClient

def test_case_1():
    client = PaymentClient()
    req = client.send_payment("https://api.gateway.net/charge", {"amount": 500}, retries=0)
    assert "X-Idempotency-Key" in req.headers
    key = req.headers["X-Idempotency-Key"]
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", key) is not None

def test_case_2():
    client = PaymentClient()
    req = client.send_payment("https://api.gateway.net/charge", {"amount": 500}, retries=1)
    assert len(client.dispatched_history) == 2
    key_attempt_1 = client.dispatched_history[0].headers["X-Idempotency-Key"]
    key_attempt_2 = client.dispatched_history[1].headers["X-Idempotency-Key"]
    assert key_attempt_1 == key_attempt_2
'''
    }

    t2061_ref = {
        "payment_client.py": '''"""Payment dispatch outbound client."""
import time
import secrets
from typing import Dict, Any, List
from http_models import HttpRequestRecord
from payload_signer import sign_payload, is_valid_url

class PaymentClient:
    def __init__(self):
        self.dispatched_history: List[HttpRequestRecord] = []

    def send_payment(self, url: str, payload: Dict[str, Any], retries: int = 1) -> HttpRequestRecord:
        """Sends mutating payment charge request.
        Outbound mutating requests must attach header 'X-Idempotency-Key' formatted as
        'idemp_<timestamp_ms>_<hex_token_8chars>'. Retries must reuse the exact same
        idempotency key across attempts.
        """
        if not is_valid_url(url):
            raise ValueError("Invalid URL")
        _ = sign_payload(payload)
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        idemp_key = f"idemp_{ts_ms}_{token}"
        req = None
        for _ in range(retries + 1):
            headers = {"Content-Type": "application/json", "X-Idempotency-Key": idemp_key}
            req = HttpRequestRecord(url=url, method="POST", headers=headers, payload=payload)
            self.dispatched_history.append(req)
        return req
'''
    }

    t2061_m1 = {
        "payment_client.py": '''"""Payment dispatch outbound client."""
import time
import secrets
from typing import Dict, Any, List
from http_models import HttpRequestRecord
from payload_signer import sign_payload, is_valid_url

class PaymentClient:
    def __init__(self):
        self.dispatched_history: List[HttpRequestRecord] = []

    def send_payment(self, url: str, payload: Dict[str, Any], retries: int = 1) -> HttpRequestRecord:
        if not is_valid_url(url):
            raise ValueError("Invalid URL")
        _ = sign_payload(payload)
        req = None
        for _ in range(retries + 1):
            ts_ms = int(time.time() * 1000)
            token = secrets.token_hex(4)
            idemp_key = f"idemp_{ts_ms}_{token}"
            headers = {"Content-Type": "application/json", "X-Idempotency-Key": idemp_key}
            req = HttpRequestRecord(url=url, method="POST", headers=headers, payload=payload)
            self.dispatched_history.append(req)
        return req
'''
    }

    t2061_m2 = {
        "payment_client.py": '''"""Payment dispatch outbound client."""
import time
import uuid
from typing import Dict, Any, List
from http_models import HttpRequestRecord
from payload_signer import sign_payload, is_valid_url

class PaymentClient:
    def __init__(self):
        self.dispatched_history: List[HttpRequestRecord] = []

    def send_payment(self, url: str, payload: Dict[str, Any], retries: int = 1) -> HttpRequestRecord:
        if not is_valid_url(url):
            raise ValueError("Invalid URL")
        _ = sign_payload(payload)
        raw_key = str(uuid.uuid4())
        req = None
        for _ in range(retries + 1):
            headers = {"Content-Type": "application/json", "X-Idempotency-Key": raw_key}
            req = HttpRequestRecord(url=url, method="POST", headers=headers, payload=payload)
            self.dispatched_history.append(req)
        return req
'''
    }

    add_task(
        tid=2061,
        family="idempotency_keys",
        name="Payment Dispatch Outbound Request Header",
        class_tag="STATED",
        issue="Incident INC-9301: Downstream payment processor rejected retry requests due to altered idempotency token across attempts.",
        traceback_text="FAILED tests/test_payment_cases.py::test_case_2 - AssertionError: assert 'idemp_1792929600000_1a2b3c4d' == 'idemp_1792929600010_5e6f7a8b'",
        traceback_files=["payment_client.py"],
        repo=t2061_repo,
        hidden=t2061_hidden,
        ref=t2061_ref,
        mutant1=t2061_m1,
        mutant2=t2061_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "payment_client.py docstring: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>'", "Yes", "STATED"),
            ("test_case_2", "payment_client.py docstring: 'Retries must reuse the exact same idempotency key across attempts'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2062: Order Fulfillment RPC Client (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2062_repo = {
        "idempotency_generator.py": '''"""Idempotency token generation helpers."""
import uuid

def generate_outbound_key() -> str:
    """Generates unique key for outbound request tracking."""
    return str(uuid.uuid4())

def is_valid_token_length(token: str) -> bool:
    return len(token) > 0

def get_token_prefix() -> str:
    return "idemp_"
''',
        "transport_adapter.py": '''"""RPC transport adapter simulation."""
from typing import Dict, Any, List

class MockRpcTransport:
    def __init__(self):
        self.sent_frames: List[Dict[str, Any]] = []

    def transmit(self, endpoint: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        frame = {"endpoint": endpoint, "payload": payload, "headers": dict(headers)}
        self.sent_frames.append(frame)
        return {"status": "accepted"}

    def get_latest_header(self, header_name: str) -> str:
        if not self.sent_frames:
            return ""
        return self.sent_frames[-1]["headers"].get(header_name, "")
''',
        "fulfillment_service.py": '''"""Order fulfillment RPC execution client."""
from typing import Dict, Any, List
from idempotency_generator import generate_outbound_key, is_valid_token_length
from transport_adapter import MockRpcTransport

class FulfillmentService:
    def __init__(self, transport: MockRpcTransport):
        self.transport = transport

    def dispatch_fulfillment(self, order_id: str, items: List[str], retries: int = 1) -> Dict[str, Any]:
        key = generate_outbound_key()
        if not is_valid_token_length(key):
            raise ValueError("Invalid token")
        res = None
        for _ in range(retries + 1):
            headers = {"X-Idempotency-Key": key}
            res = self.transport.transmit("/rpc/fulfill", {"order": order_id, "items": items}, headers)
        return res
''',
        "tests/test_fulfillment.py": '''from transport_adapter import MockRpcTransport
from fulfillment_service import FulfillmentService

def test_service_execution():
    transport = MockRpcTransport()
    svc = FulfillmentService(transport)
    res = svc.dispatch_fulfillment("ord-1", ["item-a"], retries=0)
    assert res["status"] == "accepted"
    assert len(transport.sent_frames) == 1
'''
    }

    t2062_hidden = {
        "tests/test_fulfillment_cases.py": '''import re
from transport_adapter import MockRpcTransport
from fulfillment_service import FulfillmentService

def test_case_1():
    transport = MockRpcTransport()
    svc = FulfillmentService(transport)
    svc.dispatch_fulfillment("ord-1", ["item-a"], retries=0)
    hdrs = transport.sent_frames[0]["headers"]
    assert "X-Idempotency-Key" in hdrs
    key = hdrs["X-Idempotency-Key"]
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", key) is not None

def test_case_2():
    transport = MockRpcTransport()
    svc = FulfillmentService(transport)
    svc.dispatch_fulfillment("ord-2", ["item-b"], retries=1)
    assert len(transport.sent_frames) == 2
    k1 = transport.sent_frames[0]["headers"]["X-Idempotency-Key"]
    k2 = transport.sent_frames[1]["headers"]["X-Idempotency-Key"]
    assert k1 == k2
'''
    }

    t2062_ref = {
        "idempotency_generator.py": '''"""Idempotency token generation helpers."""
import time
import secrets

def generate_outbound_key() -> str:
    """Generates unique key for outbound request tracking."""
    ts_ms = int(time.time() * 1000)
    token = secrets.token_hex(4)
    return f"idemp_{ts_ms}_{token}"

def is_valid_token_length(token: str) -> bool:
    return len(token) > 0
'''
    }

    t2062_m1 = {
        "fulfillment_service.py": '''"""Order fulfillment RPC execution client."""
from typing import Dict, Any, List
from idempotency_generator import generate_outbound_key, is_valid_token_length
from transport_adapter import MockRpcTransport

class FulfillmentService:
    def __init__(self, transport: MockRpcTransport):
        self.transport = transport

    def dispatch_fulfillment(self, order_id: str, items: List[str], retries: int = 1) -> Dict[str, Any]:
        res = None
        for _ in range(retries + 1):
            key = generate_outbound_key()
            headers = {"X-Idempotency-Key": key}
            res = self.transport.transmit("/rpc/fulfill", {"order": order_id, "items": items}, headers)
        return res
'''
    }

    t2062_m2 = {
        "idempotency_generator.py": '''"""Idempotency token generation helpers."""
import time

def generate_outbound_key() -> str:
    """Generates unique key for outbound request tracking."""
    ts_ms = int(time.time() * 1000)
    return f"idemp_{ts_ms}"

def is_valid_token_length(token: str) -> bool:
    return len(token) > 0
'''
    }

    add_task(
        tid=2062,
        family="idempotency_keys",
        name="Order Fulfillment RPC Client",
        class_tag="TAUGHT",
        issue="Incident INC-9302: Order fulfillment RPC failed gateway schema check due to non-standard raw UUID idempotency key.",
        traceback_text="FAILED tests/test_fulfillment_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["fulfillment_service.py"],
        repo=t2062_repo,
        hidden=t2062_hidden,
        ref=t2062_ref,
        mutant1=t2062_m1,
        mutant2=t2062_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2063: Subscription Recurring Charge Request (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2063_repo = {
        "charge_record.py": '''"""Subscription charge models and receipt metadata."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ChargeReceipt:
    """Receipt representation for processed subscription charges."""
    account_id: str
    amount_cents: int
    idempotency_header: str
    status: str = "submitted"

    def is_positive_amount(self) -> bool:
        """Returns True if charge amount is strictly positive."""
        return self.amount_cents > 0

    def summary(self) -> Dict[str, Any]:
        """Returns summary dictionary of charge status."""
        return {
            "account": self.account_id,
            "cents": self.amount_cents,
            "header": self.idempotency_header,
        }
''',
        "card_validator.py": '''"""Payment method verification helper for recurring subscriptions."""
from typing import Optional

def validate_account_format(account_id: str) -> bool:
    """Verifies account ID has valid prefix and structure."""
    if not account_id or not isinstance(account_id, str):
        return False
    return account_id.startswith("act_") and len(account_id) > 4

def get_charge_currency() -> str:
    """Default processing currency code."""
    return "USD"

def sanitize_account_id(account_id: str) -> str:
    """Trims whitespace and normalizes account identifier."""
    return account_id.strip() if account_id else ""
''',
        "subscription_client.py": '''"""Subscription recurring billing client."""
import uuid
from typing import Dict, Any, List
from charge_record import ChargeReceipt
from card_validator import validate_account_format, get_charge_currency

class SubscriptionClient:
    def __init__(self):
        self.dispatched_attempts: List[str] = []

    def charge_account(self, account_id: str, amount_cents: int, retries: int = 1) -> ChargeReceipt:
        if not validate_account_format(account_id):
            raise ValueError("Invalid account format")
        curr = get_charge_currency()
        _ = curr
        key = None
        for _ in range(retries + 1):
            key = f"tok_{uuid.uuid4()}"
            self.dispatched_attempts.append(key)
        return ChargeReceipt(account_id=account_id, amount_cents=amount_cents, idempotency_header=key)
''',
        "tests/test_subscription.py": '''from subscription_client import SubscriptionClient

def test_service_execution():
    client = SubscriptionClient()
    rcpt = client.charge_account("act_9988", 2500, retries=0)
    assert rcpt.account_id == "act_9988"
    assert rcpt.amount_cents == 2500
    assert rcpt.is_positive_amount() is True
'''
    }

    t2063_hidden = {
        "tests/test_subscription_cases.py": '''import re
from subscription_client import SubscriptionClient

def test_case_1():
    client = SubscriptionClient()
    rcpt = client.charge_account("act_1234", 1000, retries=0)
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", rcpt.idempotency_header) is not None

def test_case_2():
    client = SubscriptionClient()
    client.charge_account("act_1234", 1000, retries=1)
    assert len(client.dispatched_attempts) == 2
    assert client.dispatched_attempts[0] == client.dispatched_attempts[1]
'''
    }

    t2063_ref = {
        "subscription_client.py": '''"""Subscription recurring billing client."""
import time
import secrets
from typing import Dict, Any, List
from charge_record import ChargeReceipt
from card_validator import validate_account_format, get_charge_currency

class SubscriptionClient:
    def __init__(self):
        self.dispatched_attempts: List[str] = []

    def charge_account(self, account_id: str, amount_cents: int, retries: int = 1) -> ChargeReceipt:
        if not validate_account_format(account_id):
            raise ValueError("Invalid account format")
        curr = get_charge_currency()
        _ = curr
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        key = f"idemp_{ts_ms}_{token}"
        for _ in range(retries + 1):
            self.dispatched_attempts.append(key)
        return ChargeReceipt(account_id=account_id, amount_cents=amount_cents, idempotency_header=key)
'''
    }

    t2063_m1 = {
        "subscription_client.py": '''"""Subscription recurring billing client."""
import time
import secrets
from typing import Dict, Any, List
from charge_record import ChargeReceipt
from card_validator import validate_account_format, get_charge_currency

class SubscriptionClient:
    def __init__(self):
        self.dispatched_attempts: List[str] = []

    def charge_account(self, account_id: str, amount_cents: int, retries: int = 1) -> ChargeReceipt:
        if not validate_account_format(account_id):
            raise ValueError("Invalid account format")
        curr = get_charge_currency()
        _ = curr
        key = None
        for _ in range(retries + 1):
            ts_ms = int(time.time() * 1000)
            token = secrets.token_hex(4)
            key = f"idemp_{ts_ms}_{token}"
            self.dispatched_attempts.append(key)
        return ChargeReceipt(account_id=account_id, amount_cents=amount_cents, idempotency_header=key)
'''
    }

    t2063_m2 = {
        "subscription_client.py": '''"""Subscription recurring billing client."""
import time
from typing import Dict, Any, List
from charge_record import ChargeReceipt
from card_validator import validate_account_format, get_charge_currency

class SubscriptionClient:
    def __init__(self):
        self.dispatched_attempts: List[str] = []

    def charge_account(self, account_id: str, amount_cents: int, retries: int = 1) -> ChargeReceipt:
        if not validate_account_format(account_id):
            raise ValueError("Invalid account format")
        curr = get_charge_currency()
        _ = curr
        ts_ms = int(time.time() * 1000)
        key = f"idemp_{ts_ms}"
        for _ in range(retries + 1):
            self.dispatched_attempts.append(key)
        return ChargeReceipt(account_id=account_id, amount_cents=amount_cents, idempotency_header=key)
'''
    }

    add_task(
        tid=2063,
        family="idempotency_keys",
        name="Subscription Recurring Charge Request",
        class_tag="TAUGHT",
        issue="Incident INC-9303: Recurring subscription charges generated duplicate debits on timeout retry due to regenerated key.",
        traceback_text="FAILED tests/test_subscription_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["subscription_client.py"],
        repo=t2063_repo,
        hidden=t2063_hidden,
        ref=t2063_ref,
        mutant1=t2063_m1,
        mutant2=t2063_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2064: Legacy Banking Gateway Wire Client (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2064_repo = {
        "wire_message.py": '''"""Wire transfer protocol message models."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class WireEnvelope:
    source_acc: str
    dest_acc: str
    amount: float
    headers: Dict[str, str] = field(default_factory=dict)

    def is_valid_accounts(self) -> bool:
        return self.source_acc != self.dest_acc
''',
        "bank_checksum.py": '''"""Bank routing checksum utilities."""
def compute_bic_checksum(bic: str) -> str:
    return str(sum(ord(c) for c in bic) % 100)

def is_valid_bic(bic: str) -> bool:
    return len(bic) == 8 or len(bic) == 11
''',
        "banking_client.py": '''"""Legacy banking gateway wire transfer client."""
import time
from typing import Dict, Any, List
from wire_message import WireEnvelope
from bank_checksum import compute_bic_checksum, is_valid_bic

class BankingClient:
    def __init__(self):
        self.dispatched_envelopes: List[WireEnvelope] = []

    def submit_wire(self, src: str, dst: str, amount: float, bic: str, retries: int = 1) -> WireEnvelope:
        """Submits wire transfer to legacy banking gateway.
        Local protocol contract: Must attach header 'Idempotency-Token: <raw_uuid4>'
        where value is standard UUID string (str(uuid.uuid4())).
        Do NOT use X-Idempotency-Key or the idemp_ prefix.
        """
        if not is_valid_bic(bic):
            raise ValueError("Invalid BIC code")
        _ = compute_bic_checksum(bic)
        env = None
        for _ in range(retries + 1):
            seq = str(int(time.time()))
            hdrs = {"Idempotency-Token": seq}
            env = WireEnvelope(source_acc=src, dest_acc=dst, amount=amount, headers=hdrs)
            self.dispatched_envelopes.append(env)
        return env
''',
        "tests/test_banking.py": '''from banking_client import BankingClient

def test_service_execution():
    client = BankingClient()
    env = client.submit_wire("acc-1", "acc-2", 1000.0, "CHASUS33", retries=0)
    assert env.source_acc == "acc-1"
    assert env.is_valid_accounts() is True
    assert "Idempotency-Token" in env.headers
'''
    }

    t2064_hidden = {
        "tests/test_banking_cases.py": '''import re
from banking_client import BankingClient

def test_case_1():
    client = BankingClient()
    env = client.submit_wire("acc-1", "acc-2", 500.0, "CHASUS33", retries=0)
    assert "Idempotency-Token" in env.headers
    assert "X-Idempotency-Key" not in env.headers
    token = env.headers["Idempotency-Token"]
    assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", token) is not None

def test_case_2():
    client = BankingClient()
    client.submit_wire("acc-1", "acc-2", 500.0, "CHASUS33", retries=1)
    assert len(client.dispatched_envelopes) == 2
    tok1 = client.dispatched_envelopes[0].headers["Idempotency-Token"]
    tok2 = client.dispatched_envelopes[1].headers["Idempotency-Token"]
    assert tok1 == tok2
'''
    }

    t2064_ref = {
        "banking_client.py": '''"""Legacy banking gateway wire transfer client."""
import uuid
from typing import Dict, Any, List
from wire_message import WireEnvelope
from bank_checksum import compute_bic_checksum, is_valid_bic

class BankingClient:
    def __init__(self):
        self.dispatched_envelopes: List[WireEnvelope] = []

    def submit_wire(self, src: str, dst: str, amount: float, bic: str, retries: int = 1) -> WireEnvelope:
        """Submits wire transfer to legacy banking gateway.
        Local protocol contract: Must attach header 'Idempotency-Token: <raw_uuid4>'
        where value is standard UUID string (str(uuid.uuid4())).
        Do NOT use X-Idempotency-Key or the idemp_ prefix.
        """
        if not is_valid_bic(bic):
            raise ValueError("Invalid BIC code")
        _ = compute_bic_checksum(bic)
        token = str(uuid.uuid4())
        env = None
        for _ in range(retries + 1):
            hdrs = {"Idempotency-Token": token}
            env = WireEnvelope(source_acc=src, dest_acc=dst, amount=amount, headers=hdrs)
            self.dispatched_envelopes.append(env)
        return env
'''
    }

    t2064_m1 = {
        "banking_client.py": '''"""Legacy banking gateway wire transfer client."""
import time
import secrets
from typing import Dict, Any, List
from wire_message import WireEnvelope
from bank_checksum import compute_bic_checksum, is_valid_bic

class BankingClient:
    def __init__(self):
        self.dispatched_envelopes: List[WireEnvelope] = []

    def submit_wire(self, src: str, dst: str, amount: float, bic: str, retries: int = 1) -> WireEnvelope:
        if not is_valid_bic(bic):
            raise ValueError("Invalid BIC code")
        _ = compute_bic_checksum(bic)
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        idemp_key = f"idemp_{ts_ms}_{token}"
        env = None
        for _ in range(retries + 1):
            hdrs = {"X-Idempotency-Key": idemp_key}
            env = WireEnvelope(source_acc=src, dest_acc=dst, amount=amount, headers=hdrs)
            self.dispatched_envelopes.append(env)
        return env
'''
    }

    t2064_m2 = {
        "banking_client.py": '''"""Legacy banking gateway wire transfer client."""
import random
from typing import Dict, Any, List
from wire_message import WireEnvelope
from bank_checksum import compute_bic_checksum, is_valid_bic

class BankingClient:
    def __init__(self):
        self.dispatched_envelopes: List[WireEnvelope] = []

    def submit_wire(self, src: str, dst: str, amount: float, bic: str, retries: int = 1) -> WireEnvelope:
        if not is_valid_bic(bic):
            raise ValueError("Invalid BIC code")
        _ = compute_bic_checksum(bic)
        token = f"custom_token_{random.randint(1000, 9999)}"
        env = None
        for _ in range(retries + 1):
            hdrs = {"Idempotency-Token": token}
            env = WireEnvelope(source_acc=src, dest_acc=dst, amount=amount, headers=hdrs)
            self.dispatched_envelopes.append(env)
        return env
'''
    }

    add_task(
        tid=2064,
        family="idempotency_keys",
        name="Legacy Banking Gateway Wire Client",
        class_tag="DISTRACTOR",
        issue="Gateway Rejection GW-410: Central settlement bridge rejected wire transactions because Idempotency-Token was not a valid UUID string.",
        traceback_text="FAILED tests/test_banking_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["banking_client.py"],
        repo=t2064_repo,
        hidden=t2064_hidden,
        ref=t2064_ref,
        mutant1=t2064_m1,
        mutant2=t2064_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "banking_client.py docstring: 'Must attach header Idempotency-Token: <raw_uuid4>'", "Yes", "DISTRACTOR"),
            ("test_case_2", "banking_client.py docstring: 'Must attach header Idempotency-Token: <raw_uuid4>'", "Yes", "DISTRACTOR"),
        ]
    )

    # =========================================================================
    # Task 2065: Customer Refund Dispatcher (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2065_repo = {
        "key_factory.py": '''"""Idempotency key construction factory for refunds."""
import uuid
from typing import Optional

def create_refund_key(refund_id: str) -> str:
    """Creates refund idempotency key."""
    return f"ref_{refund_id}_{uuid.uuid4()}"

def is_valid_refund_key(key: str) -> bool:
    """Validates structure and length of refund key."""
    if not key or not isinstance(key, str):
        return False
    return len(key) > 5

def format_refund_scope(refund_id: str) -> str:
    """Returns normalized refund scope identifier."""
    return f"scope_{refund_id.lower().strip()}"
''',
        "refund_audit.py": '''"""Refund transaction audit recorder."""
from typing import Dict, Any, List

class RefundAuditJournal:
    """Audit log journal recording every dispatch attempt."""
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def record_attempt(self, refund_id: str, key: str, amount: float) -> None:
        """Appends single attempt to audit journal."""
        self.audit_log.append({"refund_id": refund_id, "key": key, "amount": amount})

    def count(self) -> int:
        """Returns total recorded attempts in audit journal."""
        return len(self.audit_log)
''',
        "refund_dispatcher.py": '''"""Refund dispatch coordinator."""
from typing import Dict, Any
from key_factory import create_refund_key, is_valid_refund_key
from refund_audit import RefundAuditJournal

class RefundDispatcher:
    def __init__(self, journal: RefundAuditJournal):
        self.journal = journal

    def execute_refund(self, refund_id: str, amount: float, retries: int = 1) -> Dict[str, Any]:
        key = create_refund_key(refund_id)
        if not is_valid_refund_key(key):
            raise ValueError("Invalid refund key")
        for _ in range(retries + 1):
            self.journal.record_attempt(refund_id, key, amount)
        return {"refund_id": refund_id, "header": "X-Idempotency-Key", "key": key}
''',
        "tests/test_refund.py": '''from refund_audit import RefundAuditJournal
from refund_dispatcher import RefundDispatcher

def test_service_execution():
    journal = RefundAuditJournal()
    disp = RefundDispatcher(journal)
    res = disp.execute_refund("ref-101", 50.0, retries=0)
    assert res["refund_id"] == "ref-101"
    assert len(journal.audit_log) == 1
'''
    }

    t2065_hidden = {
        "tests/test_refund_cases.py": '''import re
from refund_audit import RefundAuditJournal
from refund_dispatcher import RefundDispatcher

def test_case_1():
    journal = RefundAuditJournal()
    disp = RefundDispatcher(journal)
    res = disp.execute_refund("ref-101", 50.0, retries=0)
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", res["key"]) is not None

def test_case_2():
    journal = RefundAuditJournal()
    disp = RefundDispatcher(journal)
    disp.execute_refund("ref-102", 75.0, retries=1)
    assert len(journal.audit_log) == 2
    assert journal.audit_log[0]["key"] == journal.audit_log[1]["key"]
'''
    }

    t2065_ref = {
        "key_factory.py": '''"""Idempotency key construction factory."""
import time
import secrets

def create_refund_key(refund_id: str) -> str:
    """Creates refund idempotency key."""
    ts_ms = int(time.time() * 1000)
    token = secrets.token_hex(4)
    return f"idemp_{ts_ms}_{token}"

def is_valid_refund_key(key: str) -> bool:
    return len(key) > 5
'''
    }

    t2065_m1 = {
        "refund_dispatcher.py": '''"""Refund dispatch coordinator."""
from typing import Dict, Any
from key_factory import create_refund_key, is_valid_refund_key
from refund_audit import RefundAuditJournal

class RefundDispatcher:
    def __init__(self, journal: RefundAuditJournal):
        self.journal = journal

    def execute_refund(self, refund_id: str, amount: float, retries: int = 1) -> Dict[str, Any]:
        key = None
        for _ in range(retries + 1):
            key = create_refund_key(refund_id)
            self.journal.record_attempt(refund_id, key, amount)
        return {"refund_id": refund_id, "header": "X-Idempotency-Key", "key": key}
'''
    }

    t2065_m2 = {
        "key_factory.py": '''"""Idempotency key construction factory."""
import time
import secrets

def create_refund_key(refund_id: str) -> str:
    """Creates refund idempotency key."""
    ts_ms = int(time.time() * 1000)
    token = secrets.token_hex(4)
    return f"{ts_ms}_{token}"

def is_valid_refund_key(key: str) -> bool:
    return len(key) > 5
'''
    }

    add_task(
        tid=2065,
        family="idempotency_keys",
        name="Customer Refund Dispatcher",
        class_tag="TAUGHT",
        issue="Incident INC-9305: Customer refund pipeline failed outbound validation due to non-standard prefix in refund tracking key.",
        traceback_text="FAILED tests/test_refund_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["refund_dispatcher.py"],
        repo=t2065_repo,
        hidden=t2065_hidden,
        ref=t2065_ref,
        mutant1=t2065_m1,
        mutant2=t2065_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2066: Warehouse Stock Reservation Client (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2066_repo = {
        "stock_record.py": '''"""Inventory reservation records."""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ReservationResult:
    warehouse_id: str
    items: List[str]
    headers: Dict[str, str] = field(default_factory=dict)

    def is_empty_reservation(self) -> bool:
        return len(self.items) == 0
''',
        "sku_verifier.py": '''"""SKU format and checksum validator."""
from typing import List

def verify_sku_list(items: List[str]) -> bool:
    return all(len(item) > 2 for item in items)

def count_distinct_items(items: List[str]) -> int:
    return len(set(items))
''',
        "stock_client.py": '''"""Warehouse inventory stock reservation client."""
import time
from typing import Dict, Any, List
from stock_record import ReservationResult
from sku_verifier import verify_sku_list, count_distinct_items

class StockClient:
    def __init__(self):
        self.dispatched_attempts: List[Dict[str, str]] = []

    def reserve_stock(self, warehouse_id: str, items: List[str], retries: int = 1) -> ReservationResult:
        """Reserves inventory stock units.
        Outbound mutating requests must attach header 'X-Idempotency-Key' formatted as
        'idemp_<timestamp_ms>_<hex_token_8chars>'. Retries must reuse the exact same
        idempotency key across attempts.
        """
        if not verify_sku_list(items):
            raise ValueError("Invalid SKUs")
        _ = count_distinct_items(items)
        hdrs = None
        for _ in range(retries + 1):
            seq = str(int(time.time() * 1000))
            hdrs = {"X-Idempotency-Key": f"idemp_{seq}"}
            self.dispatched_attempts.append(dict(hdrs))
        return ReservationResult(warehouse_id=warehouse_id, items=items, headers=hdrs)
''',
        "tests/test_stock.py": '''from stock_client import StockClient

def test_service_execution():
    client = StockClient()
    res = client.reserve_stock("wh-east", ["SKU-1", "SKU-2"], retries=0)
    assert res.warehouse_id == "wh-east"
    assert res.is_empty_reservation() is False
    assert "X-Idempotency-Key" in res.headers
'''
    }

    t2066_hidden = {
        "tests/test_stock_cases.py": '''import re
from stock_client import StockClient

def test_case_1():
    client = StockClient()
    res = client.reserve_stock("wh-east", ["SKU-1"], retries=0)
    key = res.headers["X-Idempotency-Key"]
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", key) is not None

def test_case_2():
    client = StockClient()
    client.reserve_stock("wh-east", ["SKU-1"], retries=1)
    assert len(client.dispatched_attempts) == 2
    assert client.dispatched_attempts[0]["X-Idempotency-Key"] == client.dispatched_attempts[1]["X-Idempotency-Key"]
'''
    }

    t2066_ref = {
        "stock_client.py": '''"""Warehouse inventory stock reservation client."""
import time
import secrets
from typing import Dict, Any, List
from stock_record import ReservationResult
from sku_verifier import verify_sku_list, count_distinct_items

class StockClient:
    def __init__(self):
        self.dispatched_attempts: List[Dict[str, str]] = []

    def reserve_stock(self, warehouse_id: str, items: List[str], retries: int = 1) -> ReservationResult:
        """Reserves inventory stock units.
        Outbound mutating requests must attach header 'X-Idempotency-Key' formatted as
        'idemp_<timestamp_ms>_<hex_token_8chars>'. Retries must reuse the exact same
        idempotency key across attempts.
        """
        if not verify_sku_list(items):
            raise ValueError("Invalid SKUs")
        _ = count_distinct_items(items)
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        key = f"idemp_{ts_ms}_{token}"
        hdrs = {"X-Idempotency-Key": key}
        for _ in range(retries + 1):
            self.dispatched_attempts.append(dict(hdrs))
        return ReservationResult(warehouse_id=warehouse_id, items=items, headers=hdrs)
'''
    }

    t2066_m1 = {
        "stock_client.py": '''"""Warehouse inventory stock reservation client."""
import time
import secrets
from typing import Dict, Any, List
from stock_record import ReservationResult
from sku_verifier import verify_sku_list, count_distinct_items

class StockClient:
    def __init__(self):
        self.dispatched_attempts: List[Dict[str, str]] = []

    def reserve_stock(self, warehouse_id: str, items: List[str], retries: int = 1) -> ReservationResult:
        if not verify_sku_list(items):
            raise ValueError("Invalid SKUs")
        _ = count_distinct_items(items)
        hdrs = None
        for _ in range(retries + 1):
            ts_ms = int(time.time() * 1000)
            token = secrets.token_hex(4)
            key = f"idemp_{ts_ms}_{token}"
            hdrs = {"X-Idempotency-Key": key}
            self.dispatched_attempts.append(dict(hdrs))
        return ReservationResult(warehouse_id=warehouse_id, items=items, headers=hdrs)
'''
    }

    t2066_m2 = {
        "stock_client.py": '''"""Warehouse inventory stock reservation client."""
import time
import secrets
from typing import Dict, Any, List
from stock_record import ReservationResult
from sku_verifier import verify_sku_list, count_distinct_items

class StockClient:
    def __init__(self):
        self.dispatched_attempts: List[Dict[str, str]] = []

    def reserve_stock(self, warehouse_id: str, items: List[str], retries: int = 1) -> ReservationResult:
        if not verify_sku_list(items):
            raise ValueError("Invalid SKUs")
        _ = count_distinct_items(items)
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        key = f"idemp_{ts_ms}_{token}"
        hdrs = {"Idempotency-Key": key}
        for _ in range(retries + 1):
            self.dispatched_attempts.append(dict(hdrs))
        return ReservationResult(warehouse_id=warehouse_id, items=items, headers=hdrs)
'''
    }

    add_task(
        tid=2066,
        family="idempotency_keys",
        name="Warehouse Stock Reservation Client",
        class_tag="STATED",
        issue="Incident INC-9306: Stock reservation failed schema validation because idempotency header omitted random 8-character token suffix.",
        traceback_text="FAILED tests/test_stock_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["stock_client.py"],
        repo=t2066_repo,
        hidden=t2066_hidden,
        ref=t2066_ref,
        mutant1=t2066_m1,
        mutant2=t2066_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "stock_client.py docstring: 'X-Idempotency-Key formatted as idemp_<timestamp_ms>_<hex_token_8chars>'", "Yes", "STATED"),
            ("test_case_2", "stock_client.py docstring: 'Retries must reuse the exact same idempotency key across attempts'", "Yes", "STATED"),
        ]
    )

    # =========================================================================
    # Task 2067: Cloud Virtual Machine Provisioning RPC (TAUGHT, HRC=True, VTS=True)
    # =========================================================================
    t2067_repo = {
        "token_builder.py": '''"""RPC header token builders for compute instances."""
import uuid
from typing import Dict, Optional

def build_mutation_headers() -> Dict[str, str]:
    """Generates standard request mutation headers."""
    return {"X-Request-Id": str(uuid.uuid4())}

def is_valid_header_dict(hdrs: dict) -> bool:
    """Validates that header mapping is non-empty."""
    return isinstance(hdrs, dict) and len(hdrs) > 0

def extract_request_token(hdrs: dict) -> Optional[str]:
    """Extracts existing request identifier if present."""
    return hdrs.get("X-Request-Id")
''',
        "quota_tracker.py": '''"""VM quota tracking and endpoint lookup."""
from typing import Optional

def check_core_quota(cores: int) -> bool:
    """Verifies requested cores do not exceed tenant quota."""
    return 0 < cores <= 64

def get_region_endpoint(region: str) -> str:
    """Resolves compute endpoint URL for target AWS region."""
    return f"https://{region.strip().lower()}.compute.internal"

def default_region_zone(region: str) -> str:
    """Returns primary availability zone identifier."""
    return f"{region}a"
''',
        "vm_provisioner.py": '''"""Virtual machine provisioning client."""
from typing import Dict, Any, List
from token_builder import build_mutation_headers, is_valid_header_dict
from quota_tracker import check_core_quota, get_region_endpoint

class VMProvisioner:
    def __init__(self):
        self.dispatched_calls: List[Dict[str, str]] = []

    def provision_instance(self, instance_id: str, cores: int, region: str, retries: int = 1) -> Dict[str, Any]:
        if not check_core_quota(cores):
            raise ValueError("Core quota exceeded")
        endpoint = get_region_endpoint(region)
        hdrs = None
        for _ in range(retries + 1):
            hdrs = build_mutation_headers()
            if not is_valid_header_dict(hdrs):
                raise ValueError("Invalid headers")
            self.dispatched_calls.append(dict(hdrs))
        return {"instance_id": instance_id, "endpoint": endpoint, "headers": hdrs}
''',
        "tests/test_vm.py": '''from vm_provisioner import VMProvisioner

def test_service_execution():
    client = VMProvisioner()
    res = client.provision_instance("i-1234", 4, "us-east-2", retries=0)
    assert res["instance_id"] == "i-1234"
    assert "headers" in res
'''
    }

    t2067_hidden = {
        "tests/test_vm_cases.py": '''import re
from vm_provisioner import VMProvisioner

def test_case_1():
    client = VMProvisioner()
    res = client.provision_instance("i-1234", 4, "us-east-2", retries=0)
    assert "X-Idempotency-Key" in res["headers"]
    key = res["headers"]["X-Idempotency-Key"]
    assert re.match(r"^idemp_\d+_[0-9a-f]{8}$", key) is not None

def test_case_2():
    client = VMProvisioner()
    client.provision_instance("i-5678", 8, "us-east-2", retries=1)
    assert len(client.dispatched_calls) == 2
    assert client.dispatched_calls[0]["X-Idempotency-Key"] == client.dispatched_calls[1]["X-Idempotency-Key"]
'''
    }

    t2067_ref = {
        "token_builder.py": '''"""RPC header token builders."""
import time
import secrets
from typing import Dict

def build_mutation_headers() -> Dict[str, str]:
    ts_ms = int(time.time() * 1000)
    token = secrets.token_hex(4)
    return {"X-Idempotency-Key": f"idemp_{ts_ms}_{token}"}

def is_valid_header_dict(hdrs: dict) -> bool:
    return len(hdrs) > 0
''',
        "vm_provisioner.py": '''"""Virtual machine provisioning client."""
from typing import Dict, Any, List
from token_builder import build_mutation_headers, is_valid_header_dict
from quota_tracker import check_core_quota, get_region_endpoint

class VMProvisioner:
    def __init__(self):
        self.dispatched_calls: List[Dict[str, str]] = []

    def provision_instance(self, instance_id: str, cores: int, region: str, retries: int = 1) -> Dict[str, Any]:
        if not check_core_quota(cores):
            raise ValueError("Core quota exceeded")
        endpoint = get_region_endpoint(region)
        hdrs = build_mutation_headers()
        if not is_valid_header_dict(hdrs):
            raise ValueError("Invalid headers")
        for _ in range(retries + 1):
            self.dispatched_calls.append(dict(hdrs))
        return {"instance_id": instance_id, "endpoint": endpoint, "headers": hdrs}
'''
    }

    t2067_m1 = {
        "token_builder.py": '''"""RPC header token builders."""
import time
import secrets
from typing import Dict

def build_mutation_headers() -> Dict[str, str]:
    ts_ms = int(time.time() * 1000)
    token = secrets.token_hex(4)
    return {"X-Idempotency-Key": f"idemp_{ts_ms}_{token}"}

def is_valid_header_dict(hdrs: dict) -> bool:
    return len(hdrs) > 0
''',
        "vm_provisioner.py": '''"""Virtual machine provisioning client."""
from typing import Dict, Any, List
from token_builder import build_mutation_headers, is_valid_header_dict
from quota_tracker import check_core_quota, get_region_endpoint

class VMProvisioner:
    def __init__(self):
        self.dispatched_calls: List[Dict[str, str]] = []

    def provision_instance(self, instance_id: str, cores: int, region: str, retries: int = 1) -> Dict[str, Any]:
        if not check_core_quota(cores):
            raise ValueError("Core quota exceeded")
        endpoint = get_region_endpoint(region)
        hdrs = None
        for _ in range(retries + 1):
            hdrs = build_mutation_headers()
            self.dispatched_calls.append(dict(hdrs))
        return {"instance_id": instance_id, "endpoint": endpoint, "headers": hdrs}
'''
    }

    t2067_m2 = {
        "token_builder.py": '''"""RPC header token builders."""
import secrets
from typing import Dict

def build_mutation_headers() -> Dict[str, str]:
    token = secrets.token_hex(4)
    return {"X-Idempotency-Key": f"idemp_{token}"}

def is_valid_header_dict(hdrs: dict) -> bool:
    return len(hdrs) > 0
'''
    }

    add_task(
        tid=2067,
        family="idempotency_keys",
        name="Cloud Virtual Machine Provisioning RPC",
        class_tag="TAUGHT",
        issue="Incident INC-9307: Cloud control plane rejected provisioning RPC due to absent X-Idempotency-Key header.",
        traceback_text="FAILED tests/test_vm_cases.py::test_case_1 - AssertionError: assert 'X-Idempotency-Key' in {'X-Request-Id': '...'}",
        traceback_files=["vm_provisioner.py"],
        repo=t2067_repo,
        hidden=t2067_hidden,
        ref=t2067_ref,
        mutant1=t2067_m1,
        mutant2=t2067_m2,
        hidden_root_cause=True,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
            ("test_case_2", "HANDBOOK.md Rule H13", "No", "TAUGHT"),
        ]
    )

    # =========================================================================
    # Task 2068: Clearing House Settlement Client (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2068_repo = {
        "settlement_record.py": '''"""Clearing house settlement payload models."""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class SettlementBatch:
    batch_id: str
    amount: float
    headers: Dict[str, Any] = field(default_factory=dict)

    def is_valid_batch(self) -> bool:
        return bool(self.batch_id and self.amount > 0)
''',
        "ledger_digest.py": '''"""Ledger transaction hashing and formatting."""
def compute_batch_digest(batch_id: str) -> str:
    return str(hash(batch_id) % 10000)

def is_valid_batch_id(batch_id: str) -> bool:
    return batch_id.startswith("bat_")
''',
        "settlement_client.py": '''"""Clearing house settlement client."""
import time
from typing import Dict, Any, List
from settlement_record import SettlementBatch
from ledger_digest import compute_batch_digest, is_valid_batch_id

class SettlementClient:
    def __init__(self):
        self.dispatched_batches: List[SettlementBatch] = []

    def post_settlement(self, batch_id: str, amount: float, retries: int = 1) -> SettlementBatch:
        """Submits settlement batch to clearing house engine.
        Local clearing house specification: The idempotency identifier must be passed
        in header 'Tx-Identifier' containing a raw integer transaction ID (e.g. int(time.time() * 1000)).
        Do NOT format as a string token with prefixes.
        """
        if not is_valid_batch_id(batch_id):
            raise ValueError("Invalid batch ID")
        _ = compute_batch_digest(batch_id)
        batch = None
        for _ in range(retries + 1):
            ts_str = f"idemp_{int(time.time() * 1000)}_token"
            hdrs = {"Tx-Identifier": ts_str}
            batch = SettlementBatch(batch_id=batch_id, amount=amount, headers=hdrs)
            self.dispatched_batches.append(batch)
        return batch
''',
        "tests/test_settlement.py": '''from settlement_client import SettlementClient

def test_service_execution():
    client = SettlementClient()
    b = client.post_settlement("bat_001", 15000.0, retries=0)
    assert b.batch_id == "bat_001"
    assert b.is_valid_batch() is True
    assert "Tx-Identifier" in b.headers
'''
    }

    t2068_hidden = {
        "tests/test_settlement_cases.py": '''from settlement_client import SettlementClient

def test_case_1():
    client = SettlementClient()
    b = client.post_settlement("bat_001", 15000.0, retries=0)
    assert "Tx-Identifier" in b.headers
    assert "X-Idempotency-Key" not in b.headers
    val = b.headers["Tx-Identifier"]
    assert isinstance(val, int) or str(val).isdigit()

def test_case_2():
    client = SettlementClient()
    client.post_settlement("bat_002", 20000.0, retries=1)
    assert len(client.dispatched_batches) == 2
    t1 = client.dispatched_batches[0].headers["Tx-Identifier"]
    t2 = client.dispatched_batches[1].headers["Tx-Identifier"]
    assert t1 == t2
'''
    }

    t2068_ref = {
        "settlement_client.py": '''"""Clearing house settlement client."""
import time
from typing import Dict, Any, List
from settlement_record import SettlementBatch
from ledger_digest import compute_batch_digest, is_valid_batch_id

class SettlementClient:
    def __init__(self):
        self.dispatched_batches: List[SettlementBatch] = []

    def post_settlement(self, batch_id: str, amount: float, retries: int = 1) -> SettlementBatch:
        """Submits settlement batch to clearing house engine.
        Local clearing house specification: The idempotency identifier must be passed
        in header 'Tx-Identifier' containing a raw integer transaction ID (e.g. int(time.time() * 1000)).
        Do NOT format as a string token with prefixes.
        """
        if not is_valid_batch_id(batch_id):
            raise ValueError("Invalid batch ID")
        _ = compute_batch_digest(batch_id)
        tx_id = int(time.time() * 1000)
        hdrs = {"Tx-Identifier": tx_id}
        batch = None
        for _ in range(retries + 1):
            batch = SettlementBatch(batch_id=batch_id, amount=amount, headers=hdrs)
            self.dispatched_batches.append(batch)
        return batch
'''
    }

    t2068_m1 = {
        "settlement_client.py": '''"""Clearing house settlement client."""
import time
import secrets
from typing import Dict, Any, List
from settlement_record import SettlementBatch
from ledger_digest import compute_batch_digest, is_valid_batch_id

class SettlementClient:
    def __init__(self):
        self.dispatched_batches: List[SettlementBatch] = []

    def post_settlement(self, batch_id: str, amount: float, retries: int = 1) -> SettlementBatch:
        if not is_valid_batch_id(batch_id):
            raise ValueError("Invalid batch ID")
        _ = compute_batch_digest(batch_id)
        ts_ms = int(time.time() * 1000)
        token = secrets.token_hex(4)
        key = f"idemp_{ts_ms}_{token}"
        hdrs = {"X-Idempotency-Key": key}
        batch = None
        for _ in range(retries + 1):
            batch = SettlementBatch(batch_id=batch_id, amount=amount, headers=hdrs)
            self.dispatched_batches.append(batch)
        return batch
'''
    }

    t2068_m2 = {
        "settlement_client.py": '''"""Clearing house settlement client."""
import random
from typing import Dict, Any, List
from settlement_record import SettlementBatch
from ledger_digest import compute_batch_digest, is_valid_batch_id

class SettlementClient:
    def __init__(self):
        self.dispatched_batches: List[SettlementBatch] = []

    def post_settlement(self, batch_id: str, amount: float, retries: int = 1) -> SettlementBatch:
        if not is_valid_batch_id(batch_id):
            raise ValueError("Invalid batch ID")
        _ = compute_batch_digest(batch_id)
        tx_id = f"random_id_{random.random()}"
        hdrs = {"Tx-Identifier": tx_id}
        batch = None
        for _ in range(retries + 1):
            batch = SettlementBatch(batch_id=batch_id, amount=amount, headers=hdrs)
            self.dispatched_batches.append(batch)
        return batch
'''
    }

    add_task(
        tid=2068,
        family="idempotency_keys",
        name="Clearing House Settlement Client",
        class_tag="DISTRACTOR",
        issue="Incident INC-9308: Clearing house settlement rejected transactions due to non-integer string in Tx-Identifier header.",
        traceback_text="FAILED tests/test_settlement_cases.py::test_case_1 - AssertionError: assert False == True",
        traceback_files=["settlement_client.py"],
        repo=t2068_repo,
        hidden=t2068_hidden,
        ref=t2068_ref,
        mutant1=t2068_m1,
        mutant2=t2068_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H13"],
        assertions=[
            ("test_case_1", "settlement_client.py docstring: 'Tx-Identifier containing a raw integer transaction ID'", "Yes", "DISTRACTOR"),
            ("test_case_2", "settlement_client.py docstring: 'Tx-Identifier containing a raw integer transaction ID'", "Yes", "DISTRACTOR"),
        ]
    )

    print("Family 12 registered (Tasks 2061-2068).")
