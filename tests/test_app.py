import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
    })


@pytest.fixture(autouse=True)
def restore_activities():
    reset_activities()
    yield


def test_get_activities_returns_activities():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert data["Programming Class"]["max_participants"] == 20


def test_signup_for_activity_adds_participant():
    reset_activities()

    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_bad_request():
    reset_activities()

    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    reset_activities()

    response = client.delete(
        "/activities/Chess%20Club/participants?email=daniel@mergington.edu"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed daniel@mergington.edu from Chess Club"
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    reset_activities()

    response = client.delete(
        "/activities/Chess%20Club/participants?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"


def test_signup_for_unknown_activity_returns_not_found():
    reset_activities()

    response = client.post(
        "/activities/Unknown%20Club/signup?email=test@mergington.edu"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant_from_unknown_activity_returns_not_found():
    reset_activities()

    response = client.delete(
        "/activities/Unknown%20Club/participants?email=test@mergington.edu"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"
