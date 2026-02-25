from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects():
    # disable auto-redirect following so we can inspect the actual status code
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    # should redirect to the static index page
    assert "/static/index.html" in response.headers.get("location", "")


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # make sure at least one known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "teststudent@example.com"

    # sign up should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json()["message"]

    # duplicate signup returns 400
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister should succeed
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json()["message"]

    # unregister again should 404
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 404


def test_signup_errors():
    # non-existent activity
    resp = client.post("/activities/NotAnActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_errors():
    # non-existent activity
    resp = client.delete("/activities/NotAnActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

    # existing activity but student not signed up
    activity = "Programming Class"
    resp = client.delete(f"/activities/{activity}/signup", params={"email": "nosuch@school.edu"})
    assert resp.status_code == 404
