from app.services import policy_engine

PRIYA_REF = "SK4821X"


def test_priya_cancelled_flight_refund_eligible():
    decision = policy_engine.check_refund_eligibility(PRIYA_REF)
    assert decision.eligible is True
    assert decision.action == "INITIATE_REFUND"


def test_priya_cancelled_flight_free_rebooking_eligible():
    decision = policy_engine.check_rebooking_eligibility(PRIYA_REF)
    assert decision.eligible is True
    assert decision.action == "REBOOK_NEXT_AVAILABLE"


def test_priya_refund_mentions_original_payment_method():
    decision = policy_engine.check_refund_eligibility(PRIYA_REF)
    assert "original payment method" in decision.reason.lower()


def test_priya_refund_mentions_7_business_days():
    decision = policy_engine.check_refund_eligibility(PRIYA_REF)
    assert "7 business days" in decision.reason


def test_priya_gold_priority_rebooking():
    customer = policy_engine.get_customer(PRIYA_REF)
    benefits = policy_engine.check_loyalty_benefits(customer.loyalty_tier)
    assert benefits.priority_rebooking is True


def test_priya_gold_no_additional_compensation():
    customer = policy_engine.get_customer(PRIYA_REF)
    benefits = policy_engine.check_loyalty_benefits(customer.loyalty_tier)
    assert benefits.additional_compensation is False


def test_priya_business_class_upgrade_not_auto_granted():
    decision = policy_engine.evaluate_request(PRIYA_REF, "REQUEST_UPGRADE")
    assert decision.eligible is False


def test_priya_business_class_upgrade_escalates():
    decision = policy_engine.evaluate_request(PRIYA_REF, "REQUEST_UPGRADE")
    assert decision.requires_escalation is True


def test_priya_cancellation_options_both_present():
    options = policy_engine.get_cancellation_options(PRIYA_REF)
    assert options.eligible is True
    assert options.option_a_free_rebooking is True
    assert options.option_b_full_refund is True