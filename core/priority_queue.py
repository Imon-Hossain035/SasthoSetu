"""Priority-Based Patient Queue Manager for SasthoSetu (Prompt 14).

This module implements the core patient prioritization logic:
1. Multi-tier urgency ordering:
   URGENT (1) -> PENDING / MANUAL REVIEW (2) -> MODERATE (3) -> ROUTINE (4)
2. Strict First-In, First-Out (FIFO) ordering within each urgency tier
   based on the intake creation timestamp (created_at ASC).
3. Active Waiting Queue isolation:
   Only patients with status='Waiting' occupy sequential active queue positions (#1, #2, ...).
   Completed and In Consultation records are retained for historical audit without displacing waiting patients.
4. Safe pending case handling:
   Pending assessments are never silently downgraded to Routine.
"""

from typing import Any, Dict, List, Optional, Tuple
from core import constants


QUEUE_RULE_EXPLANATION = (
    "Queue ordering: Urgent cases first, followed by Moderate and Routine cases. "
    "Patients within the same urgency level are strictly ordered by arrival time (FIFO)."
)


def get_priority_value(urgency: Optional[str]) -> int:
    """Returns the numeric priority weight for a given urgency level.

    Lower integer values indicate higher priority (placed earlier in the queue).
    - URGENT: 1 (Highest priority)
    - PENDING / Unassessed: 2 (Safety-net review tier; never treated as Routine)
    - MODERATE: 3 (Medium priority)
    - ROUTINE: 4 (Standard priority)
    - Other / Unknown: 5 (Lowest fallback priority)

    Args:
        urgency: Text urgency label (e.g., 'URGENT', 'MODERATE', 'ROUTINE', 'PENDING_CONTEXTUAL_TRIAGE').

    Returns:
        Integer priority weight (1 to 5).
    """
    if not urgency:
        return constants.PRIORITY_PENDING

    normalized = str(urgency).strip().upper()

    if normalized == constants.TIER_URGENT:
        return constants.PRIORITY_URGENT
    elif normalized in (
        constants.STATE_PENDING_CONTEXTUAL_TRIAGE,
        "PENDING",
        "NEEDS ASSESSMENT",
        "MANUAL_REVIEW",
    ):
        return constants.PRIORITY_PENDING
    elif normalized == constants.TIER_MODERATE:
        return constants.PRIORITY_MODERATE
    elif normalized == constants.TIER_ROUTINE:
        return constants.PRIORITY_ROUTINE
    else:
        return constants.PRIORITY_UNKNOWN


def get_status_weight(status: Optional[str]) -> int:
    """Returns numeric order for consultation statuses.

    Ensures active waiting patients are grouped first before ongoing consultations
    and completed historical records.
    - Waiting: 0
    - In Consultation: 1
    - Completed / Reviewed: 2
    - Other: 3
    """
    if not status:
        return 0

    norm = str(status).strip()
    if norm == constants.STATUS_WAITING:
        return 0
    elif norm == constants.STATUS_IN_CONSULTATION:
        return 1
    elif norm in (constants.STATUS_COMPLETED, constants.STATUS_REVIEWED):
        return 2
    return 3


def get_effective_urgency(record: Dict[str, Any]) -> Optional[str]:
    """Returns the effective urgency tier for a patient record (Prompt 15).

    If a clinician override exists, the override takes precedence for active
    queue ordering. Otherwise, returns the final_urgency or the original automated
    urgency_level.
    """
    override = record.get("clinician_override_urgency")
    if override and override != constants.OVERRIDE_USE_AUTOMATED:
        return override
    return record.get("final_urgency") or record.get("urgency_level")


def sort_patients_by_priority(
    patients: List[Dict[str, Any]],
    active_waiting_only: bool = False,
) -> List[Dict[str, Any]]:
    """Sorts patient records by effective urgency priority and arrival timestamp (FIFO).

    The sorting key is:
    1. Status Weight (Waiting patients first, unless active_waiting_only is filtered)
    2. Effective Urgency Priority (URGENT -> PENDING -> MODERATE -> ROUTINE)
    3. Arrival Timestamp (created_at ASC for oldest first within the same urgency tier)

    Args:
        patients: List of patient/triage record dictionaries.
        active_waiting_only: If True, filters strictly to status='Waiting' before sorting.

    Returns:
        A new sorted list of patient records.
    """
    if not patients:
        return []

    target_records = list(patients)
    if active_waiting_only:
        target_records = [
            r for r in target_records if r.get("status") == constants.STATUS_WAITING
        ]

    def _sorting_key(record: Dict[str, Any]) -> Tuple[int, int, str]:
        status_w = get_status_weight(record.get("status"))
        effective_urg = get_effective_urgency(record)
        priority_w = get_priority_value(effective_urg)
        created_at_str = str(record.get("created_at") or "").strip()
        return (status_w, priority_w, created_at_str)

    return sorted(target_records, key=_sorting_key)


def calculate_queue_positions(records: List[Dict[str, Any]]) -> Dict[int, int]:
    """Calculates dynamic 1-based queue positions for all active waiting patients.

    Only records with status == 'Waiting' receive an active queue number (1, 2, 3...).
    Non-waiting records (Completed, In Consultation) are excluded from the queue mapping.

    Args:
        records: Patient records in display order.

    Returns:
        Dictionary mapping triage record ID to its 1-based queue position.
    """
    positions: Dict[int, int] = {}
    current_pos = 1

    for record in records:
        if record.get("status") == constants.STATUS_WAITING:
            rec_id = record.get("id")
            if rec_id is not None:
                positions[int(rec_id)] = current_pos
                current_pos += 1

    return positions


def format_queue_position(position: Optional[int]) -> str:
    """Formats an integer queue position for table display (e.g. '#1', '#2', or '—')."""
    if position is not None and position > 0:
        return f"#{position}"
    return " — "
