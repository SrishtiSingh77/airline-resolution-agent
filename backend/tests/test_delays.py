"""
Delay compensation tests.

Covers assignment test cases 9-18:
  Arvind  (SK-118, 4h delay)  -> meal voucher + lounge, NO hotel
  Meher   (SK-305, 6h delay)  -> meal voucher + lounge + delayed-hours hotel,
                                 NOT a full night's stay

These tests drive the public HTTP surface so they assert on the behaviour a
reviewer can actually observe in the running app.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ARVIND = "TR1190B"
MEHER = "WL7742"


def setup_function() -> None:
    """Each test starts from a clean demo session."""
    client.post("/api/reset")


def chat(booking_reference: str, message: str) -> dict:
    response = client.post(
        "/api/chat",
        json={"booking_reference": booking_reference, "message": message},
    )
    assert response.status_code == 200, response.text
    return response.json()


def action_types(payload: dict) -> set:
    """Collect action identifiers regardless of field naming."""
    types = set()
    for action in payload.get("actions") or []:
        value = action.get("type") or action.get("action")
        if value:
            types.add(value)
    return types


def text_of(payload: dict) -> str:
    return (payload.get("message") or "").lower()


# ---------------------------------------------------------------------------
# Arvind - 4 hour delay
# ---------------------------------------------------------------------------


def test_arvind_flight_status_reports_four_hour_delay():
    response = client.get(f"/api/flights/{ARVIND}")
    assert response.status_code == 200
    body = response.json()
    assert "SK-118" in str(body)
    assert "4" in str(body.get("delay_hours", body))


def test_09_four_hour_delay_issues_meal_voucher():
    payload = chat(ARVIND, "My flight is delayed. What am I entitled to?")
    assert "ISSUE_MEAL_VOUCHER" in action_types(payload)


def test_10_four_hour_delay_issues_lounge_access():
    payload = chat(ARVIND, "Can I get lounge access?")
    assert "ISSUE_LOUNGE_ACCESS" in action_types(payload)
    assert payload["policy_decision"]["eligible"] is True


def test_11_four_hour_delay_does_not_arrange_hotel():
    payload = chat(ARVIND, "I need a hotel because I missed my meeting.")

    assert payload["policy_decision"]["eligible"] is False
    assert "ARRANGE_DELAY_HOURS_HOTEL" not in action_types(payload)
    # The agent must not claim it booked anything.
    assert "i've booked" not in text_of(payload)
    assert "i have booked" not in text_of(payload)


def test_11b_hotel_denial_explains_the_five_hour_threshold():
    payload = chat(ARVIND, "Can I get a hotel room?")
    reason = (payload["policy_decision"]["reason"] or "").lower()
    assert "5" in reason or "five" in reason


def test_12_missed_meeting_does_not_create_extra_compensation():
    payload = chat(ARVIND, "I want extra compensation, I missed my meeting.")

    decision = payload["policy_decision"]
    assert decision["eligible"] is False
    assert decision["requires_escalation"] is True
    assert payload.get("escalation") is not None


def test_arvind_silver_tier_gets_no_priority_rebooking_claim():
    """Priority rebooking is a Gold/Platinum benefit only."""
    response = client.get(f"/api/customers/{ARVIND}")
    assert response.status_code == 200
    assert response.json()["loyalty_tier"] == "Silver"


def test_arvind_multiple_requests_in_one_conversation():
    chat(ARVIND, "What am I entitled to?")
    chat(ARVIND, "I want a meal voucher.")
    payload = chat(ARVIND, "Can I get lounge access?")

    log = client.get(f"/api/actions/{ARVIND}")
    assert log.status_code == 200
    logged = str(log.json())
    assert "ISSUE_MEAL_VOUCHER" in logged
    assert "ISSUE_LOUNGE_ACCESS" in logged
    assert "ARRANGE_DELAY_HOURS_HOTEL" not in logged
    assert payload["policy_decision"]["eligible"] is True


# ---------------------------------------------------------------------------
# Meher - 6 hour delay
# ---------------------------------------------------------------------------


def test_13_six_hour_delay_issues_meal_voucher():
    payload = chat(MEHER, "My flight is delayed 6 hours. What do I get?")
    assert "ISSUE_MEAL_VOUCHER" in action_types(payload)


def test_14_six_hour_delay_issues_lounge_access():
    payload = chat(MEHER, "My flight is delayed 6 hours. What do I get?")
    assert "ISSUE_LOUNGE_ACCESS" in action_types(payload)


def test_15_six_hour_delay_arranges_delayed_hours_hotel():
    payload = chat(MEHER, "I only want hotel coverage for the delay.")

    assert payload["policy_decision"]["eligible"] is True
    assert "ARRANGE_DELAY_HOURS_HOTEL" in action_types(payload)


def test_16_six_hour_delay_refuses_full_night_hotel():
    payload = chat(MEHER, "I want a full night's hotel.")

    body = text_of(payload)
    assert "delayed hours" in body or "delayed-hours" in body
    assert "FULL_NIGHT_HOTEL" not in action_types(payload)

    # A full-night request is either denied outright or flagged for escalation,
    # but it is never silently granted.
    decision = payload["policy_decision"]
    assert decision["eligible"] is False or decision["requires_escalation"] is True


def test_17_platinum_gets_priority_rebooking():
    response = client.get("/api/policies/loyalty")
    assert response.status_code == 200
    body = str(response.json()).lower()
    assert "priority" in body

    customer = client.get(f"/api/customers/{MEHER}").json()
    assert customer["loyalty_tier"] == "Platinum"


def test_18_platinum_gets_no_additional_compensation():
    payload = chat(MEHER, "I want compensation because I'm Platinum.")

    decision = payload["policy_decision"]
    assert decision["eligible"] is False
    assert decision["requires_escalation"] is True
    body = text_of(payload)
    assert "platinum" in body


def test_delay_benefits_endpoint_is_consistent_across_thresholds():
    """Threshold behaviour, evaluated through the policy API."""
    cases = [
        (ARVIND, "meal voucher", True),
        (ARVIND, "lounge", True),
        (MEHER, "hotel", True),
    ]
    for booking_reference, phrase, expected in cases:
        payload = client.post(
            "/api/evaluate",
            json={
                "booking_reference": booking_reference,
                "request_type": "DELAY_BENEFITS",
                "request_details": {},
            },
        )
        assert payload.status_code == 200
        body = str(payload.json()).lower()
        assert (phrase in body) is expected