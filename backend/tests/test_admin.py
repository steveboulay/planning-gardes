from datetime import datetime

import pytest
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
