from datetime import date, datetime, timedelta, timezone

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


def shift_payload(staff_id: str, start: datetime, end: datetime, kind: str):
    """Retourne un Shift au format JSON."""

    return {"staff_id": staff_id, "start": start.isoformat(), "end": end.isoformat(), "kind": kind}


def day_off_payload(staff_id: str, day: date):
    """Retourne un DayOffRequest au format JSON."""

    return {"staff_id": staff_id, "day": day.isoformat()}


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
    assert "kind" in response.json()["shifts"]["0"]


def test_shift_ending_before_its_start_is_rejected(api_client):
    shift = shift_payload(
        "nurse-1", datetime(2026, 11, 2, 20, 0), datetime(2026, 11, 2, 8, 0), "jour"
    )

    url = reverse("check-schedule")
    response = api_client.post(url, {"shifts": [shift]}, format="json")

    assert response.status_code == 400
    assert response.json() == {
        "shifts": {"0": {"non_field_errors": ["Un poste doit se terminer après son début."]}}
    }


def test_day_off_requests_are_used(api_client):
    shift = shift_payload(
        "nurse-1", datetime(2026, 11, 4, 8, 0), datetime(2026, 11, 4, 20, 0), "jour"
    )
    day_off = day_off_payload("nurse-1", date(2026, 11, 4))

    url = reverse("check-schedule")
    response = api_client.post(
        url, {"shifts": [shift], "day_off_requests": [day_off]}, format="json"
    )

    assert response.status_code == 200
    assert [violation["rule"] for violation in response.json()["violations"]] == ["desiderata"]


def test_given_config_is_used(api_client):
    shifts = [
        shift_payload("nurse-1", datetime(2026, 11, 2, 8, 0), datetime(2026, 11, 2, 20, 0), "jour"),
        shift_payload("nurse-1", datetime(2026, 11, 3, 7, 0), datetime(2026, 11, 3, 19, 0), "jour"),
    ]
    shifts += [
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 3, 20, 0),
            end=datetime(2026, 11, 4, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 4, 20, 0),
            end=datetime(2026, 11, 5, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 5, 20, 0),
            end=datetime(2026, 11, 6, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 6, 20, 0),
            end=datetime(2026, 11, 7, 8, 0),
            kind="nuit",
        ),
    ]
    shifts += [
        shift_payload(
            staff_id="nurse-3",
            start=datetime(2026, 11, 3, 8, 0),
            end=datetime(2026, 11, 3, 20, 0),
            kind="jour",
        ),
        shift_payload(
            staff_id="nurse-3",
            start=datetime(2026, 11, 4, 8, 0),
            end=datetime(2026, 11, 4, 20, 0),
            kind="jour",
        ),
        shift_payload(
            staff_id="nurse-3",
            start=datetime(2026, 11, 5, 8, 0),
            end=datetime(2026, 11, 5, 20, 0),
            kind="jour",
        ),
        shift_payload(
            staff_id="nurse-3",
            start=datetime(2026, 11, 6, 8, 0),
            end=datetime(2026, 11, 6, 20, 0),
            kind="jour",
        ),
        shift_payload(
            staff_id="nurse-3",
            start=datetime(2026, 11, 7, 8, 0),
            end=datetime(2026, 11, 7, 20, 0),
            kind="jour",
        ),
    ]
    url = reverse("check-schedule")
    response = api_client.post(
        url,
        {
            "shifts": shifts,
            "config": {
                "min_daily_rest": "11:00:00",
                "max_weekly_duration": "60:00:00",
                "max_consecutive_nights": 4,
            },
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.json() == {"violations": []}


def test_partial_config_keeps_other_defaults(api_client):
    shifts = [
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 3, 20, 0),
            end=datetime(2026, 11, 4, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 4, 20, 0),
            end=datetime(2026, 11, 5, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 5, 20, 0),
            end=datetime(2026, 11, 6, 8, 0),
            kind="nuit",
        ),
        shift_payload(
            staff_id="nurse-2",
            start=datetime(2026, 11, 6, 20, 0),
            end=datetime(2026, 11, 7, 8, 0),
            kind="nuit",
        ),
    ]

    url = reverse("check-schedule")
    response = api_client.post(
        url,
        {
            "shifts": shifts,
            "config": {"min_daily_rest": "11:00:00"},
        },
        format="json",
    )

    assert response.status_code == 200
    assert [violation["rule"] for violation in response.json()["violations"]] == [
        "nuits_consecutives"
    ]


def test_invalid_config_is_rejected(api_client):
    url = reverse("check-schedule")
    response = api_client.post(
        url,
        {
            "shifts": [],
            "config": {"max_consecutive_nights": 0},
        },
        format="json",
    )

    assert response.status_code == 400
    assert "max_consecutive_nights" in response.json()["config"]


def test_shift_with_time_zone_is_rejected(api_client):
    utc_plus_one = timezone(timedelta(hours=1))
    shift = shift_payload(
        "nurse-1",
        datetime(2026, 11, 2, 0, 30, tzinfo=utc_plus_one),
        datetime(2026, 11, 2, 12, 30, tzinfo=utc_plus_one),
        "nuit",
    )
    url = reverse("check-schedule")
    response = api_client.post(url, {"shifts": [shift]}, format="json")

    assert response.status_code == 400
    assert "start" in response.json()["shifts"]["0"]
    assert "end" in response.json()["shifts"]["0"]
