import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from fractal_mcp.explorer_app import app


class TestExplorerApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_app_index_serving(self):
        """Verify that the app serves the index.html from static/."""
        with patch("fractal_mcp.explorer_app.FileResponse") as mock_fr:
            mock_fr.return_value = MagicMock()
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            # Get expected static dir path from the app module
            from fractal_mcp.explorer_app import STATIC_DIR

            mock_fr.assert_called_once_with(STATIC_DIR / "index.html")

    def test_app_includes_explorer_routes(self):
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
