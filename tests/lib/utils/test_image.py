import unittest
import numpy as np
from PIL import Image
import io
from utils.image import (
    grid_to_image_bytes, load_bokeh_palette,
    generate_mandelbrot_grid, generate_julia_grid
)

class TestImageUtils(unittest.TestCase):
    def test_generate_mandelbrot_grid(self):
        res = 10
        grid = generate_mandelbrot_grid(-2.0, 1.0, -1.5, 1.5, res, res, max_iterations=10)
        self.assertEqual(grid.shape, (res, res))
        self.assertEqual(grid.dtype, np.uint32)

    def test_generate_julia_grid(self):
        res = 10
        grid = generate_julia_grid(-2.0, 2.0, -2.0, 2.0, complex(0, 0), res, res, max_iterations=10)
        self.assertEqual(grid.shape, (res, res))
        self.assertEqual(grid.dtype, np.uint32)

    def test_grid_to_image_bytes_jpeg(self):
        grid = np.zeros((10, 10), dtype=np.uint32)
        grid[0:5, 0:5] = 50 
        grid[5:10, 5:10] = 100
        
        max_iter = 100
        jpeg_bytes = grid_to_image_bytes(
            grid, max_iter, fmt="jpeg", quality=80, colormap="Inferno", reverse=False
        )
        
        self.assertIsInstance(jpeg_bytes, bytes)
        img = Image.open(io.BytesIO(jpeg_bytes))
        self.assertEqual(img.format, "JPEG")
        self.assertEqual(img.size, (10, 10))

    def test_grid_to_image_bytes_png(self):
        grid = np.ones((5, 5), dtype=np.uint32) * 10
        grid[2, 2] = 0
        
        png_bytes = grid_to_image_bytes(
            grid, max_iterations=20, fmt="png", quality=100, colormap="Viridis", reverse=True
        )
        
        self.assertIsInstance(png_bytes, bytes)
        img = Image.open(io.BytesIO(png_bytes))
        self.assertEqual(img.format, "PNG")
        self.assertEqual(img.size, (5, 5))

    def test_grid_to_image_bytes_colormap(self):
        grid = np.linspace(1, 10, 100, dtype=np.uint32).reshape((10, 10))
        
        bytes_inferno = grid_to_image_bytes(grid, 10, "png", 90, colormap="Inferno")
        bytes_viridis = grid_to_image_bytes(grid, 10, "png", 90, colormap="Viridis")
        
        self.assertNotEqual(bytes_inferno, bytes_viridis)

    def test_load_bokeh_palette_existing_256(self):
        palette = load_bokeh_palette("Viridis")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_missing_fallback(self):
        palette_missing = load_bokeh_palette("NonExistentPalette123")
        palette_turbo = load_bokeh_palette("Turbo")
        np.testing.assert_array_equal(palette_missing, palette_turbo)

    def test_load_bokeh_palette_interpolate(self):
        palette = load_bokeh_palette("Pastel1")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_case_insensitive(self):
        palette_lower = load_bokeh_palette("viridis")
        palette_capital = load_bokeh_palette("Viridis")
        np.testing.assert_array_equal(palette_lower, palette_capital)


if __name__ == "__main__":
    unittest.main()
