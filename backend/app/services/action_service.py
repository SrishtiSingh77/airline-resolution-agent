"""
Action Service.

Executes (simulates) allowed actions and produces ActionLog entries.
This is a prototype: no real airline system is called. Actions never
invent concrete data (amounts, flight numbers, hotel names, etc.) that
was not supplied.
"""

from typing import Dict, List, Optional

from app.models.action import ActionLog, ActionType

# In-memory audit trail, keyed by booking_reference (per demo session).
_ACTION_LOG_STORE: Dict[str, List[ActionLog]] = {}


def _record(booking_reference: str, log: ActionLog) -> ActionLog:
    _ACTION_LOG_STORE.setdefault(booking_reference, []).append(log)
    return log


def get_action_log(booking_reference: str) -> List[ActionLog]:
    return _ACTION_LOG_STORE.get(booking_reference, [])


def reset_action_log(booking_reference: str) -> None:
    _ACTION_LOG_STORE.pop(booking_reference, None)


def reset_all_action_logs() -> None:
    _ACTION_LOG_STORE.clear()


def execute_allowed_action(
    action_type: ActionType,
    booking_reference: str,
    reason: str,
    action_details: Optional[dict] = None,
) -> ActionLog:
    """
    Simulate execution of an allowed action type and log it.
    """
    log = ActionLog(
        action=action_type,
        booking_reference=booking_reference,
        status="completed",
        reason=reason,
    )
    return _record(booking_reference, log)


def log_denied_action(
    booking_reference: str,
    reason: str,
    requires_escalation: bool = True,
) -> ActionLog:
    log = ActionLog(
        action="DENIED_NOT_AUTHORIZED",
        booking_reference=booking_reference,
        status="not_authorized",
        reason=reason,
        requires_escalation=requires_escalation,
    )
    return _record(booking_reference, log)


def log_escalation(
    booking_reference: str,
    reason: str,
    escalation_type: str = "human",
) -> ActionLog:
    action: ActionType = "ESCALATE_SUPERVISOR" if escalation_type == "supervisor" else "ESCALATE_HUMAN"
    log = ActionLog(
        action=action,
        booking_reference=booking_reference,
        status="escalated",
        reason=reason,
        requires_escalation=True,
    )
    return _record(booking_reference, log)


# Simulated action result payloads (never invent concrete data not provided).

def simulate_refund_result() -> dict:
    return {
        "booking_reference": None,  # filled by caller
        "amount": "Full refund",
        "processing_time": "Within 7 business days",
        "destination": "Original payment method",
    }


def simulate_rebooking_result() -> dict:
    return {
        "description": "Rebooking request completed for the next available flight within 24 hours.",
        "flight_number": "Not available in provided data (simulated action only)",
    }


def simulate_meal_voucher_result() -> dict:
    return {"description": "Meal voucher issued per delay compensation policy."}


def simulate_lounge_result() -> dict:
    return {"description": "Lounge access granted per delay compensation policy."}


def simulate_hotel_result() -> dict:
    return {
        "description": "Hotel accommodation arranged for the delayed-hours portion only.",
        "coverage": "Delayed hours only \u2014 not a full night's stay.",
    }