"""Family 6: event_ordering (Tasks 2021 - 2024).

Governing Rule: Rule H07 (Stable ordering and deterministic tiebreaker: descending priority, ascending secondary key).
Competing Alternatives: Sorting on priority only (unstable), descending secondary key tiebreaker.
Target: 40-120 non-test lines across 3-4 files.
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
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    """Order jobs for dispatch processing.
    Ordering contract:
    - Sort jobs by descending priority.
    - Tiebreaker: break ties on equal priority using job_id in ascending order (deterministic FIFO).
    """
    return sorted(jobs, key=lambda j: (j.priority, j.job_id), reverse=True)

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]

def get_highest_priority_job(jobs: List[JobItem]):
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[0] if ordered else None
''',
        "queue_metrics.py": '''"""Job queue depth monitoring."""
from typing import List
from job import JobItem

def compute_queue_load(jobs: List[JobItem]) -> int:
    return sum(j.priority for j in jobs)

def count_pending_jobs(jobs: List[JobItem]) -> int:
    return sum(1 for j in jobs if j.is_pending())
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
        "tests/test_dispatcher_hidden.py": '''from job import JobItem
from dispatcher import order_jobs_for_dispatch

def test_deterministic_tiebreaker_stated():
    j_early = JobItem(101, 100, "early")
    j_late = JobItem(102, 100, "late")
    ordered = order_jobs_for_dispatch([j_late, j_early])
    assert ordered[0].job_id == 101
    assert ordered[1].job_id == 102
'''
    }

    t2021_ref = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    """Order jobs for dispatch processing.
    Ordering contract:
    - Sort jobs by descending priority.
    - Tiebreaker: break ties on equal priority using job_id in ascending order (deterministic FIFO).
    """
    return sorted(jobs, key=lambda j: (-j.priority, j.job_id))

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]
'''
    }

    t2021_m1 = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    return sorted(jobs, key=lambda j: -j.priority)

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]
'''
    }

    t2021_m2 = {
        "dispatcher.py": '''"""Background job queue dispatcher."""
from typing import List
from job import JobItem

def order_jobs_for_dispatch(jobs: List[JobItem]) -> List[JobItem]:
    return sorted(jobs, key=lambda j: (j.priority, j.job_id), reverse=True)

def select_next_batch(jobs: List[JobItem], batch_size: int = 10) -> List[JobItem]:
    ordered = order_jobs_for_dispatch(jobs)
    return ordered[:batch_size]
'''
    }

    add_task(
        tid=2021,
        family="event_ordering",
        name="Priority Job Queue Dispatcher",
        class_tag="STATED",
        issue="Worker queue anomaly WRK-112: Background worker processed equal-priority tasks out of order under simultaneous job enqueue bursts.",
        traceback_text="FAILED tests/test_dispatcher_hidden.py::test_deterministic_tiebreaker_stated - AssertionError: Inversion error at dispatcher.py:15: equal priority jobs were not broken by ascending job_id",
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
            ("test_deterministic_tiebreaker_stated", "dispatcher.py docstring: 'Sort jobs by descending priority ... job_id in ascending order'", "Yes", "STATED")
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
    timestamp: int
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
            "ts": self.timestamp,
            "channel": self.channel,
        }
''',
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    """Sort notification messages in batch by priority level."""
    return sorted(batch, key=lambda m: -m.priority)

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]

def get_oldest_notification(batch: List[NotificationMessage]):
    if not batch:
        return None
    return min(batch, key=lambda m: m.timestamp)
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
        "tests/test_sorter.py": '''from notification import NotificationMessage
from sorter import sort_notification_batch

def test_priority_ordering():
    m1 = NotificationMessage(1, 10, 100)
    m2 = NotificationMessage(2, 50, 100)
    res = sort_notification_batch([m1, m2])
    assert res[0].msg_id == 2

def test_tiebreaker_visible_sensitive():
    m_first = NotificationMessage(10, 5, 1000)
    m_second = NotificationMessage(20, 5, 2000)
    res = sort_notification_batch([m_second, m_first])
    assert res[0].timestamp <= res[1].timestamp
'''
    }

    t2022_hidden = {
        "tests/test_sorter_hidden.py": '''from notification import NotificationMessage
from sorter import sort_notification_batch

def test_taught_deterministic_timestamp_tiebreaker():
    m_early = NotificationMessage(101, 10, 500)
    m_late = NotificationMessage(102, 10, 800)
    res = sort_notification_batch([m_late, m_early])
    assert res[0].msg_id == 101
    assert res[1].msg_id == 102
'''
    }

    t2022_ref = {
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    """Sort notification messages in batch by priority level."""
    return sorted(batch, key=lambda m: (-m.priority, m.timestamp))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]
'''
    }

    t2022_m1 = {
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    return sorted(batch, key=lambda m: (-m.priority, -m.timestamp))

def extract_urgent_notifications(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    sorted_msgs = sort_notification_batch(batch)
    return [m for m in sorted_msgs if m.is_urgent()]
'''
    }

    t2022_m2 = {
        "sorter.py": '''"""Notification priority batch sorter."""
from typing import List
from notification import NotificationMessage

def sort_notification_batch(batch: List[NotificationMessage]) -> List[NotificationMessage]:
    return sorted(batch, key=lambda m: -m.priority)

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
        issue="Delivery alert NOTIF-702: Urgent user alerts with identical priority tiers were delivered out of chronological order.",
        traceback_text="FAILED tests/test_sorter_hidden.py::test_taught_deterministic_timestamp_tiebreaker - AssertionError: Notification inversion at sorter.py:9: equal priority messages not ordered chronologically",
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
            ("test_taught_deterministic_timestamp_tiebreaker", "HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker", "No", "TAUGHT")
        ]
    )

    # =========================================================================
    # Task 2023: Task Scheduler Queue Rebalancer (STATED, HRC=False, VTS=True)
    # =========================================================================
    t2023_repo = {
        "task_item.py": '''"""Scheduled task models."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ScheduledTask:
    task_id: int
    weight: int
    sequence: int
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
            "seq": self.sequence,
        }
