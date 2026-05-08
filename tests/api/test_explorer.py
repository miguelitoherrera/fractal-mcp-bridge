import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from pathlib import Path
from fractal_mcp.api.explorer import router
from fractal_mcp.renderer import (
    DEFAULT_COLORMAP, X_MIN, X_MAX, Y_MIN, Y_MAX, DEFAULT_JULIA_C
)

class TestExplorerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router)
        cls.client = TestClient(app)

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_router_render_mandelbrot(self, mock_render):
        mock_render.return_value = b"render_data"
        
        response = self.client.get("/render?fractal_type=mandelbrot")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"render_data")
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_router_render_julia(self, mock_render):
        mock_render.return_value = b"julia_data"
        
        response = self.client.get("/render?fractal_type=julia")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"julia_data")
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_no_ext(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "test"
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
            "fractal_type": "mandelbrot"
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
    def test_router_save_julia_default_c(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        # Julia type but NO julia_c provided
        payload = {
            "fractal_type": "julia"
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Check that it used DEFAULT_JULIA_C (-0.7, 0.27)
        # julia_c-0.700_0.270_x0.0000_y0.0000_turbo.jpg
        self.assertIn("julia_c-0.700_0.270", response.json()["filename"])

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_router_save_complex_string(self, mock_write, mock_render):
        mock_render.return_value = b"save_data"
        
        # Test parsing complex number from string
        payload = {
            "fractal_type": "julia",
            "julia_c": "-0.7 + 0.27j",
            "filename": "julia_test"
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "julia_test.jpg")
        mock_write.assert_called_once_with(b"save_data")

    def test_router_suggest_filename_endpoint(self):
        response = self.client.get("/suggest-filename?fractal_type=julia&julia_c=-0.123%2B0.745j&reverse_colormap=false")
        self.assertEqual(response.status_code, 200)
        filename = response.json()["filename"]
        self.assertNotIn("reversed", filename)
        self.assertTrue(filename.endswith("turbo.jpg"))

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_invalid_complex(self, mock_write, mock_render):
        mock_render.return_value = b"data"
        # Test the validator's ValueError handling
        payload = {
            "fractal_type": "julia",
            "julia_c": "not-a-number"
            # No filename provided, so it should suggest one
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        # Should have fallen back to DEFAULT_JULIA_C and suggested a filename containing it
        self.assertIn("julia_c-0.700_0.270", response.json()["filename"])
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_missing_julia_c(self, mock_write, mock_render):
        mock_render.return_value = b"data"
        # Test the 'if c is None and req.fractal_type == JULIA' branch
        payload = {
            "fractal_type": "julia"
            # No julia_c and no filename
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("julia_c-0.700_0.270", response.json()["filename"])
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_complex_object(self, mock_write, mock_render):
        mock_render.return_value = b"data"
        payload = {
            "fractal_type": "julia",
            "julia_c": "-0.123+0.745j",
            "filename": "complex_str"
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
            "filename": "mandelbrot_save"
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    @patch("fractal_mcp.api.explorer.render_fractal")
    def test_render_cache_hit(self, mock_render):
        mock_render.return_value = b"cached_data"
        # First render to populate cache
        self.client.get("/render?fractal_type=mandelbrot&resolution=100")
        # Second render with same params should hit cache
        response = self.client.get("/render?fractal_type=mandelbrot&resolution=100")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"cached_data")
        # Should only be called ONCE
        mock_render.assert_called_once()

    def test_render_unsupported_fractal(self):
        # The Query pattern regex ^(mandelbrot|julia)$ usually catches this at the FastAPI level (422)
        response = self.client.get("/render?fractal_type=invalid")
        self.assertEqual(response.status_code, 422)

    @patch("fractal_mcp.api.explorer.render_fractal")
    @patch.object(Path, "write_bytes")
    def test_save_cache_hit(self, mock_write, mock_render):
        mock_render.return_value = b"cached_data"
        # 1. Render once to populate cache
        params = "fractal_type=mandelbrot&resolution=100"
        self.client.get(f"/render?{params}")
        
        # 2. Save with same params should hit cache
        payload = {
            "fractal_type": "mandelbrot",
            "resolution": 100,
            "filename": "cache_hit_save"
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        # Should only be called ONCE (during the initial render)
        mock_render.assert_called_once()


if __name__ == "__main__":
    unittest.main()
