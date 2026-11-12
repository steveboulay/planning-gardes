from datetime import date, datetime, timedelta

from planning_rules.models import RuleCategory, Shift, ShiftKind
from planning_rules.rules import check_daily_rest


def test_empty_schedule_has_no_daily_rest_violation():
    violations = check_daily_rest(
        shifts=[],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_rest_equal_to_minimum_has_no_daily_rest_violation():
    first_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind=ShiftKind.DAY,
    )
    second_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 3, 8, 0),
        end=datetime(2026, 11, 3, 20, 0),
        kind=ShiftKind.DAY,
    )
    violations = check_daily_rest(
        shifts=[
            first_shift,
            second_shift,
        ],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_rest_below_minimum_has_daily_rest_violation():
    first_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind=ShiftKind.DAY,
    )
    second_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 3, 7, 0),
        end=datetime(2026, 11, 3, 19, 0),
        kind=ShiftKind.DAY,
    )
    violations = check_daily_rest(
        shifts=[
            first_shift,
            second_shift,
        ],
        min_rest=timedelta(hours=12),
    )
    assert len(violations) == 1
    assert violations[0].rule == "repos_quotidien"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 3)


def test_shifts_of_different_staff_have_no_daily_rest_violation():
    first_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind=ShiftKind.DAY,
    )
    second_shift = Shift(
        staff_id="nurse-2",
        start=datetime(2026, 11, 3, 7, 0),
        end=datetime(2026, 11, 3, 19, 0),
        kind=ShiftKind.DAY,
    )
    violations = check_daily_rest(
        shifts=[
            first_shift,
            second_shift,
        ],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_shifts_interleaved_with_another_staff_have_a_daily_rest_violation():
    first_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind=ShiftKind.DAY,
    )
    second_shift = Shift(
        staff_id="nurse-2",
        start=datetime(2026, 11, 3, 7, 0),
        end=datetime(2026, 11, 3, 19, 0),
        kind=ShiftKind.DAY,
    )
    third_shift = Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 3, 7, 0),
        end=datetime(2026, 11, 3, 19, 0),
        kind=ShiftKind.DAY,
    )
    violations = check_daily_rest(
        shifts=[first_shift, second_shift, third_shift],
        min_rest=timedelta(hours=12),
    )
    assert len(violations) == 1
    assert violations[0].rule == "repos_quotidien"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 3)
