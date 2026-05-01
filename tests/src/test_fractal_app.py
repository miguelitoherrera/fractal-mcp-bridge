from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.fractal_app import app

client = TestClient(app)

def test_app_index_serving():
    """Verify that the app serves the index.html from static/."""
    with patch("src.fractal_app.FileResponse") as mock_fr:
        mock_fr.return_value = MagicMock()
        response = client.get("/")
        assert response.status_code == 200
        mock_fr.assert_called_once_with("static/index.html")

def test_app_includes_explorer_routes():
    """
    Verify that the app has correctly included the explorer router.
    Instead of full logic testing (which is in tests/src/api/test_explorer.py),
    we just verify the endpoint exists.
    """
    # We use a path that we know exists in the explorer router
    response = client.get("/render?fractal_type=invalid")
    # 422 means the endpoint was reached but validation failed (correct for an included router)
    assert response.status_code == 422
