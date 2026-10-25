"""Family 14: state_transitions (Tasks 2077 - 2084, PURE TRANSFER FAMILY 2).

Governing Rule: Rule H15 (Finite State Machine Transition Validation and Audit Tuples:
validate allowed transitions and emit structured audit tuple:
("STATE_TRANSITION", entity_id, old_state, new_state, actor_id, timestamp_ms).
Invalid transitions must raise ServiceError(code="ERR_INVALID_TRANSITION", ...).)
Competing Alternatives: Unvalidated transitions, generic ValueError, malformed audit tuples.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_14(add_task):
    # =========================================================================
    # Task 2077: Deployment Pipeline Lifecycle (TRANSFER, HRC=False, VTS=True)
    # =========================================================================
    t2077_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "pipeline_models.py": '''"""CI/CD deployment pipeline entity model."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict

@dataclass
class PipelineEntity:
    entity_id: str
    state: str = "PENDING"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return self.state in {"DEPLOYED", "FAILED", "CANCELLED"}

    def audit_count(self) -> int:
        return len(self.audit_trail)
''',
        "pipeline_manager.py": '''"""Deployment pipeline lifecycle state manager."""
from typing import Set, Dict, Any
from errors import ServiceError
from pipeline_models import PipelineEntity

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "PENDING": {"BUILDING", "CANCELLED"},
    "BUILDING": {"TESTING", "FAILED", "CANCELLED"},
    "TESTING": {"DEPLOYED", "FAILED", "CANCELLED"},
    "DEPLOYED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}

