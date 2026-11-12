from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ShiftKind(Enum):
    DAY = "jour"
    NIGHT = "nuit"


@dataclass(frozen=True)
class Shift:
    staff_id: str
    start: datetime
    end: datetime
    kind: ShiftKind

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("Un poste doit se terminer après son début.")
