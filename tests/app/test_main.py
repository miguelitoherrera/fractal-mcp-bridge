# Integration tests for the FastAPI explorer application.
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from fractal_mcp.app.main import STATIC_DIR, app


class TestExplorerApp(unittest.TestCase):
    client: TestClient

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_app_index_serving(self) -> None:
        """Verify that the app serves the index.html from static/."""
        with patch("fractal_mcp.app.main.FileResponse") as mock_fr:
            mock_fr.return_value = MagicMock()
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)

            mock_fr.assert_called_once_with(STATIC_DIR / "index.html")

    def test_app_includes_explorer_routes(self) -> None:
        """
        Verify that the app has correctly included the explorer router.
        Instead of full logic testing (which is in tests/src/api/test_explorer.py),
        we just verify the endpoint exists.
        """
        # We use a path that we know exists in the explorer router
        response = self.client.get("/render?fractal_type=invalid")
        # 422 means the endpoint was reached but validation failed
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
