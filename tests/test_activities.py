import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Basketball" in data


def test_signup_and_unregister_flow(client):
    email = "pytest_user@example.com"
    activity = "Debate Club"

    # ensure clean state
    if email in client.get("/activities").json()[activity]["participants"]:
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # signup
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # confirm present
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

    # unregister
    r2 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert r2.status_code == 200

    # unregister again should fail
    r3 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 400


def test_signup_duplicate_fails(client):
    email = "dup_user@example.com"
    activity = "Art Studio"

    # cleanup
    if email in client.get("/activities").json()[activity]["participants"]:
        client.delete(f"/activities/{activity}/unregister?email={email}")

    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # cleanup
    client.delete(f"/activities/{activity}/unregister?email={email}")


def test_nonexistent_activity(client):
    r1 = client.post("/activities/Nonexistent/signup?email=x@example.com")
    assert r1.status_code == 404
    r2 = client.delete("/activities/Nonexistent/unregister?email=x@example.com")
    assert r2.status_code == 404
