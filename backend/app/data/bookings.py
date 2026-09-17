from typing import Dict, Optional
from app.models.booking import Booking, ReturnFlight

BOOKINGS: Dict[str, Booking] = {
    "SK4821X": Booking(
        booking_reference="SK4821X",
        customer_name="Priya Nair",
        flight_number="SK-204",
        route="Delhi \u2192 Goa",
        date="Wed 23 Sep 2026",
        scheduled_departure="18:40",
        status="Cancelled",
        cancellation_reason="operational reasons",
        return_flight=ReturnFlight(
            route="Goa \u2192 Delhi",
            date="Fri 25 Sep 2026",
            scheduled_departure="16:20",
            status="Unaffected",
        ),
    ),
    "TR1190B": Booking(
        booking_reference="TR1190B",
        customer_name="Arvind Kulkarni",
        flight_number="SK-118",
        route="Mumbai \u2192 Bengaluru",
        date="Wed 23 Sep 2026",
        scheduled_departure="07:10",
        status="Delayed",
        delay_hours=4,
        new_departure="11:10",
    ),
    "WL7742": Booking(
        booking_reference="WL7742",
        customer_name="Meher Kaur",
        flight_number="SK-305",
        route="Delhi \u2192 Hyderabad",
        date="Wed 23 Sep 2026",
        scheduled_departure="14:00",
        status="Delayed",
        delay_hours=6,
        new_departure="20:00",
    ),
}


def get_booking_by_reference(booking_reference: str) -> Optional[Booking]:
    return BOOKINGS.get(booking_reference.strip().upper())


KNOWN_FARE_DIFFERENCES: Dict[str, int] = {
    "WL7742": 2000,
}


def get_known_fare_difference(booking_reference: str) -> Optional[int]:
    return KNOWN_FARE_DIFFERENCES.get(booking_reference.strip().upper())