from datetime import date, datetime, timedelta

import pytest
from django.db import IntegrityError

from planning_rules import models as engine
from schedules.models import DayOffRequest, Shift, StaffMember

pytestmark = pytest.mark.django_db


def store_shift(staff: StaffMember, start: datetime, hours: int = 12, kind: str = "jour") -> Shift:
    """Enregistre un poste en base et le retourne.

    Un poste par défaut est un poste de jour de 12 heures.
    """

    return Shift.objects.create(
        staff=staff, start=start, end=start + timedelta(hours=hours), kind=kind
    )


def test_stored_shift_converts_to_engine_shift(nurse):
    shift = store_shift(nurse, datetime(2026, 11, 2, 20, 0), kind="nuit")

    stored = Shift.objects.get(pk=shift.pk)

    assert stored.to_engine() == engine.Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 20, 0),
        end=datetime(2026, 11, 3, 8, 0),
        kind=engine.ShiftKind.NIGHT,
    )


def test_shift_ending_before_its_start_cannot_be_stored(nurse):
    with pytest.raises(IntegrityError):
        store_shift(nurse, datetime(2026, 11, 2, 20, 0), hours=-12)


def test_staff_code_cannot_be_stored_twice(nurse):
    with pytest.raises(IntegrityError):
        StaffMember.objects.create(code="nurse-1", full_name="André Martin")


def test_stored_day_off_request_converts_to_engine_request(nurse):
    day_off_request = DayOffRequest.objects.create(staff=nurse, day=date(2026, 11, 4))

    stored = DayOffRequest.objects.get(pk=day_off_request.pk)

    assert stored.to_engine() == engine.DayOffRequest(
        staff_id="nurse-1",
        day=date(2026, 11, 4),
    )


def test_day_off_request_cannot_be_stored_twice(nurse):
    DayOffRequest.objects.create(staff=nurse, day=date(2026, 11, 4))

    with pytest.raises(IntegrityError):
        DayOffRequest.objects.create(staff=nurse, day=date(2026, 11, 4))


def test_overlapping_shifts_of_the_same_staff_cannot_be_stored(nurse):
    store_shift(nurse, datetime(2026, 11, 2, 8, 0), kind="jour")

    with pytest.raises(IntegrityError):
        store_shift(nurse, datetime(2026, 11, 2, 19, 0), kind="nuit")


def test_back_to_back_shifts_can_be_stored(nurse):
    store_shift(nurse, datetime(2026, 11, 2, 8, 0), kind="jour")
    store_shift(nurse, datetime(2026, 11, 2, 20, 0), kind="nuit")

    assert Shift.objects.count() == 2


def test_overlapping_shifts_of_different_staff_can_be_stored(nurse):
    nurse2 = StaffMember.objects.create(code="nurse-2", full_name="André Martin")
    store_shift(nurse, datetime(2026, 11, 2, 8, 0), kind="jour")
    store_shift(nurse2, datetime(2026, 11, 2, 8, 0), kind="jour")

    assert Shift.objects.count() == 2
