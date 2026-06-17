from fastapi.testclient import TestClient

from magent.api.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_returns_reviewed_artifact():
    response = client.post(
        "/run",
        json={"goal": "vector databases overview", "acceptance_criteria": ["accurate"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["approved"] is True
    assert data["plan"]
    assert "Artifact" in data["artifact"]
    assert data["revisions"] == 0
