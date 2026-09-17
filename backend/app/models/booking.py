from pydantic import BaseModel
from typing import Optional, Literal

FlightStatus = Literal["Cancelled", "Delayed", "Unaffected", "On Time"]


class ReturnFlight(BaseModel):
    route: str
    date: str
    scheduled_departure: str
    status: FlightStatus


class Booking(BaseModel):
    booking_reference: str
    customer_name: str
    flight_number: str
    route: str
    date: str
    scheduled_departure: str
    status: FlightStatus
    delay_hours: Optional[int] = None
    new_departure: Optional[str] = None
    cancellation_reason: Optional[str] = None
    return_flight: Optional[ReturnFlight] = None