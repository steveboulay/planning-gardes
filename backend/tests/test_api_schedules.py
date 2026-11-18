from datetime import datetime

import pytest
from django.urls import reverse

from schedules.models import Shift, StaffMember

pytestmark = pytest.mark.django_db


def test_staff_members_are_listed(api_client):
    StaffMember.objects.create(code="nurse-2", full_name="Bruno Petit")
    StaffMember.objects.create(code="nurse-1", full_name="Alice Martin")

    response = api_client.get(reverse("staff-list"))

    assert response.status_code == 200
    assert response.json() == [
        {"code": "nurse-1", "full_name": "Alice Martin"},
        {"code": "nurse-2", "full_name": "Bruno Petit"},
    ]


def test_shifts_of_the_period_are_listed(api_client, nurse):
    Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 1, 8, 0),
        end=datetime(2026, 11, 1, 20, 0),
        kind="jour",
    )
    sunday_night = Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 8, 20, 0),
        end=datetime(2026, 11, 9, 8, 0),
        kind="nuit",
    )
    monday = Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind="jour",
    )
    Shift.objects.create(
        staff=nurse,
        start=datetime(2026, 11, 9, 20, 0),
        end=datetime(2026, 11, 10, 8, 0),
        kind="nuit",
    )

    response = api_client.get(reverse("shift-list"), {"start": "2026-11-02", "end": "2026-11-08"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": monday.pk,
            "staff": "nurse-1",
            "start": "2026-11-02T08:00:00",
            "end": "2026-11-02T20:00:00",
            "kind": "jour",
        },
        {
            "id": sunday_night.pk,
            "staff": "nurse-1",
            "start": "2026-11-08T20:00:00",
            "end": "2026-11-09T08:00:00",
            "kind": "nuit",
        },
    ]


def test_period_is_required(api_client):
    response = api_client.get(reverse("shift-list"))

    assert response.status_code == 400
    assert "start" in response.json()
    assert "end" in response.json()


def test_period_ending_before_its_start_is_rejected(api_client):
    response = api_client.get(reverse("shift-list"), {"start": "2026-11-08", "end": "2026-11-02"})

    assert response.status_code == 400
    assert response.json() == {"non_field_errors": ["La période doit se terminer après son début."]}


def test_single_day_period_is_accepted(api_client):
    response = api_client.get(reverse("shift-list"), {"start": "2026-11-02", "end": "2026-11-02"})

    assert response.status_code == 200
