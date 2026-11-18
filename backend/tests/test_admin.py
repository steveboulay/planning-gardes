from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from schedules.models import Shift

pytestmark = pytest.mark.django_db


def test_admin_lists_stored_shifts(admin_client, nurse):
    Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind="jour",
    )

    response = admin_client.get(reverse("admin:schedules_shift_changelist"))

    assert response.status_code == 200
    assert "nurse-1" in response.content.decode()


def test_overlapping_shift_is_reported_by_validation(admin_client, nurse):
    Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind="jour",
    )
    overlapping = Shift(
        staff=nurse,
        start=datetime(2026, 11, 2, 19, 0),
        end=datetime(2026, 11, 3, 7, 0),
        kind="nuit",
    )

    with pytest.raises(ValidationError) as error:
        overlapping.full_clean()

    assert error.value.messages == ["Ce soignant a déjà un poste sur ce créneau."]
