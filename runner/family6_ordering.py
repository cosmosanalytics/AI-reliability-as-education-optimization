"""Family 6: event_ordering (Tasks 2021 - 2024).

Governing Rule: Rule H07 (Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking).
Competing Alternatives: Sorting on priority only (unstable), chronological / ID tiebreaker, raw payload string tiebreaker.
Target: 40-120 non-test lines across 3-4 files. All files on reachability path (zero decoys).
"""

def register_family_6(add_task):
    # =========================================================================
    # Task 2021: Priority Job Queue Dispatcher (STATED, HRC=False, VTS=False)
    # =========================================================================
    t2021_repo = {
        "job.py": '''"""Background worker job schemas."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class JobItem:
    job_id: int
    priority: int
    payload: str
    status: str = "PENDING"
    retry_count: int = 0

    def is_pending(self) -> bool:
        return self.status == "PENDING"

    def mark_completed(self) -> None:
        self.status = "COMPLETED"

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "id": self.job_id,
            "priority": self.priority,
            "payload": self.payload,
            "status": self.status,
        }
''',
        "queue_metrics.py": '''"""Job queue depth monitoring."""
from typing import List
from job import JobItem

def compute_queue_load(jobs: List[JobItem]) -> int:
    return sum(j.priority for j in jobs)

def count_pending_jobs(jobs: List[JobItem]) -> int:
    return sum(1 for j in jobs if j.is_pending())
''',
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem
from queue_metrics import compute_queue_load

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    """Order jobs for dispatch processing.
    Ordering contract:
    - Sort jobs by descending priority.
    - Tiebreaker: break ties on equal priority deterministically using payload SHA-256 digest in ascending lexicographical order.
    """
    _ = compute_queue_load(jobs)
    return sorted(jobs, key=lambda j: (-j.priority, j.job_id))

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]

def get_highest_priority_job(jobs: List[JobItem]):
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[0] if ordered else None
''',
        "tests/test_dispatcher.py": '''from job import JobItem
from dispatcher import order_jobs_for_dispatch

def test_distinct_priorities():
    j1 = JobItem(1, 10, "low")
    j2 = JobItem(2, 50, "high")
    ordered = order_jobs_for_dispatch([j1, j2])
    assert ordered[0].job_id == 2
    assert ordered[1].job_id == 1
'''
    }

    t2021_hidden = {
        "tests/test_dispatcher_cases.py": '''from job import JobItem
from dispatcher import order_jobs_for_dispatch

def test_equal_priority_tiebreak():
    j1 = JobItem(1, 100, "payload_a")
    j2 = JobItem(2, 100, "payload_b")
    ordered = order_jobs_for_dispatch([j1, j2])
    assert ordered[0].job_id == 2
    assert ordered[1].job_id == 1
'''
    }

    t2021_ref = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
import hashlib
from typing import List
from job import JobItem
from queue_metrics import compute_queue_load

def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    """Order jobs for dispatch processing.
    Ordering contract:
    - Sort jobs by descending priority.
    - Tiebreaker: break ties on equal priority deterministically using payload SHA-256 digest in ascending lexicographical order.
    """
    _ = compute_queue_load(jobs)
    return sorted(jobs, key=lambda j: (-j.priority, _hash_payload(j.payload)))

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]
'''
    }

    t2021_m1 = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem
from queue_metrics import compute_queue_load

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    # Mutant 1: Break ties by job_id
    _ = compute_queue_load(jobs)
    return sorted(jobs, key=lambda j: (-j.priority, j.job_id))
'''
    }

    t2021_m2 = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem
from queue_metrics import compute_queue_load

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    # Mutant 2: Break ties by raw payload string
    _ = compute_queue_load(jobs)
    return sorted(jobs, key=lambda j: (-j.priority, j.payload))
'''
    }

    add_task(
        tid=2021,
        family="event_ordering",
        name="Priority Job Queue Dispatcher",
        class_tag="STATED",
        issue="Worker queue anomaly WRK-112: Background worker processed equal-priority tasks out of order under simultaneous job enqueue bursts.",
        traceback_text="FAILED tests/test_dispatcher_cases.py::test_equal_priority_tiebreak - AssertionError: assert 1 == 2",
        traceback_files=["dispatcher.py"],
        repo=t2021_repo,
        hidden=t2021_hidden,
        ref=t2021_ref,
        mutant1=t2021_m1,
        mutant2=t2021_m2,
        hidden_root_cause=False,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H07"],
        assertions=[
            ("test_equal_priority_tiebreak", "dispatcher.py docstring: 'Sort jobs by descending priority ... payload SHA-256 digest in ascending lexicographical order'", "Yes", "STATED")
        ]
    )

    # =========================================================================
    # Task 2022: Notification Batch Sorter (TAUGHT, HRC=False, VTS=True)
    # =========================================================================
    t2022_repo = {
        "notification.py": '''"""Notification queue payload."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class NotificationMessage:
    msg_id: int
    priority: int
    payload: str
    channel: str = "PUSH"
    read: bool = False

    def is_urgent(self) -> bool:
        return self.priority >= 10

    def mark_read(self) -> None:
        self.read = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.msg_id,
            "priority": self.priority,
            "payload": self.payload,
            "channel": self.channel,
        }
''',
        "formatter.py": '''"""Notification payload formatters."""
from typing import List
from notification import NotificationMessage

def format_batch_summary(batch: List[NotificationMessage]) -> str:
    return f"Batch size={len(batch)}"

def group_by_channel(batch: List[NotificationMessage]) -> dict:
    res = {}
    for m in batch:
        res.setdefault(m.channel, []).append(m)
    return res
''',
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage
from formatter import format_batch_summary

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    """Sort notification messages in batch by priority level."""
    _ = format_batch_summary(batch)
    return sorted(batch, key=lambda m: (-m.priority, m.msg_id))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]

