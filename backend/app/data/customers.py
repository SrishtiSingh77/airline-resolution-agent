from typing import Dict, Optional

from app.models.customer import Customer

CUSTOMERS: Dict[str, Customer] = {
    "SK4821X": Customer(
        name="Priya Nair",
        loyalty_tier="Gold",
        booking_reference="SK4821X",
        email="priya.nair@example.com",
        phone="+91-98xxxxxxx1",
        travel_history="6 flights in last 12 months",
        prior_complaints="1, delayed baggage, resolved with voucher",
    ),
    "TR1190B": Customer(
        name="Arvind Kulkarni",
        loyalty_tier="Silver",
        booking_reference="TR1190B",
        email="arvind.kulkarni@example.com",
        phone="+91-98xxxxxxx2",
        travel_history="3 flights in last 12 months",
        prior_complaints="none",
    ),
    "WL7742": Customer(
        name="Meher Kaur",
        loyalty_tier="Platinum",
        booking_reference="WL7742",
        email="meher.kaur@example.com",
        phone="+91-98xxxxxxx3",
        travel_history="10 flights in last 12 months",
        prior_complaints="1, overbooking, resolved with tier-status upgrade",
    ),
}


def get_customer_by_reference(booking_reference: str) -> Optional[Customer]:
    return CUSTOMERS.get(booking_reference.strip().upper())