''',
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    """Rebalance scheduled task list.
    Ordering contract:
    - Sort tasks by weight in descending order.
    - Tiebreaker: break equal-weight ties using sequence in ascending order.
    """
    return sorted(tasks, key=lambda t: (t.weight, t.sequence))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None

def filter_active_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    return [t for t in tasks if t.active]
''',
        "metrics.py": '''"""Task queue depth metrics."""
from typing import List
from task_item import ScheduledTask

def total_pending_weight(tasks: List[ScheduledTask]) -> int:
    return sum(t.weight for t in tasks)

def average_task_weight(tasks: List[ScheduledTask]) -> float:
    return total_pending_weight(tasks) / len(tasks) if tasks else 0.0
''',
        "tests/test_rebalancer.py": '''from task_item import ScheduledTask
from rebalancer import rebalance_tasks

def test_basic_rebalance():
    t1 = ScheduledTask(1, 10, 1)
    t2 = ScheduledTask(2, 50, 1)
    res = rebalance_tasks([t1, t2])
    assert res[0].weight == 50

def test_weight_descending_visible_sensitive():
    t1 = ScheduledTask(1, 5, 1)
    t2 = ScheduledTask(2, 20, 2)
    assert rebalance_tasks([t1, t2])[0].task_id == 2
'''
    }

    t2023_hidden = {
        "tests/test_rebalancer_hidden.py": '''from task_item import ScheduledTask
from rebalancer import rebalance_tasks

def test_sequence_tiebreaker_stated():
    t_first = ScheduledTask(10, 100, 1)
    t_second = ScheduledTask(20, 100, 2)
    res = rebalance_tasks([t_second, t_first])
    assert res[0].task_id == 10
    assert res[1].task_id == 20
'''
    }

    t2023_ref = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    """Rebalance scheduled task list.
    Ordering contract:
    - Sort tasks by weight in descending order.
    - Tiebreaker: break equal-weight ties using sequence in ascending order.
    """
    return sorted(tasks, key=lambda t: (-t.weight, t.sequence))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    t2023_m1 = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    return sorted(tasks, key=lambda t: (-t.weight, -t.sequence))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    t2023_m2 = {
        "rebalancer.py": '''"""Scheduler queue rebalancer."""
from typing import List, Optional
from task_item import ScheduledTask

def rebalance_tasks(tasks: List[ScheduledTask]) -> List[ScheduledTask]:
    return sorted(tasks, key=lambda t: (t.weight, t.sequence))

def get_next_executable_task(tasks: List[ScheduledTask]) -> Optional[ScheduledTask]:
    rebalanced = rebalance_tasks(tasks)
    return rebalanced[0] if rebalanced else None
'''
    }

    add_task(
        tid=2023,
        family="event_ordering",
        name="Task Scheduler Queue Rebalancer",
        class_tag="STATED",
        issue="Task scheduler incident SCHED-404: Low-weight background tasks scheduled before heavy priority jobs after queue rebalance.",
        traceback_text="FAILED tests/test_rebalancer.py::test_weight_descending_visible_sensitive - AssertionError: Rebalance error at rebalancer.py:12: highest weight task not placed first",
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
            ("test_sequence_tiebreaker_stated", "rebalancer.py docstring: 'Sort tasks by weight in descending order ... sequence in ascending order'", "Yes", "STATED")
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
    offset: int
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
            "offset": self.offset,
            "topic": self.topic,
        }
