import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# keep an original deep copy to reset between tests
_ORIG = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # restore the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(_ORIG))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_ORIG))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # expect some known activities from the seed data
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity():
    email = "teststudent@mergington.edu"
    activity = "Chess Club"

    # initial participants count
    before = len(activities[activity]["participants"])

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # ensure participant added
    assert email in activities[activity]["participants"]
    assert len(activities[activity]["participants"]) == before + 1


def test_unregister_from_activity():
    # use an existing participant from seed data
    activity = "Chess Club"
    email = "michael@mergington.edu"

    assert email in activities[activity]["participants"]

    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # ensure participant removed
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    activity = "Chess Club"
    email = "nonexistent@mergington.edu"

    assert email not in activities[activity]["participants"]

    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 404


def test_signup_nonexistent_activity_returns_404():
    resp = client.post("/activities/NoSuchActivity/signup?email=test@mergington.edu")
    assert resp.status_code == 404


def test_delete_nonexistent_activity_returns_404():
    resp = client.delete("/activities/NoSuchActivity/signup?email=test@mergington.edu")
    assert resp.status_code == 404
