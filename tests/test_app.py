import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_signup_and_unregister_participant(client):
    activity_name = "Chess Club"
    email = "newstudent@example.com"
    original_participants = activities[activity_name]["participants"][:]

    try:
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

        unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants
