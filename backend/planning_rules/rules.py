from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from itertools import pairwise
from operator import attrgetter

from planning_rules.formatting import format_duration
from planning_rules.models import (
    DEFAULT_CONFIG,
    DayOffRequest,
    RuleCategory,
    RulesConfig,
    Shift,
    ShiftKind,
    Violation,
)


def check_daily_rest(shifts: list[Shift], min_rest: timedelta) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si l'écart entre deux postes du même soignant est inférieur à la
    durée minimale reçue en paramètre.
    """
    violations: list[Violation] = []
    sorted_shifts = sorted(shifts, key=attrgetter("staff_id", "start"))

    for prev_shift, next_shift in pairwise(sorted_shifts):
        if prev_shift.staff_id != next_shift.staff_id:
            continue

        rest_duration = next_shift.start - prev_shift.end
        if rest_duration < min_rest:
            violations.append(
                Violation(
                    rule="repos_quotidien",
                    category=RuleCategory.LEGAL,
                    staff_id=prev_shift.staff_id,
                    day=next_shift.start.date(),
                    message=(
                        f"Soignant {prev_shift.staff_id} :"
                        f" repos de {format_duration(rest_duration)}"
                        f" inférieur à {format_duration(min_rest)}."
                    ),
                )
            )
    return violations


def check_consecutive_nights(shifts: list[Shift], max_nights: int) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si le nombre de nuits consécutives est supérieur au maximum.
    """
    violations: list[Violation] = []
    night_shifts = sorted(
        (s for s in shifts if s.kind == ShiftKind.NIGHT),
        key=attrgetter("staff_id", "start"),
    )

    consecutive_count = 1
    for prev_shift, next_shift in pairwise(night_shifts):
        if (
            prev_shift.staff_id != next_shift.staff_id
            or next_shift.start.date() - prev_shift.start.date() > timedelta(days=1)
        ):
            consecutive_count = 1
            continue
        consecutive_count += 1
        if consecutive_count > max_nights:
            violations.append(
                Violation(
                    rule="nuits_consecutives",
                    category=RuleCategory.COLLECTIVE,
                    staff_id=prev_shift.staff_id,
                    day=next_shift.start.date(),
                    message=(
                        f"Soignant {prev_shift.staff_id} : plus de {max_nights} nuits consécutives."
                    ),
                )
            )
    return violations


def check_weekly_hours(shifts: list[Shift], max_duration: timedelta) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si un soignant dépasse `max_duration` sur une semaine,
    du lundi au dimanche. Un poste compte dans la semaine où il commence.
    """

    duration_by_staff_week: dict[tuple[str, int, int], timedelta] = defaultdict(timedelta)

    for shift in shifts:
        iso = shift.start.isocalendar()
        duration_by_staff_week[(shift.staff_id, iso.year, iso.week)] += shift.duration

    violations: list[Violation] = []

    for (staff_id, iso_year, iso_week), total_duration in duration_by_staff_week.items():
        if total_duration > max_duration:
            violations.append(
                Violation(
                    rule="heures_hebdomadaires",
                    category=RuleCategory.LEGAL,
                    staff_id=staff_id,
                    day=date.fromisocalendar(iso_year, iso_week, 1),
                    message=(
                        f"Soignant {staff_id} :"
                        f" durée hebdomadaire de {format_duration(total_duration)}"
                        f" supérieure à {format_duration(max_duration)}."
                    ),
                )
            )

    return violations


def check_day_off_requests(
    shifts: list[Shift],
    requests: Sequence[DayOffRequest],
) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée pour chaque demande de repos qui tombe un jour où le soignant a un
    poste qui commence.
    """

    worked_days: set[tuple[str, date]] = {(shift.staff_id, shift.start.date()) for shift in shifts}

    violations: list[Violation] = []

    for request in requests:
        if (request.staff_id, request.day) in worked_days:
            violations.append(
                Violation(
                    rule="desiderata",
                    category=RuleCategory.INDIVIDUAL,
                    staff_id=request.staff_id,
                    day=request.day,
                    message=(
                        f"Soignant {request.staff_id} : poste le {request.day:%d/%m/%Y},"
                        " jour de repos demandé."
                    ),
                )
            )

    return violations


def check_schedule(
    shifts: list[Shift],
    requests: Sequence[DayOffRequest] = (),
    config: RulesConfig = DEFAULT_CONFIG,
) -> list[Violation]:
    """Lance les quatre règles et retourne toutes leurs infractions.

    Les infractions sont triées par jour, puis par soignant, puis par code de règle.
    """

    violations = (
        check_daily_rest(
            shifts=shifts,
            min_rest=config.min_daily_rest,
        )
        + check_consecutive_nights(
            shifts=shifts,
            max_nights=config.max_consecutive_nights,
        )
        + check_weekly_hours(
            shifts=shifts,
            max_duration=config.max_weekly_duration,
        )
        + check_day_off_requests(
            shifts=shifts,
            requests=requests,
        )
    )
    violations.sort(key=attrgetter("day", "staff_id", "rule"))

    return violations
