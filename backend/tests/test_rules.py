from datetime import date, datetime, timedelta

from planning_rules.models import RuleCategory, Shift, ShiftKind
from planning_rules.rules import check_daily_rest


def make_shift(
    staff_id: str,
    start: datetime,
    duration: timedelta | None = None,
    kind: ShiftKind = ShiftKind.DAY,
) -> Shift:
    """Retourne un poste pour les tests.

    Un poste par défaut est un poste de jour de 12h.
    """
    if duration is None:
        duration = timedelta(hours=12)

    return Shift(staff_id=staff_id, start=start, end=start + duration, kind=kind)


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
