from collections import defaultdict
from datetime import timedelta
from itertools import pairwise

from planning_rules.models import RuleCategory, Shift, Violation


def check_daily_rest(shifts: list[Shift], min_rest: timedelta) -> list[Violation]:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si l'écart entre deux postes du même soignant est inférieur à la
    durée minimale reçue en paramètre.
    """
    violations: list[Violation] = []
    by_staff: dict[str, list[Shift]] = defaultdict(list)
    for shift in shifts:
        by_staff[shift.staff_id].append(shift)
    for staff_id, staff_shifts in by_staff.items():
        for prev_shift, next_shift in pairwise(staff_shifts):
            rest = next_shift.start - prev_shift.end
            if rest < min_rest:
                violations.append(
                    Violation(
                        rule="repos_quotidien",
                        category=RuleCategory.LEGAL,
                        staff_id=staff_id,
                        day=next_shift.start.date(),
                        message=(f"Soignant {staff_id} : repos de {rest} inférieur à {min_rest}."),
                    )
                )
    return violations
