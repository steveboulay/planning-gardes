from datetime import date, datetime, timedelta

from planning_rules.models import RuleCategory, Shift, ShiftKind
from planning_rules.rules import check_consecutive_nights, check_daily_rest, check_weekly_hours


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


def make_consecutive_shifts(
    staff_id: str,
    start: datetime,
    count: int,
    kind: ShiftKind = ShiftKind.DAY,
) -> list[Shift]:
    """Retourne `count` postes consécutifs, à partir de `start`.

    Un poste par défaut est un poste de jour de 12h.
    """
    return [
        make_shift(staff_id=staff_id, start=start + timedelta(days=i), kind=kind)
        for i in range(count)
    ]


def make_consecutive_nights(staff_id: str, start: datetime, count: int) -> list[Shift]:
    """Retourne `count` postes de nuit consécutifs, à partir de `start`."""

    return make_consecutive_shifts(
        staff_id=staff_id, start=start, count=count, kind=ShiftKind.NIGHT
    )


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


def test_nights_above_maximum_have_a_consecutive_nights_violation():
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


def test_each_night_above_maximum_has_a_consecutive_nights_violation():
    nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=5,
    )

    violations = check_consecutive_nights(
        shifts=nights,
        max_nights=3,
    )
    assert len(violations) == 2
    assert violations[0].rule == "nuits_consecutives"
    assert violations[0].category == RuleCategory.COLLECTIVE
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 5)
    assert violations[1].rule == "nuits_consecutives"
    assert violations[1].category == RuleCategory.COLLECTIVE
    assert violations[1].staff_id == "nurse-1"
    assert violations[1].day == date(2026, 11, 6)


def test_nights_separated_by_a_day_off_have_no_consecutive_nights_violation():
    first_nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=3,
    )
    second_nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 6, 20, 0),
        count=3,
    )

    violations = check_consecutive_nights(
        shifts=first_nights + second_nights,
        max_nights=3,
    )
    assert violations == []


def test_nights_of_different_staff_have_no_consecutive_nights_violation():
    nurse1_nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=3,
    )
    nurse2_nights = make_consecutive_nights(
        staff_id="nurse-2",
        start=datetime(2026, 11, 5, 20, 0),
        count=3,
    )

    violations = check_consecutive_nights(
        shifts=nurse1_nights + nurse2_nights,
        max_nights=3,
    )
    assert violations == []


def test_nights_starting_at_different_hours_have_a_consecutive_nights_violation():
    first_nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        count=2,
    )
    second_nights = make_consecutive_nights(
        staff_id="nurse-1",
        start=datetime(2026, 11, 4, 21, 0),
        count=2,
    )

    violations = check_consecutive_nights(
        shifts=first_nights + second_nights,
        max_nights=3,
    )
    assert len(violations) == 1
    assert violations[0].rule == "nuits_consecutives"
    assert violations[0].category == RuleCategory.COLLECTIVE
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 5)


def test_empty_schedule_has_no_weekly_hours_violation():
    violations = check_weekly_hours(
        shifts=[],
        max_duration=timedelta(hours=48),
    )
    assert violations == []


def test_hours_equal_to_maximum_have_no_weekly_hours_violation():
    shifts = make_consecutive_shifts(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        count=4,
    )

    violations = check_weekly_hours(
        shifts=shifts,
        max_duration=timedelta(hours=48),
    )
    assert violations == []


def test_hours_above_maximum_have_a_weekly_hours_violation():
    shifts = make_consecutive_shifts(
        staff_id="nurse-1",
        start=datetime(2026, 11, 3, 8, 0),
        count=5,
    )

    violations = check_weekly_hours(
        shifts=shifts,
        max_duration=timedelta(hours=48),
    )
    assert len(violations) == 1
    assert violations[0].rule == "heures_hebdomadaires"
    assert violations[0].category == RuleCategory.LEGAL
    assert violations[0].staff_id == "nurse-1"
    assert violations[0].day == date(2026, 11, 2)


def test_shifts_spread_over_two_weeks_have_no_weekly_hours_violation():
    first_week_shifts = make_consecutive_shifts(
        staff_id="nurse-1",
        start=datetime(2026, 11, 5, 8, 0),
        count=4,
    )
    second_week_shifts = make_consecutive_shifts(
        staff_id="nurse-1",
        start=datetime(2026, 11, 9, 8, 0),
        count=4,
    )

    violations = check_weekly_hours(
        shifts=first_week_shifts + second_week_shifts,
        max_duration=timedelta(hours=48),
    )
    assert violations == []


def test_shifts_of_different_staff_have_no_weekly_hours_violation():
    nurse1_shifts = make_consecutive_shifts(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        count=4,
    )
    nurse2_shifts = make_consecutive_shifts(
        staff_id="nurse-2",
        start=datetime(2026, 11, 5, 8, 0),
        count=4,
    )

    violations = check_weekly_hours(
        shifts=nurse1_shifts + nurse2_shifts,
        max_duration=timedelta(hours=48),
    )
    assert violations == []
