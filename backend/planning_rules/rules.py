from datetime import timedelta
from itertools import pairwise
from operator import attrgetter

from planning_rules.models import RuleCategory, Shift, ShiftKind, Violation


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
                        f"Soignant {prev_shift.staff_id} : repos de {rest_duration}"
                        f" inférieur à {min_rest}."
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
