from datetime import datetime

import pytest

from planning_rules.models import Shift, ShiftKind


def test_shift_ending_before_its_start_is_rejected():
    with pytest.raises(ValueError):
        Shift(
            staff_id="nurse-1",
            start=datetime(2026, 11, 2, 8, 0),
            end=datetime(2026, 11, 2, 7, 0),
            kind=ShiftKind.DAY,
        )
