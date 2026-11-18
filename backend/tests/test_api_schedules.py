import pytest
from django.urls import reverse

from schedules.models import StaffMember

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