''',
        "sort_helper.py": '''"""Internal stream sorting helper."""
from typing import List
from event_packet import EventPacket

def order_packets(packets: List[EventPacket]) -> List[EventPacket]:
    return sorted(packets, key=lambda p: -p.severity)

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
    p1 = EventPacket("s1", 1, 10)
    p2 = EventPacket("s2", 5, 10)
    res = sequence_stream_batch([p1, p2])
    assert res[0].severity == 5
'''
    }

    t2024_hidden = {
        "tests/test_sequencer_hidden.py": '''from event_packet import EventPacket
from sequencer import sequence_stream_batch
from sort_helper import order_packets

def test_stream_ordering_taught():
    p_early = EventPacket("early", 10, 100)
    p_late = EventPacket("late", 10, 200)
    res = sequence_stream_batch([p_late, p_early])
    assert res[0].stream_id == "early"
    assert res[1].stream_id == "late"

def test_sort_helper_direct():
    p1 = EventPacket("a", 5, 1)
    p2 = EventPacket("b", 5, 2)
    assert order_packets([p2, p1])[0].stream_id == "a"
'''
    }

    t2024_ref = {
        "sort_helper.py": '''"""Internal stream sorting helper."""
from typing import List
from event_packet import EventPacket

def order_packets(packets: List[EventPacket]) -> List[EventPacket]:
    return sorted(packets, key=lambda p: (-p.severity, p.offset))

def get_max_severity(packets: List[EventPacket]) -> int:
    return max((p.severity for p in packets), default=0)
'''
    }

    t2024_m1 = {
        "sequencer.py": '''"""Stream event sequencer."""
from typing import List
from sort_helper import order_packets
from event_packet import EventPacket

def sequence_stream_batch(packets: List[EventPacket]) -> List[EventPacket]:
    return sorted(order_packets(packets), key=lambda p: (-p.severity, p.offset))

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
    return sorted(packets, key=lambda p: (-p.severity, -p.offset))

def get_max_severity(packets: List[EventPacket]) -> int:
    return max((p.severity for p in packets), default=0)
'''
    }

    add_task(
        tid=2024,
        family="event_ordering",
        name="Event Stream Ingestion Sequencer",
        class_tag="TAUGHT",
        issue="Data pipeline crash STRM-308: Out-of-order stream offsets caused state replication desync during high-severity packet bursts.",
        traceback_text="FAILED tests/test_sequencer_hidden.py::test_stream_ordering_taught - AssertionError: Offset inversion at sequencer.py:9: equal severity packets were not sequenced by ascending offset",
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
            ("test_stream_ordering_taught", "HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker", "No", "TAUGHT"),
            ("test_sort_helper_direct", "HANDBOOK.md Rule H07: Stable ordering and deterministic tiebreaker", "No", "TAUGHT")
        ]
    )

    print("Family 6 registered (Tasks 2021-2024).")
