import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from pathlib import Path
from src.api.explorer import router, generate_image

class TestExplorerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router)
        cls.client = TestClient(app)

    def test_generate_image_mandelbrot(self):
        with patch("src.api.explorer.generate_mandelbrot_grid") as mock_mandel, \
             patch("src.api.explorer.grid_to_image_bytes") as mock_img:
            mock_mandel.return_value = []
            mock_img.return_value = b"fake_data"
            
            result = generate_image(
                fractal_type="mandelbrot",
                x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5,
                max_iterations=10, resolution=10,
                colormap="Inferno", reverse_colormap=False,
                c_real=0.0, c_imag=0.0
            )
            self.assertEqual(result, b"fake_data")
            mock_mandel.assert_called_once()

    def test_generate_image_unsupported(self):
        with self.assertRaises(ValueError):
            generate_image(
                fractal_type="unsupported",
                x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5,
                max_iterations=10, resolution=10,
                colormap="Inferno", reverse_colormap=False,
                c_real=0.0, c_imag=0.0
            )

    @patch("src.api.explorer.generate_mandelbrot_grid")
    @patch("src.api.explorer.grid_to_image_bytes")
    def test_router_render_mandelbrot(self, mock_img, mock_mandel):
        mock_mandel.return_value = []
        mock_img.return_value = b"render_data"
        
        response = self.client.get("/render?fractal_type=mandelbrot")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"render_data")

    @patch("src.api.explorer.generate_julia_grid")
    @patch("src.api.explorer.grid_to_image_bytes")
    def test_router_render_julia(self, mock_img, mock_julia):
        mock_julia.return_value = []
        mock_img.return_value = b"julia_data"
        
        response = self.client.get("/render?fractal_type=julia")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"julia_data")

    @patch("src.api.explorer.generate_mandelbrot_grid")
    @patch("src.api.explorer.grid_to_image_bytes")
    @patch.object(Path, "write_bytes")
    def test_router_save_no_ext(self, mock_write, mock_img, mock_mandel):
        mock_mandel.return_value = []
        mock_img.return_value = b"save_data"
        
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "test"
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "test.jpg")
        mock_write.assert_called_once_with(b"save_data")


if __name__ == "__main__":
    unittest.main()
