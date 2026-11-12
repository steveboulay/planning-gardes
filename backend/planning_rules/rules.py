from datetime import timedelta
from itertools import pairwise
from operator import attrgetter

from planning_rules.models import RuleCategory, Shift, Violation


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
