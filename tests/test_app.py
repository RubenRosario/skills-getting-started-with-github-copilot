import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    original_state = {}
    for activity_name, activity_data in activities.items():
        original_state[activity_name] = activity_data["participants"][:]
    
    yield
    
    # Restore original state after test
    for activity_name, activity_data in activities.items():
        activities[activity_name]["participants"] = original_state[activity_name]


def test_signup_and_unregister_participant(client):
    """Test basic signup and unregister flow"""
    activity_name = "Chess Club"
    email = "newstudent@example.com"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    unregister_response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert unregister_response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify response contains expected activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Soccer Team" in data
    
    # Verify activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club


def test_root_redirect(client):
    """Test root endpoint redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity returns 404"""
    response = client.post("/activities/Nonexistent Club/signup?email=student@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_registered(client):
    """Test signup fails when student is already registered"""
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_new_participant(client):
    """Test successful signup of a new participant"""
    activity_name = "Programming Class"
    email = "newcomer@example.com"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert f"Signed up {email}" in response.json()["message"]


def test_unregister_nonexistent_activity(client):
    """Test unregister from non-existent activity returns 404"""
    response = client.delete("/activities/Nonexistent Club/signup?email=student@example.com")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_not_registered(client):
    """Test unregister fails when student is not registered"""
    activity_name = "Chess Club"
    email = "notregistered@example.com"
    
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_unregister_existing_participant(client):
    """Test successful unregister of an existing participant"""
    activity_name = "Soccer Team"
    email = activities[activity_name]["participants"][0]
    
    initial_count = len(activities[activity_name]["participants"])
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1
    assert f"Unregistered {email}" in response.json()["message"]


def test_multiple_signups_same_activity(client):
    """Test multiple students can sign up for the same activity"""
    activity_name = "Art Club"
    email1 = "student1@example.com"
    email2 = "student2@example.com"
    
    response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
    assert response1.status_code == 200
    
    response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")
    assert response2.status_code == 200
    
    assert email1 in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]


def test_signup_then_signup_again_fails(client):
    """Test that signing up again after unregistering works"""
    activity_name = "Drama Club"
    email = "student@example.com"
    
    # First signup
    response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response1.status_code == 200
    
    # Unregister
    response2 = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response2.status_code == 200
    
    # Sign up again - should succeed
    response3 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response3.status_code == 200
    assert email in activities[activity_name]["participants"]
