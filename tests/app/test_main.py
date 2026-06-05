# Integration tests for the FastAPI explorer application.
import unittest

from fastapi.testclient import TestClient

from fractal_mcp.app.main import app


class TestExplorerApp(unittest.TestCase):
    def test_app_index_serving(self) -> None:
        """Verify that the app serves the index.html from static/."""
        with TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("<!DOCTYPE html>", response.text)
            self.assertIn("Fractal Explorer", response.text)

    def test_app_includes_explorer_routes(self) -> None:
        """
        Verify that the app has correctly included the explorer router.
        Instead of full logic testing (which is in tests/src/api/test_explorer.py),
        we just verify the endpoint exists.
        """
        # We use a path that we know exists in the explorer router
        with TestClient(app) as client:
            response = client.get("/render?fractal_type=invalid")
            # 422 means the endpoint was reached but validation failed
            self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
