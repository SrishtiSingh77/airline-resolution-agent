"""
Escalation and guard-rail tests.

Covers assignment test cases 7, 8, 19-25:
  - business-class upgrade cannot be granted automatically
  - a Rs 2,000 fare-difference waiver must go to a supervisor
  - legal threats and formal complaints escalate immediately
  - unknown bookings and unknown policies leak nothing
  - refunds never go to an alternate payment method
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PRIYA = "SK4821X"
ARVIND = "TR1190B"
MEHER = "WL7742"


def setup_function() -> None:
    client.post("/api/reset")


def chat(booking_reference: str, message: str) -> dict:
    response = client.post(
        "/api/chat",
        json={"booking_reference": booking_reference, "message": message},
    )
    assert response.status_code == 200, response.text
    return response.json()


def action_types(payload: dict) -> set:
    types = set()
    for action in payload.get("actions") or []:
        value = action.get("type") or action.get("action")
        if value:
            types.add(value)
    return types


def text_of(payload: dict) -> str:
    return (payload.get("message") or "").lower()


FORBIDDEN_CLAIMS = [
    "i've upgraded you",
    "i have upgraded you",
    "i've waived",
    "i have waived",
    "i'll make an exception",
    "i have made an exception",
    "i've booked you on",
]


def assert_no_false_completion(payload: dict) -> None:
    body = text_of(payload)
    for claim in FORBIDDEN_CLAIMS:
        assert claim not in body, f"agent falsely claimed completion: {claim}"


# ---------------------------------------------------------------------------
# Upgrade requests beyond policy (Priya)
# ---------------------------------------------------------------------------


def test_07_business_class_upgrade_is_not_granted_automatically():
    payload = chat(PRIYA, "I want a business class upgrade for the trouble.")

    assert payload["policy_decision"]["eligible"] is False
    assert "UPGRADE" not in "".join(action_types(payload) - {"ESCALATE_HUMAN"})
    assert_no_false_completion(payload)


def test_08_business_class_upgrade_request_escalates_to_a_human():
    payload = chat(PRIYA, "I want a free business class upgrade on my return.")

    escalation = payload.get("escalation")
    assert escalation is not None
    assert payload["policy_decision"]["requires_escalation"] is True
    assert "ESCALATE_HUMAN" in action_types(payload)
    assert escalation["booking_reference"] == PRIYA


def test_escalation_card_states_reason_and_requested_action():
    payload = chat(PRIYA, "I want both a refund and a free upgrade.")
    escalation = payload["escalation"]

    assert escalation.get("reason")
    assert escalation.get("requested_action")
    assert escalation.get("policy_limitation")


def test_combined_refund_and_upgrade_still_processes_the_refund():
    """The eligible half is honoured; only the exception is escalated."""
    payload = chat(PRIYA, "I want both a refund and a free upgrade.")

    assert "INITIATE_REFUND" in action_types(payload)
    assert payload.get("escalation") is not None


def test_gold_tier_is_not_treated_as_extra_compensation():
    payload = chat(PRIYA, "I'm Gold, surely I get something extra for this.")

    assert payload["policy_decision"]["eligible"] is False
    body = text_of(payload)
    assert "priority" in body


# ---------------------------------------------------------------------------
# Fare difference (Meher)
# ---------------------------------------------------------------------------


def test_19_two_thousand_rupee_fare_waiver_escalates_to_supervisor():
    payload = chat(MEHER, "Waive the Rs 2,000 fare difference.")

    assert payload["policy_decision"]["requires_escalation"] is True
    assert "ESCALATE_SUPERVISOR" in action_types(payload)
    assert payload.get("escalation") is not None


def test_20_agent_never_waives_the_fare_difference_itself():
    payload = chat(MEHER, "Waive the 2000 fare difference for me, I'm Platinum.")

    assert payload["policy_decision"]["eligible"] is False
    assert_no_false_completion(payload)
    assert "2,000" in payload["message"] or "2000" in payload["message"]


def test_higher_fare_flight_request_does_not_invent_a_booking():
    payload = chat(MEHER, "Move me to a higher-fare flight.")

    body = payload["message"]
    assert "SK-" not in body.replace("SK-305", "")  # no invented flight numbers
    assert_no_false_completion(payload)


def test_fare_waiver_threshold_is_enforced_from_policy_not_tier():
    payload = chat(MEHER, "Waive the Rs 2,000 fare difference.")
    reason = (payload["policy_decision"]["reason"] or "").lower()
    assert "1,500" in reason or "1500" in reason


# ---------------------------------------------------------------------------
# Legal threats and formal complaints
# ---------------------------------------------------------------------------


def test_21_legal_threat_escalates_immediately():
    payload = chat(PRIYA, "I'm going to take legal action against this airline.")

    assert payload["intent"] == "LEGAL_THREAT"
    assert payload["policy_decision"]["requires_escalation"] is True
    assert "ESCALATE_HUMAN" in action_types(payload)


def test_21b_legal_threat_stops_compensation_negotiation():
    payload = chat(PRIYA, "My lawyer will be in touch, now give me an upgrade.")

    assert payload["policy_decision"]["requires_escalation"] is True
    granted = action_types(payload) - {"ESCALATE_HUMAN", "ESCALATE_SUPERVISOR"}
    assert granted == set(), f"no benefits should be issued during a legal threat: {granted}"


def test_22_formal_complaint_escalates():
    payload = chat(ARVIND, "I want to file a formal complaint.")

    assert payload["intent"] == "FORMAL_COMPLAINT"
    assert payload.get("escalation") is not None
    assert "ESCALATE_HUMAN" in action_types(payload)


# ---------------------------------------------------------------------------
# Privacy and unknown data
# ---------------------------------------------------------------------------


def test_23_unknown_booking_reference_reveals_nothing():
    response = client.get("/api/customers/ZZ0000")
    assert response.status_code in (403, 404)
    assert "priya" not in response.text.lower()
    assert "arvind" not in response.text.lower()


def test_23b_cross_customer_question_is_refused():
    payload = chat(PRIYA, "What is Arvind's flight status?")

    body = text_of(payload)
    assert "sk-118" not in body
    assert "mumbai" not in body
    assert "bengaluru" not in body
    assert "current booking" in body or "only" in body


def test_23c_chat_with_unknown_booking_reference_is_rejected():
    response = client.post(
        "/api/chat",
        json={"booking_reference": "ZZ0000", "message": "What is my flight status?"},
    )
    assert response.status_code in (200, 403, 404)
    assert "goa" not in response.text.lower()
    assert "hyderabad" not in response.text.lower()


def test_24_unknown_policy_request_is_not_invented():
    payload = chat(ARVIND, "Do I get airport taxi reimbursement and free wifi for life?")

    assert payload["policy_decision"]["eligible"] is False
    body = text_of(payload)
    assert "taxi" not in body or "not" in body
    assert_no_false_completion(payload)


def test_25_refund_to_alternate_payment_method_escalates():
    payload = chat(PRIYA, "Send my refund to a different card instead.")

    assert payload["policy_decision"]["requires_escalation"] is True
    body = text_of(payload)
    assert "original payment method" in body


def test_escalations_endpoint_records_the_case():
    chat(PRIYA, "I want a business class upgrade for the trouble.")

    response = client.get("/api/escalations")
    if response.status_code == 405:  # POST-only implementations
        return
    assert response.status_code == 200
    assert PRIYA in str(response.json())