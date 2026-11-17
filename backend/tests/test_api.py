from datetime import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


def shift_payload(staff_id: str, start: datetime, end: datetime, kind: str):
    return {"staff_id": staff_id, "start": start.isoformat(), "end": end.isoformat(), "kind": kind}


def test_empty_schedule_returns_no_violation(api_client):
    url = reverse("check-schedule")
    response = api_client.post(url, {"shifts": []}, format="json")

    assert response.status_code == 200
    assert response.json() == {"violations": []}


def test_get_is_not_allowed(api_client):
    url = reverse("check-schedule")
    response = api_client.get(url)

    assert response.status_code == 405


def test_missing_shifts_is_rejected(api_client):
    url = reverse("check-schedule")
    response = api_client.post(url, {}, format="json")

    assert response.status_code == 400
    assert "shifts" in response.json()


def test_daily_rest_violation_is_returned_as_json(api_client):
    first_shift = shift_payload(
        "nurse-1", datetime(2026, 11, 2, 8, 0), datetime(2026, 11, 2, 20, 0), "jour"
    )
    second_shift = shift_payload(
        "nurse-1", datetime(2026, 11, 3, 7, 0), datetime(2026, 11, 3, 19, 0), "jour"
    )
    url = reverse("check-schedule")
    response = api_client.post(url, {"shifts": [first_shift, second_shift]}, format="json")

    assert response.status_code == 200
    assert response.json() == {
        "violations": [
            {
                "rule": "repos_quotidien",
                "category": "légale",
                "staff_id": "nurse-1",
                "day": "2026-11-03",
                "message": "Soignant nurse-1 : repos de 11:00 inférieur à 12:00.",
            }
        ]
    }


def test_unknown_shift_kind_is_rejected(api_client):
    shift = shift_payload(
        "nurse-1", datetime(2026, 11, 2, 8, 0), datetime(2026, 11, 2, 20, 0), "soir"
    )
    url = reverse("check-schedule")
    response = api_client.post(url, {"shifts": [shift]}, format="json")

    assert response.status_code == 400
    assert response.json() == {
        "shifts": {"0": {"kind": ["«\xa0soir\xa0» n'est pas un choix valide."]}}
    }
