from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.models.policy import PolicyDecision
from app.data.bookings import get_booking_by_reference
from app.services import policy_engine, action_service

router = APIRouter(tags=["escalations"])


class EscalationRequest(BaseModel):
    booking_reference: str
    reason: str
    requested_action: str
    policy_limitation: str


@router.post("/api/escalations")
def create_escalation(req: EscalationRequest):
    log = action_service.log_escalation(req.booking_reference, req.reason)
    return {"status": "escalated", "action_log": log}


class EvaluateRequest(BaseModel):
    booking_reference: str
    request_type: str
    request_details: Optional[dict] = None


@router.post("/api/evaluate", response_model=PolicyDecision)
def evaluate(req: EvaluateRequest):
    if req.request_type == "DELAY_BENEFITS":
        booking = get_booking_by_reference(req.booking_reference)
        if booking is None or booking.delay_hours is None:
            return PolicyDecision(
                eligible=False,
                reason="No delay is recorded on this booking, so delay benefits do not apply.",
                requires_escalation=False,
            )
        benefits = policy_engine.calculate_delay_benefits(booking.delay_hours)
        available = []
        if benefits.meal_voucher:
            available.append("meal voucher")
        if benefits.lounge_access:
            available.append("lounge access")
        if benefits.hotel_delayed_hours:
            available.append("hotel accommodation for delayed hours")
        return PolicyDecision(
            eligible=bool(available),
            reason="Delay benefits include " + ", ".join(available) + ".",
            requires_escalation=False,
        )
    return policy_engine.evaluate_request(req.booking_reference, req.request_type, req.request_details)


class ResetRequest(BaseModel):
    booking_reference: Optional[str] = None


@router.post("/api/reset")
def reset(req: Optional[ResetRequest] = None):
    req = req or ResetRequest()
    if req.booking_reference:
        action_service.reset_action_log(req.booking_reference)
    else:
        action_service.reset_all_action_logs()
    return {"status": "reset", "booking_reference": req.booking_reference}