"""
Deterministic Policy Engine.

All policy / eligibility decisions in this application are made HERE, using
plain, explicit, rule-based Python logic. No LLM is involved in deciding
eligibility, compensation, or escalation. The chat layer (app/services/agent.py)
only translates natural language into a structured intent, and then asks this
engine what is allowed.

This keeps the system's policy behavior deterministic, auditable, and
guaranteed not to hallucinate entitlements.
"""

from __future__ import annotations
from typing import Optional

from app.models.customer import Customer
from app.models.booking import Booking
from app.models.policy import (
    PolicyDecision,
    DelayBenefits,
    CancellationOptions,
    LoyaltyBenefits,
)
from app.data.customers import get_customer_by_reference
from app.data.bookings import get_booking_by_reference


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------

def get_customer(booking_reference: str) -> Optional[Customer]:
    return get_customer_by_reference(booking_reference)


def get_booking(booking_reference: str) -> Optional[Booking]:
    return get_booking_by_reference(booking_reference)


def get_flight_status(booking_reference: str, flight_number: Optional[str] = None) -> Optional[Booking]:
    booking = get_booking_by_reference(booking_reference)
    if booking is None:
        return None
    if flight_number and booking.flight_number != flight_number:
        return None
    return booking


# ---------------------------------------------------------------------------
# Delay compensation
# ---------------------------------------------------------------------------

def calculate_delay_benefits(delay_hours: int) -> DelayBenefits:
    """
    Delay < 3h  -> meal voucher only
    Delay > 3h  -> meal voucher + lounge access
    Delay > 5h  -> meal voucher + lounge access + hotel (delayed-hours only)
    Full night hotel is NEVER authorized by policy.
    """
    reasoning = [f"Delay is {delay_hours} hour(s)."]

    meal_voucher = True
    reasoning.append("Meal voucher applies at any qualifying delay.")

    lounge_access = delay_hours > 3
    if lounge_access:
        reasoning.append("Delay exceeds 3 hours \u2192 lounge access applies.")
    else:
        reasoning.append("Delay does not exceed 3 hours \u2192 lounge access does not apply.")

    hotel_delayed_hours = delay_hours > 5
    if hotel_delayed_hours:
        reasoning.append("Delay exceeds 5 hours \u2192 hotel for the delayed-hours portion applies.")
    else:
        reasoning.append("Delay does not exceed 5 hours \u2192 hotel accommodation does not apply.")

    reasoning.append("A full night's hotel stay is never authorized under this policy.")

    return DelayBenefits(
        delay_hours=delay_hours,
        meal_voucher=meal_voucher,
        lounge_access=lounge_access,
        hotel_delayed_hours=hotel_delayed_hours,
        full_night_hotel=False,
        reasoning=reasoning,
    )


# ---------------------------------------------------------------------------
# Cancellation / rebooking / refund
# ---------------------------------------------------------------------------

def get_cancellation_options(booking_reference: str) -> CancellationOptions:
    booking = get_booking_by_reference(booking_reference)
    if booking is None or booking.status != "Cancelled":
        return CancellationOptions(
            eligible=False,
            option_a_free_rebooking=False,
            option_b_full_refund=False,
            reasoning="Booking is not in a cancelled state, so cancellation options do not apply.",
        )
    return CancellationOptions(
        eligible=True,
        option_a_free_rebooking=True,
        option_b_full_refund=True,
        reasoning=(
            "Flight was cancelled by the airline. Customer may choose free rebooking on "
            "the next available flight within 24 hours, or a full refund."
        ),
    )


def check_rebooking_eligibility(booking_reference: str) -> PolicyDecision:
    booking = get_booking_by_reference(booking_reference)
    if booking is None:
        return PolicyDecision(eligible=False, reason="Booking not found.", requires_escalation=False)
    if booking.status == "Cancelled":
        return PolicyDecision(
            eligible=True,
            action="REBOOK_NEXT_AVAILABLE",
            reason="Flight was cancelled by the airline; free rebooking within 24 hours is available.",
            requires_escalation=False,
        )
    return PolicyDecision(
        eligible=False,
        reason="Free rebooking under this policy only applies to airline-caused cancellations.",
        requires_escalation=False,
    )


