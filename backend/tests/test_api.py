import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


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
