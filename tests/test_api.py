"""API endpoint tests (mocked vector store to avoid heavy imports)."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


@patch("app.api.routes.get_vector_store")
def test_health_endpoint(mock_store):
    mock_store.return_value = MagicMock(count=10)

    from main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["vector_store_chunks"] == 10


def test_ask_empty_validation():
    with patch("app.api.routes.get_vector_store") as mock_store:
        mock_store.return_value = MagicMock(count=0)
        from main import app

        client = TestClient(app)
        response = client.post("/ask", json={"question": ""})
        assert response.status_code == 422
