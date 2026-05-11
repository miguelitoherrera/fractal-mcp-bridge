import unittest
import numpy as np
from PIL import Image
import io
from fractal_mcp.renderer import (
    render_fractal, suggest_filename, grid_to_image_bytes, load_bokeh_palette
)

# Testing Constants (formerly from renderer.py)
RESOLUTION = 1600
MAX_ITERATIONS = 200
DEFAULT_COLORMAP = "Turbo"
DEFAULT_REVERSE_COLORMAP = False
DEFAULT_JULIA_C = -0.7 + 0.27j
X_MIN = -2.0
X_MAX = 1.0
Y_MIN = -1.5
Y_MAX = 1.5

class TestRenderer(unittest.TestCase):
    def test_suggest_filename_mandelbrot(self):
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, "Turbo", False, None)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_turbo.jpg")

    def test_suggest_filename_julia(self):
        name = suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, "Viridis", False, complex(-0.7, 0.27))
        self.assertEqual(name, "julia_c-0.700_0.270_x0.0000_y0.0000_viridis.jpg")

    def test_suggest_filename_reversed(self):
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, "Turbo", True, None)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_turbo_reversed.jpg")
        
    def test_suggest_filename_julia_none_c(self):
        # Test that passing None raises ValueError for julia
        with self.assertRaises(ValueError):
            suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, "Viridis", False, None)

    def test_render_mandelbrot(self):
        img_bytes = render_fractal(
            "mandelbrot", X_MIN, X_MAX, Y_MIN, Y_MAX, 100, MAX_ITERATIONS, 
            DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, None
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_render_julia(self):
        img_bytes = render_fractal(
            "julia", X_MIN, X_MAX, Y_MIN, Y_MAX, 100, MAX_ITERATIONS, 
            DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, complex(-0.7, 0.27)
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_render_julia_none_c(self):
        # Test that passing None raises ValueError
        with self.assertRaises(ValueError):
            render_fractal(
                "julia", X_MIN, X_MAX, Y_MIN, Y_MAX, 100, MAX_ITERATIONS, 
                DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, None
            )

    def test_render_unsupported(self):
        # To test the actual ValueError in render_fractal:
        with self.assertRaises(ValueError):
             render_fractal(
                "invalid_fractal", X_MIN, X_MAX, Y_MIN, Y_MAX, 100, MAX_ITERATIONS, 
                DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, None
            )

    def test_aspect_ratio_calculation(self):
        img_bytes = render_fractal(
            "mandelbrot", 0.0, 2.0, 0.0, 1.0, 100, MAX_ITERATIONS, 
            DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, None
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    # Merged tests from test_image.py
    def test_grid_to_image_bytes(self):
        grid = np.zeros((10, 10), dtype=np.float32)
        grid[0:5, 0:5] = 50.0
        grid[5:10, 5:10] = 100.0
        
        max_iter = 100
        jpeg_bytes = grid_to_image_bytes(grid, max_iter, "Inferno", False)
        
        self.assertIsInstance(jpeg_bytes, bytes)
        img = Image.open(io.BytesIO(jpeg_bytes))
        self.assertEqual(img.format, "JPEG")
        self.assertEqual(img.size, (10, 10))

    def test_grid_to_image_bytes_colormap(self):
        grid = np.linspace(1, 10, 100, dtype=np.float32).reshape((10, 10))
        
        bytes_inferno = grid_to_image_bytes(grid, 10, "Inferno", False)
        bytes_viridis = grid_to_image_bytes(grid, 10, "Viridis", False)
        
        self.assertNotEqual(bytes_inferno, bytes_viridis)

    def test_grid_to_image_bytes_reverse(self):
        grid = np.linspace(1, 10, 100, dtype=np.float32).reshape((10, 10))

        bytes_normal = grid_to_image_bytes(grid, 10, "Inferno", False)
        bytes_reversed = grid_to_image_bytes(grid, 10, "Inferno", True)
        
        self.assertNotEqual(bytes_normal, bytes_reversed)

    def test_load_bokeh_palette_existing_256(self):
        palette = load_bokeh_palette("Viridis")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_missing(self):
        with self.assertRaises(KeyError):
            load_bokeh_palette("NonExistentPalette123")

    def test_load_bokeh_palette_interpolate(self):
        palette = load_bokeh_palette("Pastel1")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_case_insensitive(self):
        palette_lower = load_bokeh_palette("viridis")
        palette_capital = load_bokeh_palette("Viridis")
        np.testing.assert_array_equal(palette_lower, palette_capital)


if __name__ == "__main__":
    unittest.main()
