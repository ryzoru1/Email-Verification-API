from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_serves_website_to_browsers():
    response = client.get("/", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Email Verification API" in response.text


def test_terms_and_privacy_pages():
    for path, heading in (("/terms", "Terms of Use"), ("/privacy", "Privacy Policy")):
        response = client.get(path)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert heading in response.text


def test_robots_txt():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "User-agent" in response.text