def check_refund_eligibility(booking_reference: str) -> PolicyDecision:
    booking = get_booking_by_reference(booking_reference)
    if booking is None:
        return PolicyDecision(eligible=False, reason="Booking not found.", requires_escalation=False)
    if booking.status == "Cancelled":
        return PolicyDecision(
            eligible=True,
            action="INITIATE_REFUND",
            reason=(
                "Flight was cancelled by the airline. Full refund is available, processed "
                "within 7 business days to the original payment method only."
            ),
            requires_escalation=False,
        )
    return PolicyDecision(
        eligible=False,
        reason="Refunds under this policy only apply to airline-caused cancellations.",
        requires_escalation=False,
    )


# ---------------------------------------------------------------------------
# Loyalty
# ---------------------------------------------------------------------------

def check_loyalty_benefits(loyalty_tier: str) -> LoyaltyBenefits:
    if loyalty_tier in ("Gold", "Platinum"):
        return LoyaltyBenefits(
            tier=loyalty_tier,
            priority_rebooking=True,
            additional_compensation=False,
            reasoning=(
                f"{loyalty_tier} tier gives priority rebooking and first access to "
                "next-available seats, but no additional compensation beyond standard policy."
            ),
        )
    return LoyaltyBenefits(
        tier=loyalty_tier,
        priority_rebooking=False,
        additional_compensation=False,
        reasoning=f"{loyalty_tier} tier does not carry priority rebooking under the stated policy.",
    )


# ---------------------------------------------------------------------------
# Fare difference
# ---------------------------------------------------------------------------

FARE_WAIVER_SUPERVISOR_THRESHOLD = 1500


def evaluate_fare_waiver(fare_difference: int) -> PolicyDecision:
    if fare_difference <= FARE_WAIVER_SUPERVISOR_THRESHOLD:
        return PolicyDecision(
            eligible=True,
            action="WAIVE_FARE_DIFFERENCE",
            reason=f"Fare difference of \u20b9{fare_difference} is within the \u20b91,500 agent-authorized limit.",
            requires_escalation=False,
        )
    return PolicyDecision(
        eligible=False,
        reason=(
            f"Fare difference of \u20b9{fare_difference} exceeds the \u20b91,500 threshold an agent "
            "may waive without supervisor approval."
        ),
        requires_escalation=True,
        escalation_reason="Fare difference waiver above \u20b91,500 requires supervisor approval.",
    )


# ---------------------------------------------------------------------------
# Master request evaluator
# ---------------------------------------------------------------------------

# Requests that are always escalated regardless of other context.
ALWAYS_ESCALATE_INTENTS = {"LEGAL_THREAT", "FORMAL_COMPLAINT"}

# Requests that are never supported by any policy in this system.
UNSUPPORTED_INTENTS = {"REQUEST_UPGRADE", "REQUEST_EXTRA_COMPENSATION"}