def transition_pipeline(pipeline: PipelineEntity, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions pipeline to target state and records audit event."""
    old_state = pipeline.state
    # Unpatched baseline: does not validate allowed transitions or emit audit tuple
    pipeline.state = new_state

def get_pipeline_status(pipeline: PipelineEntity) -> Dict[str, Any]:
    return {"id": pipeline.entity_id, "state": pipeline.state, "terminal": pipeline.is_terminal()}
''',
        "tests/test_pipeline.py": '''from pipeline_models import PipelineEntity
from pipeline_manager import transition_pipeline, get_pipeline_status

def test_initial_state():
    p = PipelineEntity("pipe-001")
    assert p.state == "PENDING"
    assert p.audit_count() == 0
    st = get_pipeline_status(p)
    assert not st["terminal"]

def test_normal_step():
    p = PipelineEntity("pipe-001")
    transition_pipeline(p, "BUILDING", "actor-1", 1700000000000)
    assert p.state == "BUILDING"
'''
    }

    t2077_hidden = {
        "tests/test_pipeline_cases.py": '''import pytest
from errors import ServiceError
from pipeline_models import PipelineEntity
from pipeline_manager import transition_pipeline

def test_case_1():
    p = PipelineEntity("pipe-100")
    transition_pipeline(p, "BUILDING", "user-1", 1700000001000)
    assert p.state == "BUILDING"
    assert len(p.audit_trail) == 1
    assert p.audit_trail[0] == ("STATE_TRANSITION", "pipe-100", "PENDING", "BUILDING", "user-1", 1700000001000)

def test_case_2():
    p = PipelineEntity("pipe-200")
    # Illegal direct jump PENDING -> DEPLOYED
    with pytest.raises(ServiceError) as exc_info:
        transition_pipeline(p, "DEPLOYED", "user-2", 1700000002000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
    assert p.state == "PENDING"
'''
    }

    t2077_ref = {
        "pipeline_manager.py": '''"""Deployment pipeline lifecycle state manager."""
from typing import Set, Dict, Any
from errors import ServiceError
from pipeline_models import PipelineEntity

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "PENDING": {"BUILDING", "CANCELLED"},
    "BUILDING": {"TESTING", "FAILED", "CANCELLED"},
    "TESTING": {"DEPLOYED", "FAILED", "CANCELLED"},
    "DEPLOYED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}

def transition_pipeline(pipeline: PipelineEntity, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions pipeline to target state and records audit event."""
    old_state = pipeline.state
    allowed = ALLOWED_TRANSITIONS.get(old_state, set())
    if new_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Invalid transition {old_state} -> {new_state}")
    pipeline.audit_trail.append(("STATE_TRANSITION", pipeline.entity_id, old_state, new_state, actor_id, timestamp_ms))
    pipeline.state = new_state

def get_pipeline_status(pipeline: PipelineEntity) -> Dict[str, Any]:
    return {"id": pipeline.entity_id, "state": pipeline.state, "terminal": pipeline.is_terminal()}
'''
    }

    t2077_m1 = {
        "pipeline_manager.py": '''"""Deployment pipeline lifecycle state manager."""
from typing import Set, Dict, Any
from errors import ServiceError
from pipeline_models import PipelineEntity

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "PENDING": {"BUILDING", "CANCELLED"},
    "BUILDING": {"TESTING", "FAILED", "CANCELLED"},
    "TESTING": {"DEPLOYED", "FAILED", "CANCELLED"},
    "DEPLOYED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}

def transition_pipeline(pipeline: PipelineEntity, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    old_state = pipeline.state
    allowed = ALLOWED_TRANSITIONS.get(old_state, set())
    if new_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Invalid transition {old_state} -> {new_state}")
    pipeline.audit_trail.append(("STATE_TRANSITION", pipeline.entity_id, new_state, old_state, actor_id))
    pipeline.state = new_state

def get_pipeline_status(pipeline: PipelineEntity) -> Dict[str, Any]:
    return {"id": pipeline.entity_id, "state": pipeline.state, "terminal": pipeline.is_terminal()}
'''
    }

    t2077_m2 = {
        "pipeline_manager.py": '''"""Deployment pipeline lifecycle state manager."""
from typing import Set, Dict, Any
from errors import ServiceError
from pipeline_models import PipelineEntity

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "PENDING": {"BUILDING", "CANCELLED"},
    "BUILDING": {"TESTING", "FAILED", "CANCELLED"},
    "TESTING": {"DEPLOYED", "FAILED", "CANCELLED"},
    "DEPLOYED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}

def transition_pipeline(pipeline: PipelineEntity, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    old_state = pipeline.state
    allowed = ALLOWED_TRANSITIONS.get(old_state, set())
    if new_state not in allowed:
        raise ValueError(f"Invalid transition {old_state} -> {new_state}")
    pipeline.audit_trail.append(("STATE_TRANSITION", pipeline.entity_id, old_state, new_state, actor_id, timestamp_ms))
    pipeline.state = new_state

def get_pipeline_status(pipeline: PipelineEntity) -> Dict[str, Any]:
    return {"id": pipeline.entity_id, "state": pipeline.state, "terminal": pipeline.is_terminal()}
'''
    }

    add_task(
        tid=2077,
        family="state_transitions",
        name="Deployment Pipeline Lifecycle",
        class_tag="TRANSFER",
        issue="Incident INC-8201: Deployment pipeline service recorded illegal transitions and lacked transition audit records.",
        traceback_text="FAILED tests/test_pipeline_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["pipeline_manager.py"],
        repo=t2077_repo,
        hidden=t2077_hidden,
        ref=t2077_ref,
        mutant1=t2077_m1,
        mutant2=t2077_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: State transition audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on invalid jump", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2078: Payment Escrow Lifecycle (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2078_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "escrow_engine.py": '''"""Escrow transaction schemas and transition validator."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class EscrowAccount:
    entity_id: str
    amount_cents: int
    state: str = "INITIAL"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finalized(self) -> bool:
        return self.state in {"RELEASED", "REFUNDED"}

ESCROW_TRANSITIONS: Dict[str, Set[str]] = {
    "INITIAL": {"HELD"},
    "HELD": {"RELEASED", "REFUNDED", "DISPUTED"},
    "DISPUTED": {"RELEASED", "REFUNDED"},
    "RELEASED": set(),
    "REFUNDED": set(),
}

def execute_escrow_transition(escrow: EscrowAccount, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Validates and executes escrow state change."""
    cur = escrow.state
    allowed = ESCROW_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        # Erroneous error code and missing audit tuple in unpatched code
        raise ServiceError(code="ERR_ESCROW_INVALID_STATE", message="Bad state")
    escrow.state = target_state
''',
        "escrow_service.py": '''"""Public service interface for escrow operations."""
from typing import Dict, Any
from escrow_engine import EscrowAccount, execute_escrow_transition

def update_escrow(escrow: EscrowAccount, next_state: str, actor_id: str, timestamp_ms: int) -> EscrowAccount:
    """Updates escrow account to next state."""
    execute_escrow_transition(escrow, next_state, actor_id, timestamp_ms)
    return escrow

def get_escrow_details(escrow: EscrowAccount) -> Dict[str, Any]:
    return {"id": escrow.entity_id, "state": escrow.state, "cents": escrow.amount_cents}
''',
        "tests/test_escrow.py": '''from escrow_engine import EscrowAccount
from escrow_service import update_escrow, get_escrow_details

def test_initial_hold():
    e = EscrowAccount("esc-10", 5000)
    update_escrow(e, "HELD", "admin", 1700000000000)
    assert e.state == "HELD"
    details = get_escrow_details(e)
    assert details["cents"] == 5000
'''
    }

    t2078_hidden = {
        "tests/test_escrow_cases.py": '''import pytest
from errors import ServiceError
from escrow_engine import EscrowAccount
from escrow_service import update_escrow

def test_case_1():
    e = EscrowAccount("esc-55", 10000)
    update_escrow(e, "HELD", "sys", 1700000010000)
    assert len(e.audit_trail) == 1
    assert e.audit_trail[0] == ("STATE_TRANSITION", "esc-55", "INITIAL", "HELD", "sys", 1700000010000)

def test_case_2():
    e = EscrowAccount("esc-99", 2000)
    # Direct jump INITIAL -> RELEASED is forbidden
    with pytest.raises(ServiceError) as exc_info:
        update_escrow(e, "RELEASED", "sys", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2078_ref = {
        "escrow_engine.py": '''"""Escrow transaction schemas and transition validator."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class EscrowAccount:
    entity_id: str
    amount_cents: int
    state: str = "INITIAL"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finalized(self) -> bool:
        return self.state in {"RELEASED", "REFUNDED"}

ESCROW_TRANSITIONS: Dict[str, Set[str]] = {
    "INITIAL": {"HELD"},
    "HELD": {"RELEASED", "REFUNDED", "DISPUTED"},
    "DISPUTED": {"RELEASED", "REFUNDED"},
    "RELEASED": set(),
    "REFUNDED": set(),
}

def execute_escrow_transition(escrow: EscrowAccount, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Validates and executes escrow state change."""
    cur = escrow.state
    allowed = ESCROW_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {target_state} not permitted")
    escrow.audit_trail.append(("STATE_TRANSITION", escrow.entity_id, cur, target_state, actor_id, timestamp_ms))
    escrow.state = target_state
'''
    }

    t2078_m1 = {
        "escrow_service.py": '''"""Public service interface for escrow operations."""
from typing import Dict, Any
from escrow_engine import EscrowAccount, execute_escrow_transition

def update_escrow(escrow: EscrowAccount, next_state: str, actor_id: str, timestamp_ms: int) -> EscrowAccount:
    if next_state == "RELEASED" and escrow.state == "INITIAL":
        return escrow
    execute_escrow_transition(escrow, next_state, actor_id, timestamp_ms)
    return escrow

def get_escrow_details(escrow: EscrowAccount) -> Dict[str, Any]:
    return {"id": escrow.entity_id, "state": escrow.state, "cents": escrow.amount_cents}
'''
    }

    t2078_m2 = {
        "escrow_engine.py": '''"""Escrow transaction schemas and transition validator."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class EscrowAccount:
    entity_id: str
    amount_cents: int
    state: str = "INITIAL"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finalized(self) -> bool:
        return self.state in {"RELEASED", "REFUNDED"}

ESCROW_TRANSITIONS: Dict[str, Set[str]] = {
    "INITIAL": {"HELD"},
    "HELD": {"RELEASED", "REFUNDED", "DISPUTED"},
    "DISPUTED": {"RELEASED", "REFUNDED"},
    "RELEASED": set(),
    "REFUNDED": set(),
}

def execute_escrow_transition(escrow: EscrowAccount, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = escrow.state
    allowed = ESCROW_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_STATE_REJECTED", message="Not allowed")
    escrow.audit_trail.append(("STATE_TRANSITION", escrow.entity_id, cur, target_state, actor_id, timestamp_ms))
    escrow.state = target_state
'''
    }

    add_task(
        tid=2078,
        family="state_transitions",
        name="Payment Escrow Lifecycle",
        class_tag="TRANSFER",
        issue="Incident INC-8202: Settlement clearing gateway raised non-standard error codes on invalid escrow release.",
        traceback_text="FAILED tests/test_escrow_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["escrow_service.py"],
        repo=t2078_repo,
        hidden=t2078_hidden,
        ref=t2078_ref,
        mutant1=t2078_m1,
        mutant2=t2078_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Escrow audit transition tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on disallowed jump", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2079: Support Ticket Workflow (TRANSFER, HRC=False, VTS=True)
    # =========================================================================
    t2079_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "ticket_models.py": '''"""Support desk ticket data definitions."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict

@dataclass
class SupportTicket:
    entity_id: str
    state: str = "CREATED"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_closed(self) -> bool:
        return self.state == "CLOSED"

    def audit_count(self) -> int:
        return len(self.audit_trail)
''',
        "ticket_workflow.py": '''"""Customer support ticket transition workflow."""
from typing import Dict, Set, Any
from errors import ServiceError
from ticket_models import SupportTicket

TICKET_TRANSITIONS: Dict[str, Set[str]] = {
    "CREATED": {"ASSIGNED", "CLOSED"},
    "ASSIGNED": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"RESOLVED", "ASSIGNED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set(),
}

def transition_ticket(ticket: SupportTicket, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Applies status change to support ticket."""
    cur = ticket.state
    # Unpatched baseline: sets state without validation or audit tuple
    ticket.state = next_state

def get_ticket_status(ticket: SupportTicket) -> Dict[str, Any]:
    return {"id": ticket.entity_id, "state": ticket.state, "closed": ticket.is_closed()}
''',
        "tests/test_ticket.py": '''from ticket_models import SupportTicket
from ticket_workflow import transition_ticket, get_ticket_status

def test_initial_ticket():
    t = SupportTicket("tick-01")
    assert t.state == "CREATED"
    assert t.audit_count() == 0
    st = get_ticket_status(t)
    assert not st["closed"]

def test_assign():
    t = SupportTicket("tick-01")
    transition_ticket(t, "ASSIGNED", "agent-1", 1700000000000)
    assert t.state == "ASSIGNED"
'''
    }

    t2079_hidden = {
        "tests/test_ticket_cases.py": '''import pytest
from errors import ServiceError
from ticket_models import SupportTicket
from ticket_workflow import transition_ticket

def test_case_1():
    t = SupportTicket("tick-100")
    transition_ticket(t, "ASSIGNED", "dispatcher", 1700000010000)
    assert len(t.audit_trail) == 1
    assert t.audit_trail[0] == ("STATE_TRANSITION", "tick-100", "CREATED", "ASSIGNED", "dispatcher", 1700000010000)

def test_case_2():
    t = SupportTicket("tick-200")
    # Illegal transition: CREATED -> RESOLVED directly
    with pytest.raises(ServiceError) as exc_info:
        transition_ticket(t, "RESOLVED", "agent-x", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2079_ref = {
        "ticket_workflow.py": '''"""Customer support ticket transition workflow."""
from typing import Dict, Set, Any
from errors import ServiceError
from ticket_models import SupportTicket

TICKET_TRANSITIONS: Dict[str, Set[str]] = {
    "CREATED": {"ASSIGNED", "CLOSED"},
    "ASSIGNED": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"RESOLVED", "ASSIGNED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set(),
}

def transition_ticket(ticket: SupportTicket, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Applies status change to support ticket."""
    cur = ticket.state
    allowed = TICKET_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {next_state} rejected")
    ticket.audit_trail.append(("STATE_TRANSITION", ticket.entity_id, cur, next_state, actor_id, timestamp_ms))
    ticket.state = next_state

def get_ticket_status(ticket: SupportTicket) -> Dict[str, Any]:
    return {"id": ticket.entity_id, "state": ticket.state, "closed": ticket.is_closed()}
'''
    }

    t2079_m1 = {
        "ticket_workflow.py": '''"""Customer support ticket transition workflow."""
from typing import Dict, Set, Any
from errors import ServiceError
from ticket_models import SupportTicket

TICKET_TRANSITIONS: Dict[str, Set[str]] = {
    "CREATED": {"ASSIGNED", "CLOSED"},
    "ASSIGNED": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"RESOLVED", "ASSIGNED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set(),
}

def transition_ticket(ticket: SupportTicket, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = ticket.state
    allowed = TICKET_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {next_state} rejected")
    ticket.audit_trail.append(("TRANSITION", ticket.entity_id, cur, next_state, actor_id, timestamp_ms))
    ticket.state = next_state

def get_ticket_status(ticket: SupportTicket) -> Dict[str, Any]:
    return {"id": ticket.entity_id, "state": ticket.state, "closed": ticket.is_closed()}
'''
    }

    t2079_m2 = {
        "ticket_workflow.py": '''"""Customer support ticket transition workflow."""
from typing import Dict, Set, Any
from errors import ServiceError
from ticket_models import SupportTicket

TICKET_TRANSITIONS: Dict[str, Set[str]] = {
    "CREATED": {"ASSIGNED", "CLOSED"},
    "ASSIGNED": {"IN_PROGRESS", "CLOSED"},
    "IN_PROGRESS": {"RESOLVED", "ASSIGNED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set(),
}

def transition_ticket(ticket: SupportTicket, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = ticket.state
    allowed = TICKET_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise RuntimeError("Invalid transition")
    ticket.audit_trail.append(("STATE_TRANSITION", ticket.entity_id, cur, next_state, actor_id, timestamp_ms))
    ticket.state = next_state

def get_ticket_status(ticket: SupportTicket) -> Dict[str, Any]:
    return {"id": ticket.entity_id, "state": ticket.state, "closed": ticket.is_closed()}
'''
    }

    add_task(
        tid=2079,
        family="state_transitions",
        name="Support Ticket Workflow",
        class_tag="TRANSFER",
        issue="Incident INC-8203: Support ticket workflow allowed jumping directly from CREATED to RESOLVED without audit records.",
        traceback_text="FAILED tests/test_ticket_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["ticket_workflow.py"],
        repo=t2079_repo,
        hidden=t2079_hidden,
        ref=t2079_ref,
        mutant1=t2079_m1,
        mutant2=t2079_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Audit tuple structure", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION validation", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2080: Cloud Compute Instance Lifecycle (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2080_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "instance_fsm.py": '''"""Cloud compute VM lifecycle state machine and schemas."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class VirtualMachine:
    entity_id: str
    state: str = "PROVISIONING"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == "RUNNING"

VM_TRANSITIONS: Dict[str, Set[str]] = {
    "PROVISIONING": {"RUNNING", "TERMINATED"},
    "RUNNING": {"STOPPED", "TERMINATED"},
    "STOPPED": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}

def apply_vm_transition(vm: VirtualMachine, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Validates and applies compute lifecycle update."""
    cur = vm.state
    allowed = VM_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        # Erroneous exception and missing audit tuple in unpatched baseline
        raise ServiceError(code="ERR_VM_ILLEGAL_STATE", message="Invalid state jump")
    vm.state = target_state
''',
        "instance_controller.py": '''"""Cloud instance control plane orchestrator."""
from typing import Dict, Any
from instance_fsm import VirtualMachine, apply_vm_transition

def update_instance_state(vm: VirtualMachine, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Updates VM instance status."""
    apply_vm_transition(vm, next_state, actor_id, timestamp_ms)

def inspect_vm(vm: VirtualMachine) -> Dict[str, Any]:
    return {"id": vm.entity_id, "state": vm.state, "active": vm.is_active()}
''',
        "tests/test_instance.py": '''from instance_fsm import VirtualMachine
from instance_controller import update_instance_state, inspect_vm

def test_initial_vm():
    vm = VirtualMachine("vm-01")
    assert vm.state == "PROVISIONING"
    info = inspect_vm(vm)
    assert not info["active"]

def test_startup():
    vm = VirtualMachine("vm-01")
    update_instance_state(vm, "RUNNING", "system", 1700000000000)
    assert vm.state == "RUNNING"
'''
    }

    t2080_hidden = {
        "tests/test_instance_cases.py": '''import pytest
from errors import ServiceError
from instance_fsm import VirtualMachine
from instance_controller import update_instance_state

def test_case_1():
    vm = VirtualMachine("vm-101")
    update_instance_state(vm, "RUNNING", "user-admin", 1700000010000)
    assert len(vm.audit_trail) == 1
    assert vm.audit_trail[0] == ("STATE_TRANSITION", "vm-101", "PROVISIONING", "RUNNING", "user-admin", 1700000010000)

def test_case_2():
    vm = VirtualMachine("vm-202")
    # Illegal direct jump: PROVISIONING -> STOPPED
    with pytest.raises(ServiceError) as exc_info:
        update_instance_state(vm, "STOPPED", "user-admin", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2080_ref = {
        "instance_fsm.py": '''"""Cloud compute VM lifecycle state machine and schemas."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class VirtualMachine:
    entity_id: str
    state: str = "PROVISIONING"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == "RUNNING"

VM_TRANSITIONS: Dict[str, Set[str]] = {
    "PROVISIONING": {"RUNNING", "TERMINATED"},
    "RUNNING": {"STOPPED", "TERMINATED"},
    "STOPPED": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}

def apply_vm_transition(vm: VirtualMachine, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Validates and applies compute lifecycle update."""
    cur = vm.state
    allowed = VM_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {target_state} forbidden")
    vm.audit_trail.append(("STATE_TRANSITION", vm.entity_id, cur, target_state, actor_id, timestamp_ms))
    vm.state = target_state
'''
    }

    t2080_m1 = {
        "instance_controller.py": '''"""Cloud instance control plane orchestrator."""
from typing import Dict, Any
from instance_fsm import VirtualMachine, apply_vm_transition

def update_instance_state(vm: VirtualMachine, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    if next_state == "STOPPED" and vm.state == "PROVISIONING":
        return
    apply_vm_transition(vm, next_state, actor_id, timestamp_ms)

def inspect_vm(vm: VirtualMachine) -> Dict[str, Any]:
    return {"id": vm.entity_id, "state": vm.state, "active": vm.is_active()}
'''
    }

    t2080_m2 = {
        "instance_fsm.py": '''"""Cloud compute VM lifecycle state machine and schemas."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class VirtualMachine:
    entity_id: str
    state: str = "PROVISIONING"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == "RUNNING"

VM_TRANSITIONS: Dict[str, Set[str]] = {
    "PROVISIONING": {"RUNNING", "TERMINATED"},
    "RUNNING": {"STOPPED", "TERMINATED"},
    "STOPPED": {"RUNNING", "TERMINATED"},
    "TERMINATED": set(),
}

def apply_vm_transition(vm: VirtualMachine, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = vm.state
    allowed = VM_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message="Forbidden")
    vm.audit_trail.append(("INSTANCE_STATE_CHANGE", vm.entity_id, cur, target_state, actor_id, timestamp_ms))
    vm.state = target_state
'''
    }

    add_task(
        tid=2080,
        family="state_transitions",
        name="Cloud Compute Instance Lifecycle",
        class_tag="TRANSFER",
        issue="Incident INC-8204: Compute hypervisor raised non-standard error codes and lacked lifecycle transition auditing.",
        traceback_text="FAILED tests/test_instance_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["instance_controller.py"],
        repo=t2080_repo,
        hidden=t2080_hidden,
        ref=t2080_ref,
        mutant1=t2080_m1,
        mutant2=t2080_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Cloud VM audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION code", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2081: Fulfillment Order Workflow (TRANSFER, HRC=False, VTS=True)
    # =========================================================================
    t2081_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "fulfillment_models.py": '''"""Warehouse order fulfillment entities."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict

@dataclass
class FulfillmentOrder:
    entity_id: str
    state: str = "AWAITING_PAYMENT"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_delivered(self) -> bool:
        return self.state == "DELIVERED"

    def audit_count(self) -> int:
        return len(self.audit_trail)
''',
        "fulfillment_engine.py": '''"""Warehouse order fulfillment transition controller."""
from typing import Dict, Set, Any
from errors import ServiceError
from fulfillment_models import FulfillmentOrder

FULFILLMENT_TRANSITIONS: Dict[str, Set[str]] = {
    "AWAITING_PAYMENT": {"PAID", "CANCELLED"},
    "PAID": {"PICKING", "CANCELLED"},
    "PICKING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}

def transition_order_fulfillment(order: FulfillmentOrder, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions fulfillment order to target state."""
    cur = order.state
    # Unpatched baseline: sets state without validation or audit tuple
    order.state = target_state

def get_fulfillment_status(order: FulfillmentOrder) -> Dict[str, Any]:
    return {"id": order.entity_id, "state": order.state, "delivered": order.is_delivered()}
''',
        "tests/test_fulfillment.py": '''from fulfillment_models import FulfillmentOrder
from fulfillment_engine import transition_order_fulfillment, get_fulfillment_status

def test_initial_order():
    o = FulfillmentOrder("ord-1")
    assert o.state == "AWAITING_PAYMENT"
    assert o.audit_count() == 0
    st = get_fulfillment_status(o)
    assert not st["delivered"]

def test_pay_order():
    o = FulfillmentOrder("ord-1")
    transition_order_fulfillment(o, "PAID", "checkout", 1700000000000)
    assert o.state == "PAID"
'''
    }

    t2081_hidden = {
        "tests/test_fulfillment_cases.py": '''import pytest
from errors import ServiceError
from fulfillment_models import FulfillmentOrder
from fulfillment_engine import transition_order_fulfillment

def test_case_1():
    o = FulfillmentOrder("ord-101")
    transition_order_fulfillment(o, "PAID", "payment_gw", 1700000010000)
    assert len(o.audit_trail) == 1
    assert o.audit_trail[0] == ("STATE_TRANSITION", "ord-101", "AWAITING_PAYMENT", "PAID", "payment_gw", 1700000010000)

def test_case_2():
    o = FulfillmentOrder("ord-202")
    transition_order_fulfillment(o, "PAID", "payment_gw", 1700000010000)
    transition_order_fulfillment(o, "PICKING", "wh_staff", 1700000020000)
    transition_order_fulfillment(o, "SHIPPED", "courier", 1700000030000)
    # SHIPPED -> CANCELLED is illegal
    with pytest.raises(ServiceError) as exc_info:
        transition_order_fulfillment(o, "CANCELLED", "support", 1700000040000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2081_ref = {
        "fulfillment_engine.py": '''"""Warehouse order fulfillment transition controller."""
from typing import Dict, Set, Any
from errors import ServiceError
from fulfillment_models import FulfillmentOrder

FULFILLMENT_TRANSITIONS: Dict[str, Set[str]] = {
    "AWAITING_PAYMENT": {"PAID", "CANCELLED"},
    "PAID": {"PICKING", "CANCELLED"},
    "PICKING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}

def transition_order_fulfillment(order: FulfillmentOrder, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions fulfillment order to target state."""
    cur = order.state
    allowed = FULFILLMENT_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {target_state} forbidden")
    order.audit_trail.append(("STATE_TRANSITION", order.entity_id, cur, target_state, actor_id, timestamp_ms))
    order.state = target_state

def get_fulfillment_status(order: FulfillmentOrder) -> Dict[str, Any]:
    return {"id": order.entity_id, "state": order.state, "delivered": order.is_delivered()}
'''
    }

    t2081_m1 = {
        "fulfillment_engine.py": '''"""Warehouse order fulfillment transition controller."""
from typing import Dict, Set, Any
from errors import ServiceError
from fulfillment_models import FulfillmentOrder

FULFILLMENT_TRANSITIONS: Dict[str, Set[str]] = {
    "AWAITING_PAYMENT": {"PAID", "CANCELLED"},
    "PAID": {"PICKING", "CANCELLED"},
    "PICKING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}

def transition_order_fulfillment(order: FulfillmentOrder, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = order.state
    allowed = FULFILLMENT_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message="Bad transition")
    order.audit_trail.append(("state_transition", order.entity_id, cur, target_state, actor_id, timestamp_ms))
    order.state = target_state

def get_fulfillment_status(order: FulfillmentOrder) -> Dict[str, Any]:
    return {"id": order.entity_id, "state": order.state, "delivered": order.is_delivered()}
'''
    }

    t2081_m2 = {
        "fulfillment_engine.py": '''"""Warehouse order fulfillment transition controller."""
from typing import Dict, Set, Any
from errors import ServiceError
from fulfillment_models import FulfillmentOrder

FULFILLMENT_TRANSITIONS: Dict[str, Set[str]] = {
    "AWAITING_PAYMENT": {"PAID", "CANCELLED"},
    "PAID": {"PICKING", "CANCELLED"},
    "PICKING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}

def transition_order_fulfillment(order: FulfillmentOrder, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = order.state
    allowed = FULFILLMENT_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ValueError("Invalid transition")
    order.audit_trail.append(("STATE_TRANSITION", order.entity_id, cur, target_state, actor_id, timestamp_ms))
    order.state = target_state

def get_fulfillment_status(order: FulfillmentOrder) -> Dict[str, Any]:
    return {"id": order.entity_id, "state": order.state, "delivered": order.is_delivered()}
'''
    }

    add_task(
        tid=2081,
        family="state_transitions",
        name="Fulfillment Order Workflow",
        class_tag="TRANSFER",
        issue="Incident INC-8205: Warehouse management system permitted cancelling orders after shipment without audit log.",
        traceback_text="FAILED tests/test_fulfillment_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["fulfillment_engine.py"],
        repo=t2081_repo,
        hidden=t2081_hidden,
        ref=t2081_ref,
        mutant1=t2081_m1,
        mutant2=t2081_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Order transition audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on cancelled post-shipped", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2082: Pull Request Review Lifecycle (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2082_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "pr_fsm.py": '''"""Code review pull request entities and state machine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class PullRequest:
    entity_id: str
    state: str = "DRAFT"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_open(self) -> bool:
        return self.state in {"OPEN", "REVIEWED", "APPROVED"}

PR_TRANSITIONS: Dict[str, Set[str]] = {
    "DRAFT": {"OPEN", "CLOSED"},
    "OPEN": {"REVIEWED", "CLOSED"},
    "REVIEWED": {"APPROVED", "OPEN", "CLOSED"},
    "APPROVED": {"MERGED", "OPEN", "CLOSED"},
    "MERGED": set(),
    "CLOSED": set(),
}

def execute_pr_state_change(pr: PullRequest, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Executes state transition on pull request."""
    cur = pr.state
    allowed = PR_TRANSITIONS.get(cur, set())
    if new_state not in allowed:
        # Erroneous code in unpatched baseline
        raise ServiceError(code="ERR_PR_ILLEGAL_STATE", message="Disallowed state")
    pr.state = new_state
''',
        "pr_service.py": '''"""Code collaboration platform PR service."""
from typing import Dict, Any
from pr_fsm import PullRequest, execute_pr_state_change

def update_pr_lifecycle(pr: PullRequest, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Dispatches PR state update."""
    execute_pr_state_change(pr, target_state, actor_id, timestamp_ms)

def get_pr_status(pr: PullRequest) -> Dict[str, Any]:
    return {"id": pr.entity_id, "state": pr.state, "open": pr.is_open()}
''',
        "tests/test_pr.py": '''from pr_fsm import PullRequest
from pr_service import update_pr_lifecycle, get_pr_status

def test_initial_pr():
    pr = PullRequest("pr-10")
    assert pr.state == "DRAFT"
    st = get_pr_status(pr)
    assert not st["open"]

def test_open_pr():
    pr = PullRequest("pr-10")
    update_pr_lifecycle(pr, "OPEN", "dev", 1700000000000)
    assert pr.state == "OPEN"
'''
    }

    t2082_hidden = {
        "tests/test_pr_cases.py": '''import pytest
from errors import ServiceError
from pr_fsm import PullRequest
from pr_service import update_pr_lifecycle

def test_case_1():
    pr = PullRequest("pr-505")
    update_pr_lifecycle(pr, "OPEN", "developer-1", 1700000010000)
    assert len(pr.audit_trail) == 1
    assert pr.audit_trail[0] == ("STATE_TRANSITION", "pr-505", "DRAFT", "OPEN", "developer-1", 1700000010000)

def test_case_2():
    pr = PullRequest("pr-606")
    # Illegal direct jump: DRAFT -> MERGED
    with pytest.raises(ServiceError) as exc_info:
        update_pr_lifecycle(pr, "MERGED", "developer-1", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2082_ref = {
        "pr_fsm.py": '''"""Code review pull request entities and state machine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class PullRequest:
    entity_id: str
    state: str = "DRAFT"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_open(self) -> bool:
        return self.state in {"OPEN", "REVIEWED", "APPROVED"}

PR_TRANSITIONS: Dict[str, Set[str]] = {
    "DRAFT": {"OPEN", "CLOSED"},
    "OPEN": {"REVIEWED", "CLOSED"},
    "REVIEWED": {"APPROVED", "OPEN", "CLOSED"},
    "APPROVED": {"MERGED", "OPEN", "CLOSED"},
    "MERGED": set(),
    "CLOSED": set(),
}

def execute_pr_state_change(pr: PullRequest, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Executes state transition on pull request."""
    cur = pr.state
    allowed = PR_TRANSITIONS.get(cur, set())
    if new_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {new_state} disallowed")
    pr.audit_trail.append(("STATE_TRANSITION", pr.entity_id, cur, new_state, actor_id, timestamp_ms))
    pr.state = new_state
'''
    }

    t2082_m1 = {
        "pr_service.py": '''"""Code collaboration platform PR service."""
from typing import Dict, Any
from pr_fsm import PullRequest, execute_pr_state_change

def update_pr_lifecycle(pr: PullRequest, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    if target_state == "MERGED" and pr.state == "DRAFT":
        return
    execute_pr_state_change(pr, target_state, actor_id, timestamp_ms)

def get_pr_status(pr: PullRequest) -> Dict[str, Any]:
    return {"id": pr.entity_id, "state": pr.state, "open": pr.is_open()}
'''
    }

    t2082_m2 = {
        "pr_fsm.py": '''"""Code review pull request entities and state machine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class PullRequest:
    entity_id: str
    state: str = "DRAFT"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_open(self) -> bool:
        return self.state in {"OPEN", "REVIEWED", "APPROVED"}

PR_TRANSITIONS: Dict[str, Set[str]] = {
    "DRAFT": {"OPEN", "CLOSED"},
    "OPEN": {"REVIEWED", "CLOSED"},
    "REVIEWED": {"APPROVED", "OPEN", "CLOSED"},
    "APPROVED": {"MERGED", "OPEN", "CLOSED"},
    "MERGED": set(),
    "CLOSED": set(),
}

def execute_pr_state_change(pr: PullRequest, new_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = pr.state
    allowed = PR_TRANSITIONS.get(cur, set())
    if new_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message="Bad transition")
    pr.audit_trail.append(("STATE_TRANSITION", pr.entity_id, cur, new_state, actor_id))
    pr.state = new_state
'''
    }

    add_task(
        tid=2082,
        family="state_transitions",
        name="Pull Request Review Lifecycle",
        class_tag="TRANSFER",
        issue="Incident INC-8206: VCS gateway code review lifecycle raised non-conforming error codes and dropped transition audit tuples.",
        traceback_text="FAILED tests/test_pr_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["pr_service.py"],
        repo=t2082_repo,
        hidden=t2082_hidden,
        ref=t2082_ref,
        mutant1=t2082_m1,
        mutant2=t2082_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: PR state audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION error code", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2083: Subscription Account Billing State (TRANSFER, HRC=False, VTS=True)
    # =========================================================================
    t2083_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "subscription_models.py": '''"""SaaS subscription customer account entities."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict

@dataclass
class SubscriptionAccount:
    entity_id: str
    state: str = "TRIAL"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_billable(self) -> bool:
        return self.state in {"ACTIVE", "PAST_DUE"}

    def audit_count(self) -> int:
        return len(self.audit_trail)
''',
        "subscription_fsm.py": '''"""Subscription billing state transition logic."""
from typing import Dict, Set, Any
from errors import ServiceError
from subscription_models import SubscriptionAccount

SUBSCRIPTION_TRANSITIONS: Dict[str, Set[str]] = {
    "TRIAL": {"ACTIVE", "CANCELED", "EXPIRED"},
    "ACTIVE": {"PAST_DUE", "CANCELED"},
    "PAST_DUE": {"ACTIVE", "CANCELED", "EXPIRED"},
    "CANCELED": set(),
    "EXPIRED": set(),
}

def transition_subscription(account: SubscriptionAccount, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions subscription to new state."""
    cur = account.state
    # Unpatched baseline: changes state directly without validation or audit tuple
    account.state = next_state

def get_subscription_overview(account: SubscriptionAccount) -> Dict[str, Any]:
    return {"id": account.entity_id, "state": account.state, "billable": account.is_billable()}
''',
        "tests/test_subscription.py": '''from subscription_models import SubscriptionAccount
from subscription_fsm import transition_subscription, get_subscription_overview

def test_initial_sub():
    s = SubscriptionAccount("sub-1")
    assert s.state == "TRIAL"
    assert s.audit_count() == 0
    overview = get_subscription_overview(s)
    assert not overview["billable"]

def test_activate():
    s = SubscriptionAccount("sub-1")
    transition_subscription(s, "ACTIVE", "stripe", 1700000000000)
    assert s.state == "ACTIVE"
'''
    }

    t2083_hidden = {
        "tests/test_subscription_cases.py": '''import pytest
from errors import ServiceError
from subscription_models import SubscriptionAccount
from subscription_fsm import transition_subscription

def test_case_1():
    s = SubscriptionAccount("sub-808")
    transition_subscription(s, "ACTIVE", "billing_sys", 1700000010000)
    assert len(s.audit_trail) == 1
    assert s.audit_trail[0] == ("STATE_TRANSITION", "sub-808", "TRIAL", "ACTIVE", "billing_sys", 1700000010000)

def test_case_2():
    s = SubscriptionAccount("sub-909")
    transition_subscription(s, "CANCELED", "customer", 1700000010000)
    # CANCELED is terminal: CANCELED -> ACTIVE is illegal
    with pytest.raises(ServiceError) as exc_info:
        transition_subscription(s, "ACTIVE", "customer", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2083_ref = {
        "subscription_fsm.py": '''"""Subscription billing state transition logic."""
from typing import Dict, Set, Any
from errors import ServiceError
from subscription_models import SubscriptionAccount

SUBSCRIPTION_TRANSITIONS: Dict[str, Set[str]] = {
    "TRIAL": {"ACTIVE", "CANCELED", "EXPIRED"},
    "ACTIVE": {"PAST_DUE", "CANCELED"},
    "PAST_DUE": {"ACTIVE", "CANCELED", "EXPIRED"},
    "CANCELED": set(),
    "EXPIRED": set(),
}

def transition_subscription(account: SubscriptionAccount, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Transitions subscription to new state."""
    cur = account.state
    allowed = SUBSCRIPTION_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {next_state} invalid")
    account.audit_trail.append(("STATE_TRANSITION", account.entity_id, cur, next_state, actor_id, timestamp_ms))
    account.state = next_state

def get_subscription_overview(account: SubscriptionAccount) -> Dict[str, Any]:
    return {"id": account.entity_id, "state": account.state, "billable": account.is_billable()}
'''
    }

    t2083_m1 = {
        "subscription_fsm.py": '''"""Subscription billing state transition logic."""
from typing import Dict, Set, Any
from errors import ServiceError
from subscription_models import SubscriptionAccount

SUBSCRIPTION_TRANSITIONS: Dict[str, Set[str]] = {
    "TRIAL": {"ACTIVE", "CANCELED", "EXPIRED"},
    "ACTIVE": {"PAST_DUE", "CANCELED"},
    "PAST_DUE": {"ACTIVE", "CANCELED", "EXPIRED"},
    "CANCELED": set(),
    "EXPIRED": set(),
}

def transition_subscription(account: SubscriptionAccount, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = account.state
    allowed = SUBSCRIPTION_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {next_state} invalid")
    account.audit_trail.append(("STATE_CHANGED", account.entity_id, cur, next_state, actor_id, timestamp_ms))
    account.state = next_state

def get_subscription_overview(account: SubscriptionAccount) -> Dict[str, Any]:
    return {"id": account.entity_id, "state": account.state, "billable": account.is_billable()}
'''
    }

    t2083_m2 = {
        "subscription_fsm.py": '''"""Subscription billing state transition logic."""
from typing import Dict, Set, Any
from errors import ServiceError
from subscription_models import SubscriptionAccount

SUBSCRIPTION_TRANSITIONS: Dict[str, Set[str]] = {
    "TRIAL": {"ACTIVE", "CANCELED", "EXPIRED"},
    "ACTIVE": {"PAST_DUE", "CANCELED"},
    "PAST_DUE": {"ACTIVE", "CANCELED", "EXPIRED"},
    "CANCELED": set(),
    "EXPIRED": set(),
}

def transition_subscription(account: SubscriptionAccount, next_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = account.state
    allowed = SUBSCRIPTION_TRANSITIONS.get(cur, set())
    if next_state not in allowed:
        raise ServiceError(code="ERR_SUBSCRIPTION_ERROR", message="Cannot transition")
    account.audit_trail.append(("STATE_TRANSITION", account.entity_id, cur, next_state, actor_id, timestamp_ms))
    account.state = next_state

def get_subscription_overview(account: SubscriptionAccount) -> Dict[str, Any]:
    return {"id": account.entity_id, "state": account.state, "billable": account.is_billable()}
'''
    }

    add_task(
        tid=2083,
        family="state_transitions",
        name="Subscription Account Billing State",
        class_tag="TRANSFER",
        issue="Incident INC-8207: Recurring subscription service reactivated canceled accounts without validation or audit trail.",
        traceback_text="FAILED tests/test_subscription_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["subscription_fsm.py"],
        repo=t2083_repo,
        hidden=t2083_hidden,
        ref=t2083_ref,
        mutant1=t2083_m1,
        mutant2=t2083_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Subscription transition audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION from terminal state", "No", "TRANSFER")
        ]
    )

    # =========================================================================
    # Task 2084: Batch Processing Job Lifecycle (TRANSFER, HRC=True, VTS=False)
    # =========================================================================
    t2084_repo = {
        "errors.py": '''"""Domain service exception classes."""
class ServiceError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
''',
        "job_fsm.py": '''"""Batch compute job entities and lifecycle transition engine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class BatchJob:
    entity_id: str
    state: str = "SUBMITTED"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finished(self) -> bool:
        return self.state in {"COMPLETED", "FAILED", "ABORTED"}

JOB_TRANSITIONS: Dict[str, Set[str]] = {
    "SUBMITTED": {"QUEUED", "ABORTED"},
    "QUEUED": {"RUNNING", "ABORTED"},
    "RUNNING": {"COMPLETED", "FAILED", "ABORTED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "ABORTED": set(),
}

def apply_job_transition(job: BatchJob, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Executes state transition for batch job."""
    cur = job.state
    allowed = JOB_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        # Erroneous exception in unpatched baseline
        raise ServiceError(code="ERR_JOB_BAD_STATE", message="Bad state")
    job.state = target_state
''',
        "job_orchestrator.py": '''"""Distributed job scheduling orchestrator."""
from typing import Dict, Any
from job_fsm import BatchJob, apply_job_transition

def advance_job_state(job: BatchJob, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Advances batch job to target state."""
    apply_job_transition(job, target_state, actor_id, timestamp_ms)

def inspect_job_progress(job: BatchJob) -> Dict[str, Any]:
    return {"id": job.entity_id, "state": job.state, "finished": job.is_finished()}
''',
        "tests/test_job.py": '''from job_fsm import BatchJob
from job_orchestrator import advance_job_state, inspect_job_progress

def test_initial_job():
    j = BatchJob("job-01")
    assert j.state == "SUBMITTED"
    info = inspect_job_progress(j)
    assert not info["finished"]

def test_queue_job():
    j = BatchJob("job-01")
    advance_job_state(j, "QUEUED", "scheduler", 1700000000000)
    assert j.state == "QUEUED"
'''
    }

    t2084_hidden = {
        "tests/test_job_cases.py": '''import pytest
from errors import ServiceError
from job_fsm import BatchJob
from job_orchestrator import advance_job_state

def test_case_1():
    j = BatchJob("job-404")
    advance_job_state(j, "QUEUED", "scheduler", 1700000010000)
    assert len(j.audit_trail) == 1
    assert j.audit_trail[0] == ("STATE_TRANSITION", "job-404", "SUBMITTED", "QUEUED", "scheduler", 1700000010000)

def test_case_2():
    j = BatchJob("job-505")
    # Illegal direct jump: SUBMITTED -> RUNNING
    with pytest.raises(ServiceError) as exc_info:
        advance_job_state(j, "RUNNING", "scheduler", 1700000020000)
    assert exc_info.value.code == "ERR_INVALID_TRANSITION"
'''
    }

    t2084_ref = {
        "job_fsm.py": '''"""Batch compute job entities and lifecycle transition engine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class BatchJob:
    entity_id: str
    state: str = "SUBMITTED"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finished(self) -> bool:
        return self.state in {"COMPLETED", "FAILED", "ABORTED"}

JOB_TRANSITIONS: Dict[str, Set[str]] = {
    "SUBMITTED": {"QUEUED", "ABORTED"},
    "QUEUED": {"RUNNING", "ABORTED"},
    "RUNNING": {"COMPLETED", "FAILED", "ABORTED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "ABORTED": set(),
}

def apply_job_transition(job: BatchJob, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    """Executes state transition for batch job."""
    cur = job.state
    allowed = JOB_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ServiceError(code="ERR_INVALID_TRANSITION", message=f"Transition {cur} -> {target_state} forbidden")
    job.audit_trail.append(("STATE_TRANSITION", job.entity_id, cur, target_state, actor_id, timestamp_ms))
    job.state = target_state
'''
    }

    t2084_m1 = {
        "job_orchestrator.py": '''"""Distributed job scheduling orchestrator."""
from typing import Dict, Any
from job_fsm import BatchJob, apply_job_transition

def advance_job_state(job: BatchJob, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    if target_state == "RUNNING" and job.state == "SUBMITTED":
        return
    apply_job_transition(job, target_state, actor_id, timestamp_ms)

def inspect_job_progress(job: BatchJob) -> Dict[str, Any]:
    return {"id": job.entity_id, "state": job.state, "finished": job.is_finished()}
'''
    }

    t2084_m2 = {
        "job_fsm.py": '''"""Batch compute job entities and lifecycle transition engine."""
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Set
from errors import ServiceError

@dataclass
class BatchJob:
    entity_id: str
    state: str = "SUBMITTED"
    audit_trail: List[Tuple[Any, ...]] = field(default_factory=list)

    def is_finished(self) -> bool:
        return self.state in {"COMPLETED", "FAILED", "ABORTED"}

JOB_TRANSITIONS: Dict[str, Set[str]] = {
    "SUBMITTED": {"QUEUED", "ABORTED"},
    "QUEUED": {"RUNNING", "ABORTED"},
    "RUNNING": {"COMPLETED", "FAILED", "ABORTED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "ABORTED": set(),
}

def apply_job_transition(job: BatchJob, target_state: str, actor_id: str, timestamp_ms: int) -> None:
    cur = job.state
    allowed = JOB_TRANSITIONS.get(cur, set())
    if target_state not in allowed:
        raise ValueError("Invalid transition")
    job.audit_trail.append(("STATE_TRANSITION", job.entity_id, cur, target_state, actor_id, timestamp_ms))
    job.state = target_state
'''
    }

    add_task(
        tid=2084,
        family="state_transitions",
        name="Batch Processing Job Lifecycle",
        class_tag="TRANSFER",
        issue="Incident INC-8208: Batch job orchestrator permitted invalid state transitions and raised non-standard error codes.",
        traceback_text="FAILED tests/test_job_cases.py::test_case_1 - AssertionError: assert 0 == 1",
        traceback_files=["job_orchestrator.py"],
        repo=t2084_repo,
        hidden=t2084_hidden,
        ref=t2084_ref,
        mutant1=t2084_m1,
        mutant2=t2084_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H15"],
        assertions=[
            ("test_case_1", "HANDBOOK.md Rule H15: Batch job transition audit tuple", "No", "TRANSFER"),
            ("test_case_2", "HANDBOOK.md Rule H15: ERR_INVALID_TRANSITION on direct jump", "No", "TRANSFER")
        ]
    )

    print("Family 14 registered (Tasks 2077-2084).")
