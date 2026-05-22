# Unit tests for Mandelbrot set calculations.
import unittest

import numpy as np

from fractal_mcp.math.mandelbrot import generate_mandelbrot_grid, mandelbrot


class TestMandelbrot(unittest.TestCase):
    expected_max_iterations = 100
    x_min = -2.0
    x_max = 1.0
    y_min = -1.5
    y_max = 1.5

    # Descriptive complex constants for reviewers
    c_extreme_escape = complex(1e10, 1e10)

    def test_mandelbrot(self) -> None:
        test_params = [
            # (c, expected_iterations, label)
            (complex(0.0, 0.0), self.expected_max_iterations, "origin"),
            (complex(0.0, 1.0), self.expected_max_iterations, "boundary point"),
            (complex(1.0, 1.0), 2, "outside cardioid"),
            (complex(0.5, 0.5), 5, "slow escaping point"),
            (complex(-2.0, 0.0), self.expected_max_iterations, "left antenna tip"),
            (complex(2.1, 0.0), 2, "escaping real tip"),
        ]
        for c, expected_iterations, label in test_params:
            iters = mandelbrot(c, self.expected_max_iterations)
            self.assertEqual(
                round(iters),
                expected_iterations,
                f"Failed for {label} (c={c})",
            )

    def test_generate_mandelbrot_grid(self) -> None:
        res = 10
        grid = generate_mandelbrot_grid(
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            res,
            res,
            self.expected_max_iterations,
        )
        expected_shape = (res, res)
        expected_dtype = np.float32
        self.assertEqual(grid.shape, expected_shape)
        self.assertEqual(grid.dtype, expected_dtype)

    def test_mandelbrot_extreme_escape(self) -> None:
        # Verify that a point far outside the bailout radius escapes immediately.
        # Escape counts are continuous floats due to the smooth coloring formula.
        iters = mandelbrot(self.c_extreme_escape, self.expected_max_iterations)
        expected_escape_threshold = 2.0
        self.assertLess(iters, expected_escape_threshold)

    def test_generate_mandelbrot_grid_inverted(self) -> None:
        # Inverted coordinate boundaries should produce a grid whose shared coordinates
        # mathematically match the normal grid in reverse order.
        width, height = 10, 10
        normal_grid = generate_mandelbrot_grid(
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            width,
            height,
            self.expected_max_iterations,
        )
        inverted_grid = generate_mandelbrot_grid(
            self.x_max,
            self.x_min,
            self.y_max,
            self.y_min,
            width,
            height,
            self.expected_max_iterations,
        )

        expected_shape = (height, width)
        expected_dtype = np.float32
        self.assertEqual(inverted_grid.shape, expected_shape)
        self.assertEqual(inverted_grid.dtype, expected_dtype)

        # Verify mirroring of generated values for shared coordinates
        expected_precision = 4
        for y in range(1, height):
            for x in range(1, width):
                self.assertAlmostEqual(
                    inverted_grid[y, x], normal_grid[height - y, width - x], places=expected_precision
                )

    def test_generate_mandelbrot_grid_zero_dimension(self) -> None:
        # Zero dimension should raise ZeroDivisionError due to step size calculations
        width_zero, width_normal = 0, 10
        height_zero, height_normal = 0, 10
        with self.assertRaises(ZeroDivisionError):
            generate_mandelbrot_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                width_zero,
                height_normal,
                self.expected_max_iterations,
            )
        with self.assertRaises(ZeroDivisionError):
            generate_mandelbrot_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                width_normal,
                height_zero,
                self.expected_max_iterations,
            )


if __name__ == "__main__":
    unittest.main()