def evaluate_request(
    booking_reference: str,
    request_type: str,
    request_details: Optional[dict] = None,
) -> PolicyDecision:
    """
    Central dispatcher: given an intent (request_type) and optional details,
    return a structured PolicyDecision. This is the single source of truth
    for what the agent is and is not allowed to do.
    """
    request_details = request_details or {}
    booking = get_booking_by_reference(booking_reference)
    customer = get_customer_by_reference(booking_reference)

    if booking is None or customer is None:
        return PolicyDecision(
            eligible=False,
            reason="No booking found for the provided reference.",
            requires_escalation=False,
        )

    # Legal threats / formal complaints -> always escalate immediately
    if request_type in ALWAYS_ESCALATE_INTENTS:
        return PolicyDecision(
            eligible=False,
            reason="This request must be handled by a human specialist.",
            requires_escalation=True,
            escalation_reason=(
                "Legal threats and formal complaints are always escalated to a human agent."
            ),
        )

    if request_type == "REQUEST_REFUND":
        return check_refund_eligibility(booking_reference)

    if request_type == "REQUEST_REBOOKING":
        return check_rebooking_eligibility(booking_reference)

    if request_type == "REQUEST_MEAL_VOUCHER":
        if booking.delay_hours is None:
            return PolicyDecision(
                eligible=False,
                reason="No delay is recorded on this booking, so delay compensation does not apply.",
                requires_escalation=False,
            )
        benefits = calculate_delay_benefits(booking.delay_hours)
        return PolicyDecision(
            eligible=benefits.meal_voucher,
            action="ISSUE_MEAL_VOUCHER" if benefits.meal_voucher else None,
            reason=f"Delay of {booking.delay_hours} hour(s) qualifies for a meal voucher.",
            requires_escalation=False,
        )

    if request_type == "REQUEST_LOUNGE":
        if booking.delay_hours is None:
            return PolicyDecision(
                eligible=False,
                reason="No delay is recorded on this booking, so lounge access does not apply.",
                requires_escalation=False,
            )
        benefits = calculate_delay_benefits(booking.delay_hours)
        return PolicyDecision(
            eligible=benefits.lounge_access,
            action="ISSUE_LOUNGE_ACCESS" if benefits.lounge_access else None,
            reason=(
                f"Delay of {booking.delay_hours} hour(s) "
                + ("exceeds 3 hours, so lounge access applies." if benefits.lounge_access
                   else "does not exceed 3 hours, so lounge access does not apply.")
            ),
            requires_escalation=False,
        )

    if request_type == "REQUEST_HOTEL":
        if booking.delay_hours is None:
            return PolicyDecision(
                eligible=False,
                reason="No delay is recorded on this booking, so hotel accommodation does not apply.",
                requires_escalation=False,
            )
        benefits = calculate_delay_benefits(booking.delay_hours)
        wants_full_night = bool(request_details.get("full_night"))
        if wants_full_night:
            return PolicyDecision(
                eligible=False,
                reason=(
                    "Policy only covers the delayed-hours portion of a hotel stay, never a "
                    "full night's stay."
                ),
                requires_escalation=True,
                escalation_reason="Customer is requesting a full-night hotel stay, which is outside stated policy.",
            )
        return PolicyDecision(
            eligible=benefits.hotel_delayed_hours,
            action="ARRANGE_DELAY_HOURS_HOTEL" if benefits.hotel_delayed_hours else None,
            reason=(
                f"Delay of {booking.delay_hours} hour(s) "
                + ("exceeds 5 hours, so hotel accommodation for the delayed hours applies."
                   if benefits.hotel_delayed_hours
                   else "does not exceed 5 hours, so hotel accommodation does not apply "
                        "(hotel threshold is more than 5 hours).")
            ),
            requires_escalation=False,
        )

    if request_type in UNSUPPORTED_INTENTS:
        return PolicyDecision(
            eligible=False,
            reason="This request is not supported by any stated compensation policy.",
            requires_escalation=True,
            escalation_reason="Requested compensation/exception is outside the stated policy.",
        )

    if request_type == "REQUEST_HIGHER_FARE_FLIGHT":
        return PolicyDecision(
            eligible=False,
            reason=(
                "I can’t complete this rebooking because an alternate higher-fare flight "
                "cannot be confirmed from the provided booking data. This request requires "
                "human handling to confirm availability and the applicable fare."
            ),
            requires_escalation=True,
            escalation_reason="Alternate higher-fare rebooking requires human handling to confirm availability and the applicable fare.",
        )

    if request_type == "REQUEST_FARE_WAIVER":
        fare_difference = request_details.get("fare_difference")
        if fare_difference is None:
            return PolicyDecision(
                eligible=False,
                reason="No fare difference amount was provided to evaluate this waiver request.",
                requires_escalation=True,
                escalation_reason="Fare waiver requested without a confirmed fare difference amount.",
            )
        return evaluate_fare_waiver(int(fare_difference))

    if request_type in ("BOOKING_STATUS", "CANCELLED_FLIGHT"):
        return PolicyDecision(
            eligible=True,
            action="PROVIDE_BOOKING_STATUS",
            reason="Customers may view their own booking information.",
            requires_escalation=False,
        )

    if request_type == "FLIGHT_STATUS":
        return PolicyDecision(
            eligible=True,
            action="PROVIDE_FLIGHT_STATUS",
            reason="Customers may view their own flight status information.",
            requires_escalation=False,
        )

    # UNKNOWN or anything else
    return PolicyDecision(
        eligible=False,
        reason="This request could not be matched to a supported policy.",
        requires_escalation=True,
        escalation_reason="Unrecognized or unsupported request type.",
    )


def determine_escalation(
    request_type: str,
    request_details: Optional[dict],
    policy_result: PolicyDecision,
) -> Optional[dict]:
    """
    Given a PolicyDecision, build a structured escalation payload if required.
    """
    if not policy_result.requires_escalation:
        return None
    return {
        "reason": policy_result.escalation_reason or policy_result.reason,
        "requested_action": request_type,
        "policy_limitation": policy_result.reason,
        "escalation_type": "supervisor" if request_type == "REQUEST_FARE_WAIVER" else "human",
    }