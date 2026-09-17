from pydantic import BaseModel
from typing import Optional, List


class PolicyDecision(BaseModel):
    eligible: bool
    action: Optional[str] = None
    reason: str
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None


class DelayBenefits(BaseModel):
    delay_hours: int
    meal_voucher: bool
    lounge_access: bool
    hotel_delayed_hours: bool
    full_night_hotel: bool = False  # always False - never authorized
    reasoning: List[str]


class CancellationOptions(BaseModel):
    eligible: bool
    option_a_free_rebooking: bool
    option_b_full_refund: bool
    reasoning: str


class LoyaltyBenefits(BaseModel):
    tier: str
    priority_rebooking: bool
    additional_compensation: bool = False
    reasoning: str