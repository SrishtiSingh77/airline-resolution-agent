from fastapi import APIRouter, HTTPException

from app.data.bookings import get_booking_by_reference
from app.models.booking import Booking

router = APIRouter(prefix="/api", tags=["bookings"])


def _require_booking(booking_reference: str) -> Booking:
    booking = get_booking_by_reference(booking_reference)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found for this reference.")
    return booking


@router.get("/bookings/{booking_reference}", response_model=Booking)
def get_booking(booking_reference: str):
    return _require_booking(booking_reference)


@router.get("/flights/{booking_reference}", response_model=Booking)
def get_flight(booking_reference: str):
    return _require_booking(booking_reference)
