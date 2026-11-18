import pytest
from rest_framework.test import APIClient

from schedules.models import StaffMember


@pytest.fixture
def api_client() -> APIClient:
    """Client de test de DRF, sans authentification.

    Il appelle l'application directement, sans serveur HTTP : c'est l'équivalent
    du KernelBrowser de Symfony.
    """

    return APIClient()


@pytest.fixture
def nurse() -> StaffMember:
    """Soignant nurse-1, enregistré en base."""

    return StaffMember.objects.create(code="nurse-1", full_name="Alice Martin")
