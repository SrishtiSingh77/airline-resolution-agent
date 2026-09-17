from pydantic import BaseModel
from typing import Literal

LoyaltyTier = Literal["Silver", "Gold", "Platinum"]


class Customer(BaseModel):
    name: str
    loyalty_tier: LoyaltyTier
    booking_reference: str
    email: str
    phone: str
    travel_history: str
    prior_complaints: str