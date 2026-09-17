from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.data.bookings import get_booking_by_reference
from app.models.action import ActionLog
from app.services import policy_engine, action_service

router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionRequest(BaseModel):
    booking_reference: str


class ActionResult(BaseModel):
    action_log: ActionLog
    details: dict


def _require_booking(booking_reference: str):
    booking = get_booking_by_reference(booking_reference)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found for this reference.")
    return booking


@router.post("/rebook", response_model=ActionResult)
def rebook(req: ActionRequest):
    _require_booking(req.booking_reference)
    decision = policy_engine.check_rebooking_eligibility(req.booking_reference)
    if not decision.eligible:
        raise HTTPException(status_code=403, detail=decision.reason)
    log = action_service.execute_allowed_action("REBOOK_NEXT_AVAILABLE", req.booking_reference, decision.reason)
    return ActionResult(action_log=log, details=action_service.simulate_rebooking_result())


@router.post("/refund", response_model=ActionResult)
def refund(req: ActionRequest):
    _require_booking(req.booking_reference)
    decision = policy_engine.check_refund_eligibility(req.booking_reference)
    if not decision.eligible:
        raise HTTPException(status_code=403, detail=decision.reason)
    log = action_service.execute_allowed_action("INITIATE_REFUND", req.booking_reference, decision.reason)
    return ActionResult(action_log=log, details=action_service.simulate_refund_result())


@router.post("/meal-voucher", response_model=ActionResult)
def meal_voucher(req: ActionRequest):
    booking = _require_booking(req.booking_reference)
    if booking.delay_hours is None:
        raise HTTPException(status_code=403, detail="No delay recorded; meal voucher not applicable.")
    benefits = policy_engine.calculate_delay_benefits(booking.delay_hours)
    if not benefits.meal_voucher:
        raise HTTPException(status_code=403, detail="Not eligible for a meal voucher.")
    log = action_service.execute_allowed_action(
        "ISSUE_MEAL_VOUCHER", req.booking_reference, f"Delay of {booking.delay_hours}h qualifies."
    )
    return ActionResult(action_log=log, details=action_service.simulate_meal_voucher_result())


@router.post("/lounge", response_model=ActionResult)
def lounge(req: ActionRequest):
    booking = _require_booking(req.booking_reference)
    if booking.delay_hours is None:
        raise HTTPException(status_code=403, detail="No delay recorded; lounge access not applicable.")
    benefits = policy_engine.calculate_delay_benefits(booking.delay_hours)
    if not benefits.lounge_access:
        raise HTTPException(status_code=403, detail="Not eligible for lounge access.")
    log = action_service.execute_allowed_action(
        "ISSUE_LOUNGE_ACCESS", req.booking_reference, f"Delay of {booking.delay_hours}h exceeds 3 hours."
    )
    return ActionResult(action_log=log, details=action_service.simulate_lounge_result())


@router.post("/hotel", response_model=ActionResult)
def hotel(req: ActionRequest):
    booking = _require_booking(req.booking_reference)
    if booking.delay_hours is None:
        raise HTTPException(status_code=403, detail="No delay recorded; hotel not applicable.")
    benefits = policy_engine.calculate_delay_benefits(booking.delay_hours)
    if not benefits.hotel_delayed_hours:
        raise HTTPException(status_code=403, detail="Not eligible for hotel accommodation (delay must exceed 5 hours).")
    log = action_service.execute_allowed_action(
        "ARRANGE_DELAY_HOURS_HOTEL", req.booking_reference, f"Delay of {booking.delay_hours}h exceeds 5 hours."
    )
    return ActionResult(action_log=log, details=action_service.simulate_hotel_result())


@router.get("/log/{booking_reference}", response_model=List[ActionLog])
def get_log(booking_reference: str):
    return action_service.get_action_log(booking_reference)


@router.get("/{booking_reference}", response_model=List[ActionLog])
def get_action_log(booking_reference: str):
    return action_service.get_action_log(booking_reference)