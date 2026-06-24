# Tests for the fractal rendering engine.
import io
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image

from fractal_mcp.renderer import (
    IMAGES_DIR,
    ensure_images_dir,
    grid_to_image_bytes,
    list_colormaps,
    load_bokeh_palette,
    newton_to_image_bytes,
    render_fractal,
    suggest_filename,
    validate_fractal_params,
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
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, 1600, 200, "Turbo", False)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_res1600_iter200_turbo.jpg")

    def test_suggest_filename_julia(self) -> None:
        name = suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, 1600, 200, "Viridis", False, c=complex(-0.7, 0.27))
        self.assertEqual(name, "julia_c-0.700_0.270_x0.0000_y0.0000_res1600_iter200_viridis.jpg")

    def test_suggest_filename_newton(self) -> None:
        name = suggest_filename("newton", -2.0, 2.0, -2.0, 2.0, 1600, 200, "Turbo", False, power=3.0)
        self.assertEqual(name, "newton_p3.0_x0.0000_y0.0000_res1600_iter200_turbo.jpg")

    def test_suggest_filename_reversed(self) -> None:
        name = suggest_filename("mandelbrot", -2.0, 1.0, -1.5, 1.5, 1600, 200, "Turbo", True)
        self.assertEqual(name, "mandelbrot_x-0.5000_y0.0000_res1600_iter200_turbo_reversed.jpg")

    def test_suggest_filename_deep_zoom(self) -> None:
        # Deep zoom where x_max - x_min is 1e-8
        name = suggest_filename(
            "mandelbrot", -0.74364388, -0.74364387, 0.13182590, 0.13182591, 1600, 200, "Turbo", False
        )
        # log10(1e-8) = -8, precision = max(4, 8 + 2) = 10
        self.assertEqual(name, "mandelbrot_x-0.7436438750_y0.1318259050_res1600_iter200_turbo.jpg")

    def test_ensure_images_dir(self) -> None:
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            res = ensure_images_dir()
            mock_mkdir.assert_called_once_with(exist_ok=True)
            self.assertEqual(res, IMAGES_DIR)

    def test_suggest_filename_julia_none_c(self) -> None:
        # Test that passing None raises ValueError for julia
        with self.assertRaises(ValueError):
            suggest_filename("julia", -2.0, 2.0, -2.0, 2.0, 1600, 200, "Viridis", False)

    def test_suggest_filename_newton_none_power(self) -> None:
        # Test that passing None raises ValueError for newton
        with self.assertRaises(ValueError):
            suggest_filename("newton", -2.0, 2.0, -2.0, 2.0, 1600, 200, "Turbo", False)

    def test_suggest_filename_newton_zero_power(self) -> None:
        # Test that passing power=0.0 raises ValueError for newton
        with self.assertRaisesRegex(ValueError, "Newton fractal power must not be zero"):
            suggest_filename("newton", -2.0, 2.0, -2.0, 2.0, 1600, 200, "Turbo", False, power=0.0)

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
        self.assertRaisesRegex(
            ValueError,
            "^x_min must be strictly less than x_max$",
            render_fractal,
            "mandelbrot",
            1.0,
            -1.0,
            -1.0,
            1.0,
            100,
            100,
            "Turbo",
            False,
        )

        # Test y_min >= y_max
        self.assertRaisesRegex(
            ValueError,
            "^y_min must be strictly less than y_max$",
            render_fractal,
            "mandelbrot",
            -1.0,
            1.0,
            1.0,
            -1.0,
            100,
            100,
            "Turbo",
            False,
        )

    def test_validate_params_invalid_dimensions(self) -> None:
        # Test resolution <= 0
        self.assertRaisesRegex(
            ValueError,
            "^resolution must be strictly positive and at most 12800$",
            render_fractal,
            "mandelbrot",
            -1.0,
            1.0,
            -1.0,
            1.0,
            0,
            100,
            "Turbo",
            False,
        )

        # Test max_iterations <= 0
        self.assertRaisesRegex(
            ValueError,
            "^max_iterations must be strictly positive$",
            render_fractal,
            "mandelbrot",
            -1.0,
            1.0,
            -1.0,
            1.0,
            100,
            0,
            "Turbo",
            False,
        )

    def test_resolution_limit_validation(self) -> None:
        # Test that resolution > 12800 raises ValueError
        self.assertRaisesRegex(
            ValueError,
            "^resolution must be strictly positive and at most 12800$",
            render_fractal,
            "mandelbrot",
            -1.0,
            1.0,
            -1.0,
            1.0,
            12801,
            100,
            "Turbo",
            False,
        )

    def test_unsupported_colormap_validation(self) -> None:
        # Test that unsupported colormap raises ValueError
        self.assertRaisesRegex(
            ValueError,
            "^Unsupported colormap 'InvalidColormap'\\.$",
            render_fractal,
            "mandelbrot",
            -1.0,
            1.0,
            -1.0,
            1.0,
            100,
            100,
            "InvalidColormap",
            False,
        )

    def test_validate_params_non_finite(self) -> None:
        # Test that validate_fractal_params raises ValueError on non-finite coordinates
        with self.assertRaises(ValueError) as ctx:
            validate_fractal_params(
                "mandelbrot",
                None,
                x_min=-1.0,
                x_max=float("inf"),
                y_min=-1.0,
                y_max=1.0,
            )
        self.assertEqual(str(ctx.exception), "Viewport coordinates must be finite numbers")

        # Test non-finite complex c
        with self.assertRaises(ValueError) as ctx:
            validate_fractal_params(
                "julia",
                complex(float("inf"), 0.0),
                x_min=-1.0,
                x_max=1.0,
                y_min=-1.0,
                y_max=1.0,
            )
        self.assertEqual(str(ctx.exception), "Complex parameter c must be a finite number")

        # Test non-finite power
        with self.assertRaises(ValueError) as ctx:
            validate_fractal_params(
                "newton",
                None,
                power=float("nan"),
                x_min=-1.0,
                x_max=1.0,
                y_min=-1.0,
                y_max=1.0,
            )
        self.assertEqual(str(ctx.exception), "power must be a finite number")

        # Test non-finite resolution
        with self.assertRaises(ValueError) as ctx:
            validate_fractal_params(
                "mandelbrot",
                None,
                x_min=-1.0,
                x_max=1.0,
                y_min=-1.0,
                y_max=1.0,
                resolution=float("nan"),  # type: ignore[arg-type]
            )
        self.assertEqual(str(ctx.exception), "resolution must be strictly positive and at most 12800")

        # Test non-finite max_iterations
        with self.assertRaises(ValueError) as ctx:
            validate_fractal_params(
                "mandelbrot",
                None,
                x_min=-1.0,
                x_max=1.0,
                y_min=-1.0,
                y_max=1.0,
                max_iterations=float("nan"),  # type: ignore[arg-type]
            )
        self.assertEqual(str(ctx.exception), "max_iterations must be strictly positive")

    def test_validate_fractal_params_floats(self) -> None:
        # Test that float resolution raises ValueError
        with self.assertRaises(ValueError):
            validate_fractal_params("mandelbrot", None, resolution=100.5)  # type: ignore[arg-type]
        # Test that float max_iterations raises ValueError
        with self.assertRaises(ValueError):
            validate_fractal_params("mandelbrot", None, max_iterations=10.5)  # type: ignore[arg-type]

    @patch("fractal_mcp.renderer.validate_fractal_params")
    def test_suggest_filename_zero_range(self, mock_validate: MagicMock) -> None:
        # Test that a coordinate range of 0 does not raise an OverflowError/log10 warning
        name = suggest_filename(
            "mandelbrot",
            0.5,
            0.5,
            0.5,
            0.5,
            100,
            100,
            "Turbo",
            False,
        )
        self.assertIn("_x0.50000000000000000000_y0.50000000000000000000", name)

    def test_suggest_filename_extreme_zoom_capped(self) -> None:
        # Test that suggest_filename under extremely deep zoom caps precision to 20 to prevent long filenames
        name = suggest_filename(
            "mandelbrot",
            0.0,
            1e-25,
            0.0,
            1e-25,
            100,
            100,
            "Turbo",
            False,
        )
        # Check that filename contains coordinates with capped precision (20 decimal places)
        self.assertIn("_x0.00000000000000000000_y0.00000000000000000000", name)
        # Entire filename length should be well within normal filesystem limits
        self.assertLess(len(name), 100)

    def test_render_unsupported(self) -> None:
        # To test the actual ValueError in render_fractal:
        self.assertRaises(
            ValueError,
            render_fractal,
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
        self.assertRaisesRegex(
            ValueError,
            "^Unsupported fractal type: invalid_fractal$",
            render_fractal,
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

    def test_aspect_ratio_calculation(self) -> None:
        self.assertRaisesRegex(
            ValueError,
            "^The coordinate viewport must have a 1-to-1 aspect ratio\\.$",
            render_fractal,
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

    # Merged tests from test_image.py
    def test_suggest_filename_exponential(self) -> None:
        name = suggest_filename(
            "exponential",
            -2.0,
            1.0,
            -1.5,
            1.5,
            1600,
            200,
            "Turbo",
            False,
            c=complex(1.0, 0.0),
        )
        self.assertEqual(name, "exponential_c1.000_0.000_x-0.5000_y0.0000_res1600_iter200_turbo.jpg")

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
        name = suggest_filename("sine", -2.0, 1.0, -1.5, 1.5, 1600, 200, "Turbo", False, c=complex(1.0, 0.0))
        self.assertEqual(name, "sine_c1.000_0.000_x-0.5000_y0.0000_res1600_iter200_turbo.jpg")

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
        name = suggest_filename("cosine", -2.0, 1.0, -1.5, 1.5, 1600, 200, "Turbo", False, c=complex(1.0, 0.0))
        self.assertEqual(name, "cosine_c1.000_0.000_x-0.5000_y0.0000_res1600_iter200_turbo.jpg")

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

    def test_list_colormaps(self) -> None:
        colormaps = list_colormaps()
        self.assertIn("Turbo", colormaps)
        self.assertIn("Viridis", colormaps)
        self.assertGreater(len(colormaps), 10)


if __name__ == "__main__":
    unittest.main()
