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
