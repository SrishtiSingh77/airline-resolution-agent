from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

from app.models.policy import PolicyDecision
from app.models.action import ActionLog

Role = Literal["customer", "agent", "system"]

Intent = Literal[
    "BOOKING_STATUS",
    "FLIGHT_STATUS",
    "CANCELLED_FLIGHT",
    "REQUEST_REFUND",
    "REQUEST_REBOOKING",
    "REQUEST_MEAL_VOUCHER",
    "REQUEST_LOUNGE",
    "REQUEST_HOTEL",
    "REQUEST_EXTRA_COMPENSATION",
    "REQUEST_UPGRADE",
    "REQUEST_HIGHER_FARE_FLIGHT",
    "REQUEST_FARE_WAIVER",
    "FORMAL_COMPLAINT",
    "LEGAL_THREAT",
    "OTHER_CUSTOMER_DATA",
    "UNKNOWN",
]


class ChatMessage(BaseModel):
    role: Role
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class EscalationInfo(BaseModel):
    reason: str
    booking_reference: str
    requested_action: str
    policy_limitation: str
    escalation_type: Literal["human", "supervisor"] = "human"


class ChatRequest(BaseModel):
    booking_reference: str
    message: str


class ChatResponse(BaseModel):
    message: str
    intent: Intent
    policy_decision: Optional[PolicyDecision] = None
    actions: List[ActionLog] = []
    escalation: Optional[EscalationInfo] = None