from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


ActionType = Literal[
    "REBOOK_NEXT_AVAILABLE",
    "INITIATE_REFUND",
    "ISSUE_MEAL_VOUCHER",
    "ISSUE_LOUNGE_ACCESS",
    "ARRANGE_DELAY_HOURS_HOTEL",
    "PROVIDE_BOOKING_STATUS",
    "PROVIDE_FLIGHT_STATUS",
    "ESCALATE_HUMAN",
    "ESCALATE_SUPERVISOR",
    "DENIED_NOT_AUTHORIZED",
]

ActionStatus = Literal["completed", "not_authorized", "escalated", "denied"]


class ActionLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    action: ActionType
    booking_reference: str
    status: ActionStatus
    reason: str
    requires_escalation: bool = False