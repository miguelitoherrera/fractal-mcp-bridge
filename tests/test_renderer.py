# Tests for the fractal rendering engine.
import io
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image

from fractal_mcp.renderer import (
    grid_to_image_bytes,
    load_bokeh_palette,
    newton_to_image_bytes,
    render_fractal,
    suggest_filename,
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
    def test_suggest_filename_mandelbrot(self) -> None:
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, "Turbo", False)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_turbo.jpg")

    def test_suggest_filename_julia(self) -> None:
        name = suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, "Viridis", False, c=complex(-0.7, 0.27))
        self.assertEqual(name, "julia_c-0.700_0.270_x0.0000_y0.0000_viridis.jpg")

    def test_suggest_filename_newton(self) -> None:
        name = suggest_filename("newton", -2.0, 2.0, -2.0, 2.0, "Turbo", False, power=3.0)
        self.assertEqual(name, "newton_p3.0_x0.0000_y0.0000_turbo.jpg")

    def test_suggest_filename_reversed(self) -> None:
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, "Turbo", True)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_turbo_reversed.jpg")

    def test_suggest_filename_julia_none_c(self) -> None:
        # Test that passing None raises ValueError for julia
        with self.assertRaises(ValueError):
            suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, "Viridis", False)

    def test_suggest_filename_newton_none_power(self) -> None:
        # Test that passing None raises ValueError for newton
        with self.assertRaises(ValueError):
            suggest_filename("newton", -2.0, 2.0, -2.0, 2.0, "Turbo", False)

    def test_render_mandelbrot(self) -> None:
        img_bytes = render_fractal(
            "mandelbrot",
            X_MIN,
            X_MAX,
            Y_MIN,
            Y_MAX,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_render_julia(self) -> None:
        img_bytes = render_fractal(
            "julia",
            X_MIN,
            X_MAX,
            Y_MIN,
            Y_MAX,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
            c=complex(-0.7, 0.27),
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_render_newton(self) -> None:
        img_bytes = render_fractal(
            "newton",
            -2.0,
            2.0,
            -2.0,
            2.0,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
            power=3.0,
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_render_newton_none_power(self) -> None:
        # Test that passing None raises ValueError
        with self.assertRaises(ValueError):
            render_fractal(
                "newton",
                -2.0,
                2.0,
                -2.0,
                2.0,
                100,
                MAX_ITERATIONS,
                DEFAULT_COLORMAP,
                DEFAULT_REVERSE_COLORMAP,
            )

    def test_render_julia_none_c(self) -> None:
        # Test that passing None raises ValueError
        with self.assertRaises(ValueError):
            render_fractal(
                "julia",
                X_MIN,
                X_MAX,
                Y_MIN,
                Y_MAX,
                100,
                MAX_ITERATIONS,
                DEFAULT_COLORMAP,
                DEFAULT_REVERSE_COLORMAP,
            )

    def test_validate_params_invalid_coords(self) -> None:
        # Test x_min >= x_max
        with self.assertRaises(ValueError) as ctx:
            render_fractal("mandelbrot", 1.0, -1.0, -1.0, 1.0, 100, 100, "Turbo", False)
        self.assertIn("x_min must be strictly less than x_max", str(ctx.exception))

        # Test y_min >= y_max
        with self.assertRaises(ValueError) as ctx:
            render_fractal("mandelbrot", -1.0, 1.0, 1.0, -1.0, 100, 100, "Turbo", False)
        self.assertIn("y_min must be strictly less than y_max", str(ctx.exception))

    def test_validate_params_invalid_dimensions(self) -> None:
        # Test resolution <= 0
        with self.assertRaises(ValueError) as ctx:
            render_fractal("mandelbrot", -1.0, 1.0, -1.0, 1.0, 0, 100, "Turbo", False)
        self.assertIn("resolution must be strictly positive", str(ctx.exception))

        # Test max_iterations <= 0
        with self.assertRaises(ValueError) as ctx:
            render_fractal("mandelbrot", -1.0, 1.0, -1.0, 1.0, 100, 0, "Turbo", False)
        self.assertIn("max_iterations must be strictly positive", str(ctx.exception))

    def test_height_clamping(self) -> None:
        # Test that extremely narrow y range results in height of at least 1, not 0
        img_bytes = render_fractal("mandelbrot", -2.0, 1.0, 0.0, 0.0000001, 100, 100, "Turbo", False)
        self.assertIsInstance(img_bytes, bytes)

    def test_render_unsupported(self) -> None:
        # To test the actual ValueError in render_fractal:
        with self.assertRaises(ValueError):
            render_fractal(
                "invalid_fractal",
                X_MIN,
                X_MAX,
                Y_MIN,
                Y_MAX,
                100,
                MAX_ITERATIONS,
                DEFAULT_COLORMAP,
                DEFAULT_REVERSE_COLORMAP,
            )

    @patch("fractal_mcp.renderer.validate_fractal_params")
    def test_render_unsupported_bypass_validation(self, mock_validate: MagicMock) -> None:
        # Bypass validation step to cover the unsupported fractal raise block
        with self.assertRaises(ValueError) as ctx:
            render_fractal(
                "invalid_fractal",
                X_MIN,
                X_MAX,
                Y_MIN,
                Y_MAX,
                100,
                MAX_ITERATIONS,
                DEFAULT_COLORMAP,
                DEFAULT_REVERSE_COLORMAP,
            )
        self.assertIn("Unsupported fractal type", str(ctx.exception))

    def test_aspect_ratio_calculation(self) -> None:
        img_bytes = render_fractal(
            "mandelbrot",
            0.0,
            2.0,
            0.0,
            1.0,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    # Merged tests from test_image.py
    def test_suggest_filename_exponential(self) -> None:
        name = suggest_filename(
            "exponential",
            -2.0,
            1.0,
            -1.5,
            1.5,
            "Turbo",
            False,
            c=complex(1.0, 0.0),
        )
        self.assertEqual(name, "exponential_c1.000_0.000_x-0.5000_y0.0000_turbo.jpg")

    def test_render_exponential(self) -> None:
        img_bytes = render_fractal(
            "exponential",
            X_MIN,
            X_MAX,
            Y_MIN,
            Y_MAX,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
            c=complex(1.0, 0.0),
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_suggest_filename_sine(self) -> None:
        name = suggest_filename("sine", -2.0, 1.0, -1.5, 1.5, "Turbo", False, c=complex(1.0, 0.0))
        self.assertEqual(name, "sine_c1.000_0.000_x-0.5000_y0.0000_turbo.jpg")

    def test_render_sine(self) -> None:
        img_bytes = render_fractal(
            "sine",
            X_MIN,
            X_MAX,
            Y_MIN,
            Y_MAX,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
            c=complex(1.0, 0.0),
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_suggest_filename_cosine(self) -> None:
        name = suggest_filename("cosine", -2.0, 1.0, -1.5, 1.5, "Turbo", False, c=complex(1.0, 0.0))
        self.assertEqual(name, "cosine_c1.000_0.000_x-0.5000_y0.0000_turbo.jpg")

    def test_render_cosine(self) -> None:
        img_bytes = render_fractal(
            "cosine",
            X_MIN,
            X_MAX,
            Y_MIN,
            Y_MAX,
            100,
            MAX_ITERATIONS,
            DEFAULT_COLORMAP,
            DEFAULT_REVERSE_COLORMAP,
            c=complex(1.0, 0.0),
        )
        self.assertIsInstance(img_bytes, bytes)
        self.assertGreater(len(img_bytes), 0)

    def test_grid_to_image_bytes(self) -> None:
        grid = np.zeros((10, 10), dtype=np.float32)
        grid[0:5, 0:5] = 50.0
        grid[5:10, 5:10] = 100.0

        max_iter = 100
        jpeg_bytes = grid_to_image_bytes(grid, max_iter, "Inferno", False)

        self.assertIsInstance(jpeg_bytes, bytes)
        img = Image.open(io.BytesIO(jpeg_bytes))
        self.assertEqual(img.format, "JPEG")
        self.assertEqual(img.size, (10, 10))

    def test_newton_to_image_bytes(self) -> None:
        roots = np.zeros((10, 10), dtype=np.float32)
        roots[0:5, 0:5] = 0.0
        roots[5:10, 5:10] = 0.5
        iters = np.ones((10, 10), dtype=np.float32) * 10.0

        max_iter = 100
        jpeg_bytes = newton_to_image_bytes(roots, iters, max_iter, "Inferno", False)

        self.assertIsInstance(jpeg_bytes, bytes)
        img = Image.open(io.BytesIO(jpeg_bytes))
        self.assertEqual(img.format, "JPEG")
        self.assertEqual(img.size, (10, 10))

    def test_newton_to_image_bytes_reversed(self) -> None:
        roots = np.linspace(0, 1, 100, dtype=np.float32).reshape((10, 10))
        iters = np.ones((10, 10), dtype=np.float32) * 5.0
        max_iter = 100
        bytes_normal = newton_to_image_bytes(roots, iters, max_iter, "Inferno", False)
        bytes_reversed = newton_to_image_bytes(roots, iters, max_iter, "Inferno", True)
        self.assertNotEqual(bytes_normal, bytes_reversed)

    def test_grid_to_image_bytes_colormap(self) -> None:
        grid = np.linspace(1, 10, 100, dtype=np.float32).reshape((10, 10))

        bytes_inferno = grid_to_image_bytes(grid, 10, "Inferno", False)
        bytes_viridis = grid_to_image_bytes(grid, 10, "Viridis", False)

        self.assertNotEqual(bytes_inferno, bytes_viridis)

    def test_grid_to_image_bytes_reverse(self) -> None:
        grid = np.linspace(1, 10, 100, dtype=np.float32).reshape((10, 10))

        bytes_normal = grid_to_image_bytes(grid, 10, "Inferno", False)
        bytes_reversed = grid_to_image_bytes(grid, 10, "Inferno", True)

        self.assertNotEqual(bytes_normal, bytes_reversed)

    def test_load_bokeh_palette_existing_256(self) -> None:
        palette = load_bokeh_palette("Viridis")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_missing(self) -> None:
        with self.assertRaises(KeyError):
            load_bokeh_palette("NonExistentPalette123")

    def test_load_bokeh_palette_interpolate(self) -> None:
        palette = load_bokeh_palette("Pastel1")
        self.assertEqual(palette.shape, (256, 3))

    def test_load_bokeh_palette_case_insensitive(self) -> None:
        palette_lower = load_bokeh_palette("viridis")
        palette_capital = load_bokeh_palette("Viridis")
        np.testing.assert_array_equal(palette_lower, palette_capital)


if __name__ == "__main__":
    unittest.main()
