from datetime import timedelta

from planning_rules.formatting import format_duration


def test_format_duration_returns_hh_mm_above_24_hours():
    assert format_duration(timedelta(hours=60)) == "60:00"


def test_format_duration_formats_minutes():
    assert format_duration(timedelta(hours=35, minutes=30)) == "35:30"


def test_format_duration_pads_single_digit_hours_with_leading_zero():
    assert format_duration(timedelta(hours=9)) == "09:00"


def test_format_duration_includes_minus_sign_for_negative_duration():
    assert format_duration(timedelta(hours=-36)) == "-36:00"


def test_format_duration_returns_00_00_for_zero_duration():
    assert format_duration(timedelta()) == "00:00"


def test_format_duration_includes_minus_sign_for_negative_duration_with_minutes():
    assert format_duration(-timedelta(hours=1, minutes=30)) == "-01:30"


def test_format_duration_has_no_minus_sign_when_negative_duration_rounds_to_zero():
    assert format_duration(-timedelta(seconds=30)) == "00:00"
