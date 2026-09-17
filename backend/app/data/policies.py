"""
Static, human-readable policy reference text.

These are DESCRIPTIONS of the rules for display in the UI / API.
The actual decision logic lives in app/services/policy_engine.py.
Nothing here should be treated as executable logic.
"""
from typing import Dict
POLICIES: Dict[str, dict] = {
    "cancellation": {
        "title": "Cancellation Rebooking Policy",
        "rule": (
            "If a flight is cancelled by the airline, the customer is entitled to a free "
            "rebooking on the next available flight within 24 hours OR a full refund. "
            "The customer chooses between these two options."
        ),
    },
    "delay_compensation": {
        "title": "Delay Compensation Policy",
        "rule": (
            "Delay under 3 hours: \u20b9500 meal voucher. "
            "Delay more than 3 hours: meal voucher + lounge access. "
            "Delay more than 5 hours: meal voucher + lounge access + hotel accommodation "
            "covering ONLY the delayed hours (not a full night's stay)."
        ),
    },
    "refund": {
        "title": "Refund Processing Policy",
        "rule": (
            "For airline-caused cancellations, refunds are processed in full within 7 "
            "business days. Refunds go to the original payment method only."
        ),
    },
    "fare_difference": {
        "title": "Fare Difference Policy",
        "rule": (
            "If a customer voluntarily chooses to rebook on a higher-fare flight (not "
            "airline-caused), the customer must pay the fare difference. Agents cannot "
            "waive fare differences above \u20b91,500 without supervisor approval."
        ),
    },
    "loyalty": {
        "title": "Loyalty Tier Policy",
        "rule": (
            "Gold and Platinum customers get priority rebooking and first access to "
            "next-available seats. They receive no additional compensation beyond "
            "standard policy."
        ),
    },
}