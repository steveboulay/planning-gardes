from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum


class ShiftKind(Enum):
    DAY = "jour"
    NIGHT = "nuit"


class RuleCategory(Enum):
    LEGAL = "légale"
    COLLECTIVE = "collective"
    INDIVIDUAL = "individuelle"


@dataclass(frozen=True)
class Violation:
    rule: str
    category: RuleCategory
    staff_id: str
    day: date
    message: str


@dataclass(frozen=True)
class Shift:
    staff_id: str
    start: datetime
    end: datetime
    kind: ShiftKind

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("Un poste doit se terminer après son début.")

    @property
    def duration(self) -> timedelta:
        """Retourne la durée du poste."""
        return self.end - self.start


@dataclass(frozen=True)
class DayOffRequest:
    staff_id: str
    day: date
