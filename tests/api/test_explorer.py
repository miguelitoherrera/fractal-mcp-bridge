import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from pathlib import Path
from fractal_mcp.api.explorer import router

# Testing Constants (formerly from renderer.py)
RESOLUTION = 1600
MAX_ITERATIONS = 200
DEFAULT_COLORMAP = "Turbo"
DEFAULT_JULIA_C = -0.7 + 0.27j
X_MIN = -2.0
X_MAX = 1.0
Y_MIN = -1.5
Y_MAX = 1.5

class TestExplorerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router)
        cls.client = TestClient(app)

    def _get_default_params(self, **kwargs):
        defaults = {
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False
        }
        defaults.update(kwargs)
        import urllib.parse
        return urllib.parse.urlencode(defaults)

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_router_render_mandelbrot(self, mock_render):
        mock_render.return_value = b"render_data"
        
        params = self._get_default_params(fractal_type="mandelbrot")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"render_data")
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_router_render_julia(self, mock_render):
        mock_render.return_value = b"julia_data"
        
        # Must provide julia_c now
        params = self._get_default_params(fractal_type="julia", julia_c="-0.7+0.27j")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"julia_data")
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_no_ext(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "test",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_suggest_filename(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        # No filename provided
        payload = {
            "fractal_type": "mandelbrot",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Expected filename based on default coords and turbo colormap
        # x_center = -0.5, y_center = 0
        expected = f"mandelbrot_x-0.5000_y0.0000_{DEFAULT_COLORMAP.lower()}.jpg"
        self.assertEqual(response.json()["filename"], expected)
        mock_write.assert_called_once_with(b"save_data")

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_julia_with_c(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        # Julia type WITH julia_c provided
        payload = {
            "fractal_type": "julia",
            "julia_c": "-0.7+0.27j",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Check that it used the provided c
        self.assertIn("julia_c-0.700_0.270", response.json()["filename"])

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_complex_string(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        # Test parsing complex number from string
        payload = {
            "fractal_type": "julia",
            "julia_c": "-0.7 + 0.27j",
            "filename": "julia_test",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "julia_test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_suggest_filename_endpoint(self):
        params = self._get_default_params(fractal_type="julia", julia_c="-0.123+0.745j", reverse_colormap=False)
        response = self.client.get(f"/suggest-filename?{params}")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertNotIn("reversed", filename)
        self.assertTrue(filename.endswith("turbo.jpg"))

    def test_router_suggest_filename_julia_with_c(self):
        params = self._get_default_params(fractal_type="julia", julia_c="-0.7+0.27j")
        response = self.client.get(f"/suggest-filename?{params}")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertIn("julia_c-0.700_0.270", filename)

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_invalid_complex(self, mock_write, mock_render):
        # Now returns 422 because we removed the try-except in the validator
        payload = {
            "fractal_type": "julia",
            "julia_c": "not-a-number",
            "resolution": 123
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_missing_julia_c(self, mock_write, mock_render):
        # Should raise ValueError in the endpoint now
        payload = {
            "fractal_type": "julia",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        with self.assertRaises(ValueError):
             self.client.post("/save", json=payload)

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_explicit_none_julia_c(self, mock_write, mock_render):
        payload = {
            "fractal_type": "julia",
            "julia_c": None,
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        with self.assertRaises(ValueError):
            self.client.post("/save", json=payload)

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_complex_object(self, mock_write, mock_render):
        mock_render.return_value = b"data"
        payload = {
            "fractal_type": "julia",
            "julia_c": "-0.123+0.745j",
            "filename": "complex_str",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_mandelbrot(self, mock_write, mock_render):
        mock_render.return_value = b"data"
        # Test the branch where fractal_type != JULIA
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "mandelbrot_save",
            "x_min": X_MIN, "x_max": X_MAX, "y_min": Y_MIN, "y_max": Y_MAX,
            "max_iterations": 200, "resolution": 1600, "colormap": "Turbo", "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_render_cache_hit(self, mock_render):
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

    def test_render_unsupported_fractal(self):
        # Now raises ValueError because Query validation is removed
        params = self._get_default_params(fractal_type="invalid")
        with self.assertRaises(ValueError):
             self.client.get(f"/render?{params}")

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_cache_hit(self, mock_write, mock_render):
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
            "reverse_colormap": False
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        # Should only be called ONCE (during the initial render)
        mock_render.assert_called_once()


if __name__ == "__main__":
    unittest.main()
