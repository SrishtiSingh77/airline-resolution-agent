"""
Escalation Service.

Builds structured escalation records for the UI and logs an escalation
action against the audit trail. This is called whenever the policy engine
returns requires_escalation=True.
"""

from __future__ import annotations
from typing import Optional

from app.models.chat import EscalationInfo
from app.services import action_service


def create_escalation(
    booking_reference: str,
    reason: str,
    requested_action: str,
    policy_limitation: str,
    escalation_type: str = "human",
) -> EscalationInfo:
    action_service.log_escalation(
        booking_reference=booking_reference,
        reason=reason,
        escalation_type=escalation_type,
    )
    return EscalationInfo(
        reason=reason,
        booking_reference=booking_reference,
        requested_action=requested_action,
        policy_limitation=policy_limitation,
        escalation_type="supervisor" if escalation_type == "supervisor" else "human",
    )