def get_oldest_notification(batch: List[NotificationMessage]):
    if not batch:
        return None
    return batch[0]
''',
        "tests/test_sorter.py": '''from notification import NotificationMessage
from sorter import sort_notification_batch

def test_priority_ordering():
    m1 = NotificationMessage(1, 10, "info")
    m2 = NotificationMessage(2, 50, "alert")
    res = sort_notification_batch([m1, m2])
    assert res[0].msg_id == 2

def test_batch_reordering():
    m1 = NotificationMessage(1, 20, "x")
    m2 = NotificationMessage(2, 30, "y")
    res = sort_notification_batch([m1, m2])
    assert res[0].priority > res[1].priority
'''
    }

    t2022_hidden = {
        "tests/test_sorter_cases.py": '''from notification import NotificationMessage
from sorter import sort_notification_batch

def test_notification_sha256_tiebreak():
    m1 = NotificationMessage(101, 10, "payload_a")
    m2 = NotificationMessage(102, 10, "payload_b")
    res = sort_notification_batch([m1, m2])
    assert res[0].msg_id == 102
    assert res[1].msg_id == 101
'''
    }

    t2022_ref = {
        "sorter.py": '''"""Notification priority batch sorter."""
import hashlib
from typing import List
from notification import NotificationMessage
from formatter import format_batch_summary

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    """Sort notification messages in batch by priority level."""
    _ = format_batch_summary(batch)
    return sorted(batch, key=lambda m: (-m.priority, hashlib.sha256(m.payload.encode("utf-8")).hexdigest()))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]
'''
    }

    t2022_m1 = {
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage
from formatter import format_batch_summary

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    # Mutant 1: tiebreak by msg_id
    _ = format_batch_summary(batch)
    return sorted(batch, key=lambda m: (-m.priority, m.msg_id))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]
'''
    }

    t2022_m2 = {
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage
from formatter import format_batch_summary

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    # Mutant 2: tiebreak by raw payload string
    _ = format_batch_summary(batch)
    return sorted(batch, key=lambda m: (-m.priority, m.payload))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]
