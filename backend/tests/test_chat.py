"""
Chat layer tests.

The chat endpoint is a thin orchestration layer: it parses an intent, asks the
policy engine for a decision, executes only allowed actions, and phrases the
result. These tests assert the contract of that layer and the conversational
guard rails, not the wording of individual sentences.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PRIYA = "SK4821X"
ARVIND = "TR1190B"
MEHER = "WL7742"


def setup_function() -> None:
    client.post("/api/reset")


def chat(booking_reference: str, message: str):
    return client.post(
        "/api/chat",
        json={"booking_reference": booking_reference, "message": message},
    )


def ok(booking_reference: str, message: str) -> dict:
    response = chat(booking_reference, message)
    assert response.status_code == 200, response.text
    return response.json()


def action_types(payload: dict) -> set:
    types = set()
    for action in payload.get("actions") or []:
        value = action.get("type") or action.get("action")
        if value:
            types.add(value)
    return types


# ---------------------------------------------------------------------------
# Response contract
# ---------------------------------------------------------------------------


def test_chat_response_has_the_documented_shape():
    payload = ok(PRIYA, "I want a full refund.")

    for key in ("message", "intent", "policy_decision", "actions", "escalation"):
        assert key in payload

    assert isinstance(payload["message"], str) and payload["message"].strip()
    assert isinstance(payload["actions"], list)

    decision = payload["policy_decision"]
    assert isinstance(decision["eligible"], bool)
    assert isinstance(decision["requires_escalation"], bool)
    assert decision["reason"]


def test_every_action_carries_a_status():
    payload = ok(MEHER, "My flight is delayed 6 hours. What do I get?")

    assert payload["actions"], "delay benefits should produce actions"
    for action in payload["actions"]:
        assert action.get("status") in {
            "completed",
            "initiated",
            "not_authorized",
            "escalated",
            "denied",
        }


def test_missing_message_is_rejected():
    response = client.post("/api/chat", json={"booking_reference": PRIYA})
    assert response.status_code == 422


def test_empty_message_does_not_crash():
    response = chat(PRIYA, "   ")
    assert response.status_code in (200, 422)


# ---------------------------------------------------------------------------
# Intent mapping
# ---------------------------------------------------------------------------


def test_intent_mapping_across_phrasings():
    cases = [
        (PRIYA, "Why was my flight cancelled?", "CANCELLED_FLIGHT"),
        (PRIYA, "I want a full refund.", "REQUEST_REFUND"),
        (PRIYA, "I want a business class upgrade for the trouble.", "REQUEST_UPGRADE"),
        (ARVIND, "Can I get lounge access?", "REQUEST_LOUNGE"),
        (ARVIND, "I want a meal voucher.", "REQUEST_MEAL_VOUCHER"),
        (ARVIND, "I need a hotel because I missed my meeting.", "REQUEST_HOTEL"),
        (ARVIND, "I want extra compensation.", "REQUEST_EXTRA_COMPENSATION"),
        (MEHER, "Move me to a higher-fare flight.", "REQUEST_HIGHER_FARE_FLIGHT"),
        (MEHER, "Waive the Rs 2,000 fare difference.", "REQUEST_FARE_WAIVER"),
        (PRIYA, "I'll see you in court.", "LEGAL_THREAT"),
        (ARVIND, "I want to file a formal complaint.", "FORMAL_COMPLAINT"),
    ]
    for booking_reference, message, expected in cases:
        payload = ok(booking_reference, message)
        assert payload["intent"] == expected, f"{message!r} -> {payload['intent']}"


def test_unrecognised_request_falls_back_to_unknown_without_inventing_policy():
    payload = ok(ARVIND, "Can you tell me the pilot's name?")

    assert payload["intent"] == "UNKNOWN"
    assert payload["actions"] == [] or all(
        action.get("status") != "completed" for action in payload["actions"]
    )


def test_emotional_message_is_acknowledged_without_promising_anything():
    payload = ok(PRIYA, "I'm furious about this.")

    body = payload["message"].lower()
    assert any(word in body for word in ("understand", "sorry", "frustrat"))
    granted = action_types(payload) - {"PROVIDE_BOOKING_STATUS", "PROVIDE_FLIGHT_STATUS"}
    assert "REBOOK_NEXT_AVAILABLE" not in granted or payload["policy_decision"]["eligible"]


# ---------------------------------------------------------------------------
# Information requests
# ---------------------------------------------------------------------------


def test_booking_status_returns_only_the_current_customer_data():
    payload = ok(PRIYA, "What's my booking status?")

    body = payload["message"]
    assert "SK4821X" in body or "SK-204" in body
    assert "TR1190B" not in body
    assert "WL7742" not in body


def test_cancellation_explanation_uses_the_supplied_reason_only():
    payload = ok(PRIYA, "Why was my flight cancelled?")

    body = payload["message"].lower()
    assert "operational" in body
    for invented in ("weather", "crew shortage", "technical fault", "strike"):
        assert invented not in body


def test_flight_status_does_not_invent_a_replacement_flight():
    payload = ok(PRIYA, "What's my flight status?")

    body = payload["message"]
    assert "SK-204" in body
    # SK-204 is the only flight number in Priya's data set.
    assert "SK-1" not in body and "SK-3" not in body


# ---------------------------------------------------------------------------
# Conversation state
# ---------------------------------------------------------------------------


def test_multiple_requests_accumulate_in_the_audit_log():
    ok(PRIYA, "Why was my flight cancelled?")
    ok(PRIYA, "I want a full refund.")
    ok(PRIYA, "I want a business class upgrade for the trouble.")

    response = client.get(f"/api/actions/{PRIYA}")
    assert response.status_code == 200
    logged = str(response.json())
    assert "INITIATE_REFUND" in logged
    assert "ESCALATE_HUMAN" in logged


def test_reset_clears_the_session_log():
    ok(PRIYA, "I want a full refund.")
    reset = client.post("/api/reset")
    assert reset.status_code == 200

    response = client.get(f"/api/actions/{PRIYA}")
    assert response.status_code == 200
    body = response.json()
    entries = body if isinstance(body, list) else body.get("actions", body.get("log", []))
    assert entries == []


def test_refund_action_states_method_and_timeline():
    payload = ok(PRIYA, "I want a full refund.")

    body = payload["message"].lower()
    assert "original payment method" in body
    assert "7 business days" in body
    # No fare amount exists in the source data, so none may be quoted.
    assert "rs " not in body and "inr" not in body and "₹" not in body


def test_rebooking_action_does_not_invent_flight_details():
    payload = ok(PRIYA, "Please rebook me instead.")

    body = payload["message"]
    assert "REBOOK_NEXT_AVAILABLE" in action_types(payload)
    assert "seat" not in body.lower() or "not" in body.lower()
    assert "24 hours" in body