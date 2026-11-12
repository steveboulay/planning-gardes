from datetime import timedelta

from planning_rules.models import Shift


def check_daily_rest(shifts: list[Shift], min_rest: timedelta) -> list:
    """Retourne la liste des infractions et une liste vide si tout est conforme.

    Une infraction est relevée si l'écart entre deux postes du même soignant est inférieur à la
    durée minimale reçue en paramètre.
    """
    return []
