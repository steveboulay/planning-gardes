from datetime import timedelta


def format_duration(duration: timedelta) -> str:
    """Retourne la durée au format HH:MM, avec un signe moins si elle est négative."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    sign = "-" if total_seconds < 0 and (hours or minutes) else ""
    return f"{sign}{hours:02d}:{minutes:02d}"
