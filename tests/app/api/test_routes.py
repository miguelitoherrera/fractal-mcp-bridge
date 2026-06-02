# Tests for the explorer API routes.
import unittest
import urllib.parse
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fractal_mcp.app.api.routes import router

# Testing Constants (formerly from renderer.py)
RESOLUTION = 1600
MAX_ITERATIONS = 200
DEFAULT_COLORMAP = "Turbo"
DEFAULT_JULIA_C = -0.7 + 0.27j
X_MIN = -2.0
X_MAX = 1.0
Y_MIN = -1.5
Y_MAX = 1.5


@patch.object(Path, "write_bytes")
@patch("fractal_mcp.app.api.routes.render_fractal")
class TestExplorerAPI(unittest.TestCase):
    client: TestClient

    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(router)
        from fractal_mcp.app.main import value_error_handler

        app.add_exception_handler(ValueError, value_error_handler)
        self.client = TestClient(app)

    def _get_default_params(self, **kwargs: Any) -> str:
        defaults = {
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        defaults.update(kwargs)

        return urllib.parse.urlencode(defaults)

    def test_router_render_mandelbrot(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"render_data"

        params = self._get_default_params(fractal_type="mandelbrot")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"render_data")
        mock_render.assert_called_once()

    def test_router_render_julia(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"julia_data"

        # Must provide julia_c now
        params = self._get_default_params(fractal_type="julia", c="-0.7+0.27j")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"julia_data")
        mock_render.assert_called_once()

    def test_router_render_exponential(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"expo_data"

        params = self._get_default_params(fractal_type="exponential", c="1+0j")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"expo_data")
        mock_render.assert_called_once()

    def test_router_render_sine(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"sine_data"

        params = self._get_default_params(fractal_type="sine", c="1+0j")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"sine_data")
        mock_render.assert_called_once()

    def test_router_render_cosine(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cosine_data"

        params = self._get_default_params(fractal_type="cosine", c="1+0j")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"cosine_data")
        mock_render.assert_called_once()

    def test_router_render_newton(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"newton_data"

        params = self._get_default_params(fractal_type="newton", power=3.0)
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"newton_data")
        mock_render.assert_called_once()

    def test_router_save_no_ext(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"

        payload = {
            "fractal_type": "mandelbrot",
            "filename": "test",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_save_missing_filename(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # No filename provided - should return 422 Unprocessable Entity
        payload = {
            "fractal_type": "mandelbrot",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_router_save_julia_with_c(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"

        # Julia type WITH julia_c provided
        payload = {
            "fractal_type": "julia",
            "c": "-0.7+0.27j",
            "filename": "julia_custom",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "julia_custom.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_save_newton(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"

        payload = {
            "fractal_type": "newton",
            "power": 3.0,
            "filename": "newton_test",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "newton_test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_save_complex_string(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"

        # Test parsing complex number from string
        payload = {
            "fractal_type": "julia",
            "c": "-0.7 + 0.27j",
            "filename": "julia_test",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "julia_test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_suggest_filename_endpoint(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        params = self._get_default_params(fractal_type="julia", c="-0.123+0.745j", reverse_colormap=False)
        response = self.client.get(f"/suggest-filename?{params}")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertNotIn("reversed", filename)
        self.assertTrue(filename.endswith("turbo.jpg"))

    def test_router_suggest_filename_julia_with_c(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        params = self._get_default_params(fractal_type="julia", c="-0.7+0.27j")
        response = self.client.get(f"/suggest-filename?{params}")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertIn("julia_c-0.700_0.270", filename)

    def test_router_suggest_filename_newton(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        params = self._get_default_params(fractal_type="newton", power=3.5)
        response = self.client.get(f"/suggest-filename?{params}")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertIn("newton_p3.5", filename)

    def test_save_invalid_complex(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # Now returns 422 because we removed the try-except in the validator
        payload = {"fractal_type": "julia", "c": "not-a-number", "resolution": 123}
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_save_missing_julia_c(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # Should return 422 because of Pydantic model_validator
        payload = {
            "fractal_type": "julia",
            "filename": "missing_c",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_save_explicit_none_julia_c(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # Should return 422 because of Pydantic model_validator
        payload = {
            "fractal_type": "julia",
            "julia_c": None,
            "filename": "none_c",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_save_complex_object(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"data"
        payload = {
            "fractal_type": "julia",
            "c": "-0.123+0.745j",
            "filename": "complex_str",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    def test_save_mandelbrot(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"data"
        # Test the branch where fractal_type != JULIA
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "mandelbrot_save",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    def test_render_cache_hit(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cached_data"
        params = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        # First render to populate cache
        self.client.get(f"/render?{params}")
        # Second render with same params should hit cache
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"cached_data")
        # Should only be called ONCE
        mock_render.assert_called_once()

    def test_render_unsupported_fractal(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # Now returns 400 because ValueError is handled
        params = self._get_default_params(fractal_type="invalid")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 400)

    def test_save_cache_hit(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cached_data"
        # 1. Render once to populate cache
        params = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        self.client.get(f"/render?{params}")

        # 2. Save with same params should hit cache
        payload = {
            "fractal_type": "mandelbrot",
            "resolution": 100,
            "filename": "cache_hit_save",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        # Should only be called ONCE (during the initial render)
        mock_render.assert_called_once()

    def test_render_invalid_coords_value_error(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        params = self._get_default_params(fractal_type="mandelbrot", x_min=1.0, x_max=-1.0)
        response = self.client.get(f"/render?{params}")
        # ValueError is caught by the exception handler in main.py, returning 400
        self.assertEqual(response.status_code, 400)
        self.assertIn("x_min must be strictly less than x_max", response.json()["detail"])

    def test_save_invalid_coords_value_error(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "invalid_coords",
            "x_min": 1.0,
            "x_max": -1.0,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
