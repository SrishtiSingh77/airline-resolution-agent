from fastapi import APIRouter, HTTPException

from app.data.customers import get_customer_by_reference
from app.models.customer import Customer

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/{booking_reference}", response_model=Customer)
def get_customer(booking_reference: str):
    customer = get_customer_by_reference(booking_reference)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found for this reference.")
    return customer
