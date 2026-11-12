from datetime import timedelta
from itertools import pairwise

from planning_rules.models import RuleCategory, Shift, Violation


def check_daily_rest(shifts: list[Shift], min_rest: timedelta) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si l'écart entre deux postes est inférieur à la
    durée minimale reçue en paramètre.
    """
    violations: list[Violation] = []
    for prev_shift, next_shift in pairwise(shifts):
        rest = next_shift.start - prev_shift.end
        if rest < min_rest:
            violations.append(
                Violation(
                    rule="repos_quotidien",
                    category=RuleCategory.LEGAL,
                    staff_id=prev_shift.staff_id,
                    day=next_shift.start.date(),
                    message=(
                        f"Soignant {prev_shift.staff_id} : repos de {rest} inférieur à {min_rest}."
                    ),
                )
            )
    return violations
