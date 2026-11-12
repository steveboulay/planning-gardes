from datetime import date, datetime, timedelta

from planning_rules.models import RuleCategory, Shift, ShiftKind
from planning_rules.rules import check_consecutive_nights, check_daily_rest


def make_shift(
    staff_id: str,
    start: datetime,
    duration: timedelta = timedelta(hours=12),
    kind: ShiftKind = ShiftKind.DAY,
) -> Shift:
    """Retourne un poste pour les tests.

    Un poste par défaut est un poste de jour de 12h.
    """

    return Shift(staff_id=staff_id, start=start, end=start + duration, kind=kind)


def make_night(
    staff_id: str,
    start: datetime,
    duration: timedelta = timedelta(hours=12),
) -> Shift:
    """Retourne un poste de nuit pour les tests."""

    return make_shift(staff_id=staff_id, start=start, duration=duration, kind=ShiftKind.NIGHT)


def make_consecutive_nights(staff_id: str, start: datetime, count: int) -> list[Shift]:
    """Retourne {count} postes de nuit consécutifs."""

    return [make_night(staff_id=staff_id, start=start + timedelta(days=i)) for i in range(count)]


def test_empty_schedule_has_no_daily_rest_violation():
    violations = check_daily_rest(
        shifts=[],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_rest_equal_to_minimum_has_no_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    second_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 8, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_rest_below_minimum_has_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    second_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 7, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift],
        min_rest=timedelta(hours=12),
    )
    assert len(violations) == 1
    assert violations[0].rule == "repos_quotidien"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 3)


def test_shifts_of_different_staff_have_no_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    second_shift = make_shift(staff_id="nurse-2", start=datetime(2026, 11, 3, 7, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_shifts_interleaved_with_another_staff_have_a_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    second_shift = make_shift(staff_id="nurse-2", start=datetime(2026, 11, 3, 7, 0))
    third_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 7, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift, third_shift],
        min_rest=timedelta(hours=12),
    )
    assert len(violations) == 1
    assert violations[0].rule == "repos_quotidien"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 3)


def test_unsorted_shifts_have_no_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 8, 0))
    second_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift],
        min_rest=timedelta(hours=12),
    )
    assert violations == []


def test_unsorted_shifts_interleaved_with_another_staff_have_a_daily_rest_violation():
    earlier_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    other_staff_shift = make_shift(staff_id="nurse-2", start=datetime(2026, 11, 3, 7, 0))
    later_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 7, 0))
    violations = check_daily_rest(
        shifts=[later_shift, other_staff_shift, earlier_shift],
        min_rest=timedelta(hours=12),
    )
    assert len(violations) == 1
    assert violations[0].rule == "repos_quotidien"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 3)


def test_rest_equal_to_lower_minimum_has_no_daily_rest_violation():
    first_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 2, 8, 0))
    second_shift = make_shift(staff_id="nurse-1", start=datetime(2026, 11, 3, 7, 0))
    violations = check_daily_rest(
        shifts=[first_shift, second_shift],
        min_rest=timedelta(hours=11),
    )
    assert violations == []


def test_empty_schedule_has_no_consecutive_nights_violation():
    violations = check_consecutive_nights(
        shifts=[],
        max_nights=3,
    )
    assert violations == []


def test_nights_equal_to_maximum_have_no_consecutive_nights_violation():
    nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=3,
    )

    violations = check_consecutive_nights(
        shifts=nights,
        max_nights=3,
    )
    assert violations == []


def test_nights_greater_than_maximum_have_a_consecutive_nights_violation():
    nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=4,
    )

    violations = check_consecutive_nights(
        shifts=nights,
        max_nights=3,
    )
    assert len(violations) == 1
    assert violations[0].rule == "nuits_consecutives"
    assert violations[0].category == RuleCategory.COLLECTIVE
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 5)
