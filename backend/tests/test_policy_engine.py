from app.services import policy_engine


def test_delay_under_3_hours_meal_voucher_only():
    b = policy_engine.calculate_delay_benefits(2)
    assert b.meal_voucher is True
    assert b.lounge_access is False
    assert b.hotel_delayed_hours is False


def test_delay_4_hours_meal_and_lounge_no_hotel():
    b = policy_engine.calculate_delay_benefits(4)
    assert b.meal_voucher is True
    assert b.lounge_access is True
    assert b.hotel_delayed_hours is False


def test_delay_6_hours_meal_lounge_and_hotel():
    b = policy_engine.calculate_delay_benefits(6)
    assert b.meal_voucher is True
    assert b.lounge_access is True
    assert b.hotel_delayed_hours is True


def test_full_night_hotel_never_authorized():
    for hours in (2, 4, 6, 10):
        b = policy_engine.calculate_delay_benefits(hours)
        assert b.full_night_hotel is False


def test_gold_priority_rebooking_no_extra_compensation():
    benefits = policy_engine.check_loyalty_benefits("Gold")
    assert benefits.priority_rebooking is True
    assert benefits.additional_compensation is False


def test_platinum_priority_rebooking_no_extra_compensation():
    benefits = policy_engine.check_loyalty_benefits("Platinum")
    assert benefits.priority_rebooking is True
    assert benefits.additional_compensation is False


def test_silver_no_priority_rebooking():
    benefits = policy_engine.check_loyalty_benefits("Silver")
    assert benefits.priority_rebooking is False


def test_fare_waiver_within_threshold_allowed():
    decision = policy_engine.evaluate_fare_waiver(1000)
    assert decision.eligible is True
    assert decision.requires_escalation is False


def test_fare_waiver_above_threshold_escalates():
    decision = policy_engine.evaluate_fare_waiver(2000)
    assert decision.eligible is False
    assert decision.requires_escalation is True


def test_fare_waiver_exactly_at_threshold_allowed():
    decision = policy_engine.evaluate_fare_waiver(1500)
    assert decision.eligible is True