'''
    }

    add_task(
        tid=2022,
        family="event_ordering",
        name="Notification Batch Sorter",
        class_tag="TAUGHT",
        issue="Delivery alert NOTIF-702: Urgent user alerts with identical priority tiers were delivered out of deterministic order.",
        traceback_text="FAILED tests/test_sorter_cases.py::test_notification_sha256_tiebreak - AssertionError: assert 101 == 102",
        traceback_files=["sorter.py"],
        repo=t2022_repo,
        hidden=t2022_hidden,
        ref=t2022_ref,
        mutant1=t2022_m1,
        mutant2=t2022_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H07"],
        assertions=[
            ("test_notification_sha256_tiebreak", "HANDBOOK.md Rule H07: Deterministic SHA-256 tie-breaking", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2023: Task Scheduler Queue Rebalancer (DISTRACTOR, HRC=False, VTS=True)
    # =========================================================================
    t2023_repo = {
        "task_item.py": '''"""Scheduled task models."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ScheduledTask:
    task_id: int
    weight: int
    payload: str = ""
    active: bool = True
    assigned_worker: Optional[str] = None

    def is_heavy(self) -> bool:
        return self.weight >= 50

    def assign(self, worker_id: str) -> None:
        self.assigned_worker = worker_id

    def to_summary(self) -> Dict[str, Any]:
        return {
            "id": self.task_id,
            "weight": self.weight,
            "payload": self.payload,
        }
''',
        "metrics.py": '''"""Task queue depth metrics."""
from typing import List
from task_item import ScheduledTask

def total_pending_weight(tasks: List[ScheduledTask]) -> int:
    return sum(t.weight for t in tasks)

def average_task_weight(tasks: List[ScheduledTask]) -> float:
    return total_pending_weight(tasks) / len(tasks) if tasks else 0.0
''',
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask
from metrics import total_pending_weight

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    """Rebalance scheduled task list.
    Ordering contract:
    - Sort tasks by weight in descending order.
    - Tiebreaker: ties in priority MUST be broken by ascending chronological registration ID (task_id), do NOT compute SHA-256 digests.
    """
    _ = total_pending_weight(tasks)
    return sorted(tasks, key=lambda t: (t.weight, t.task_id))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None

def filter_active_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    return [t for t in tasks if t.active]
''',
        "tests/test_rebalancer.py": '''from task_item import ScheduledTask
from rebalancer import rebalance_tasks

def test_basic_rebalance():
    t1 = ScheduledTask(1, 10, "a")
    t2 = ScheduledTask(2, 50, "b")
    res = rebalance_tasks([t1, t2])
    assert res[0].weight == 50

def test_weight_ordering():
    t1 = ScheduledTask(1, 5, "a")
    t2 = ScheduledTask(2, 20, "b")
    assert rebalance_tasks([t1, t2])[0].task_id == 2
'''
    }

    t2023_hidden = {
        "tests/test_rebalancer_cases.py": '''from task_item import ScheduledTask
from rebalancer import rebalance_tasks

def test_task_id_tiebreak():
    t1 = ScheduledTask(10, 100, "payload_a")
    t2 = ScheduledTask(20, 100, "payload_b")
    res = rebalance_tasks([t2, t1])
    assert res[0].task_id == 10
    assert res[1].task_id == 20
'''
    }

    t2023_ref = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask
from metrics import total_pending_weight

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    """Rebalance scheduled task list.
    Ordering contract:
    - Sort tasks by weight in descending order.
    - Tiebreaker: ties in priority MUST be broken by ascending chronological registration ID (task_id), do NOT compute SHA-256 digests.
    """
    _ = total_pending_weight(tasks)
    return sorted(tasks, key=lambda t: (-t.weight, t.task_id))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    t2023_m1 = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
import hashlib
from typing import List, Optional
from task_item import ScheduledTask
from metrics import total_pending_weight

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    # Mutant 1: Blindly computes SHA-256 tiebreak per H07
    _ = total_pending_weight(tasks)
    return sorted(tasks, key=lambda t: (-t.weight, hashlib.sha256(t.payload.encode()).hexdigest()))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    t2023_m2 = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask
from metrics import total_pending_weight

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    # Mutant 2: Reverse task_id
    _ = total_pending_weight(tasks)
    return sorted(tasks, key=lambda t: (-t.weight, -t.task_id))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    add_task(
        tid=2023,
        family="event_ordering",
        name="Task Scheduler Queue Rebalancer",
        class_tag="DISTRACTOR",
        issue="Task scheduler incident SCHED-404: Low-weight background tasks scheduled before heavy priority jobs after queue rebalance.",
        traceback_text="FAILED tests/test_rebalancer.py::test_weight_ordering - AssertionError: assert 1 == 2",
        traceback_files=["rebalancer.py"],
        repo=t2023_repo,
        hidden=t2023_hidden,
        ref=t2023_ref,
        mutant1=t2023_m1,
        mutant2=t2023_m2,
        hidden_root_cause=False,
        visible_test_sensitive=True,
        root_cause_only_with_exploration=False,
        handbook_citations=["Rule H07"],
        assertions=[
            ("test_task_id_tiebreak", "rebalancer.py docstring: 'ties in priority MUST be broken by ascending chronological registration ID (task_id), do NOT compute SHA-256 digests'", "Yes", "DISTRACTOR")
        ]
    )

    # =========================================================================
    # Task 2024: Event Stream Ingestion Sequencer (TAUGHT, HRC=True, VTS=False)
    # =========================================================================
    t2024_repo = {
        "event_packet.py": '''"""Stream event packet model."""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class EventPacket:
    stream_id: str
    severity: int
    payload: str
    topic: str = "telemetry"
    processed: bool = False

    def is_critical(self) -> bool:
        return self.severity >= 9

    def mark_processed(self) -> None:
        self.processed = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "severity": self.severity,
            "payload": self.payload,
            "topic": self.topic,
        }
''',
        "sort_helper.py": '''"""Internal stream sorting helper."""
from typing import List
from event_packet import EventPacket

def order_packets(packets: List[EventPacket]) -> List[EventPacket]:
    return sorted(packets, key=lambda p: (-p.severity, p.stream_id))

def get_max_severity(packets: List[EventPacket]) -> int:
    return max((p.severity for p in packets), default=0)

def count_critical_packets(packets: List[EventPacket]) -> int:
    return sum(1 for p in packets if p.is_critical())
''',
        "sequencer.py": '''"""Stream event sequencer."""
from typing import List
from sort_helper import order_packets, get_max_severity
from event_packet import EventPacket

def sequence_stream_batch(packets: List[EventPacket]) -> List[EventPacket]:
    """Sequence event packets by severity."""
    return order_packets(packets)

def get_highest_priority_packet(packets: List[EventPacket]):
    ordered = sequence_stream_batch(packets)
    return ordered[0] if ordered else None

def get_batch_severity_peak(packets: List[EventPacket]) -> int:
    return get_max_severity(packets)
''',
        "tests/test_sequencer.py": '''from event_packet import EventPacket
from sequencer import sequence_stream_batch

def test_nominal_severity():
    p1 = EventPacket("s1", 1, "low")
    p2 = EventPacket("s2", 5, "high")
    res = sequence_stream_batch([p1, p2])
    assert res[0].severity == 5
'''
    }

    t2024_hidden = {
        "tests/test_sequencer_cases.py": '''from event_packet import EventPacket
from sequencer import sequence_stream_batch
from sort_helper import order_packets

def test_stream_sequencing():
    p1 = EventPacket("s1", 10, "payload_a")
    p2 = EventPacket("s2", 10, "payload_b")
    res = sequence_stream_batch([p1, p2])
    assert res[0].stream_id == "s2"
    assert res[1].stream_id == "s1"

def test_sort_helper_contract():
    p1 = EventPacket("a", 5, "payload_a")
    p2 = EventPacket("b", 5, "payload_b")
    assert order_packets([p1, p2])[0].stream_id == "b"
'''
    }

    t2024_ref = {
        "sort_helper.py": '''"""Internal stream sorting helper."""
import hashlib
from typing import List
from event_packet import EventPacket

def order_packets(packets: List[EventPacket]) -> List[EventPacket]:
    return sorted(packets, key=lambda p: (-p.severity, hashlib.sha256(p.payload.encode("utf-8")).hexdigest()))

def get_max_severity(packets: List[EventPacket]) -> int:
    return max((p.severity for p in packets), default=0)
'''
    }

    t2024_m1 = {
        "sequencer.py": '''"""Stream event sequencer."""
import hashlib
from typing import List
from sort_helper import order_packets
from event_packet import EventPacket

def sequence_stream_batch(packets: List[EventPacket]) -> List[EventPacket]:
    # Mutant 1: Wrong file edit (HRC violation)
    return sorted(order_packets(packets), key=lambda p: (-p.severity, hashlib.sha256(p.payload.encode("utf-8")).hexdigest()))

def get_highest_priority_packet(packets: List[EventPacket]):
    ordered = sequence_stream_batch(packets)
    return ordered[0] if ordered else None
'''
    }

    t2024_m2 = {
        "sort_helper.py": '''"""Internal stream sorting helper."""
from typing import List
from event_packet import EventPacket

def order_packets(packets: List[EventPacket]) -> List[EventPacket]:
    # Mutant 2: Break ties by stream_id
    return sorted(packets, key=lambda p: (-p.severity, p.stream_id))

def get_max_severity(packets: List[EventPacket]) -> int:
    return max((p.severity for p in packets), default=0)
'''
    }

    add_task(
        tid=2024,
        family="event_ordering",
        name="Event Stream Ingestion Sequencer",
        class_tag="TAUGHT",
        issue="Data pipeline crash STRM-308: Out-of-order stream tiebreaker caused state replication desync during high-severity packet bursts.",
        traceback_text="FAILED tests/test_sequencer_cases.py::test_stream_sequencing - AssertionError: assert 's1' == 's2'",
        traceback_files=["sequencer.py"],
        repo=t2024_repo,
        hidden=t2024_hidden,
        ref=t2024_ref,
        mutant1=t2024_m1,
        mutant2=t2024_m2,
        hidden_root_cause=True,
        visible_test_sensitive=False,
        root_cause_only_with_exploration=True,
        handbook_citations=["Rule H07"],
        assertions=[
            ("test_stream_sequencing", "HANDBOOK.md Rule H07: Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking", "No", "TAUGHT"),
            ("test_sort_helper_contract", "HANDBOOK.md Rule H07: Event Priority Queue Ordering and Deterministic SHA-256 Tie-Breaking", "No", "TAUGHT")
        ]
    )

    print("Family 6 registered (Tasks 2021-2024).")
