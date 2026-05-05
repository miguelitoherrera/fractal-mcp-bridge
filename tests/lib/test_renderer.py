import unittest
from renderer import render_fractal, FractalResult

class TestRenderer(unittest.TestCase):
    def test_render_mandelbrot(self):
        result = render_fractal("mandelbrot", resolution=100)
        self.assertIsInstance(result, FractalResult)
        self.assertIsInstance(result.image_bytes, bytes)
        self.assertGreater(len(result.image_bytes), 0)
        self.assertIsInstance(result.mean_escape, float)
        self.assertEqual(result.grid_shape[1], 100)

    def test_render_julia(self):
        result = render_fractal("julia", resolution=100, julia_c=complex(-0.7, 0.27))
        self.assertIsInstance(result, FractalResult)
        self.assertIsInstance(result.image_bytes, bytes)
        self.assertGreater(len(result.image_bytes), 0)
        self.assertIsInstance(result.mean_escape, float)
        self.assertEqual(result.grid_shape[1], 100)

    def test_render_unsupported(self):
        with self.assertRaises(ValueError):
            render_fractal("invalid_fractal")

    def test_aspect_ratio_calculation(self):
        # Viewport is 2.0 wide (0.0 to 2.0) and 1.0 high (0.0 to 1.0)
        # Resolution 100 -> height should be 50
        result = render_fractal("mandelbrot", x_min=0.0, x_max=2.0, y_min=0.0, y_max=1.0, resolution=100)
        self.assertEqual(result.grid_shape, (50, 100))

if __name__ == "__main__":
    unittest.main()
