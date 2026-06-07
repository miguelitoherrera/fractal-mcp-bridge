# Unit tests for Julia set calculations.
import unittest

import numpy as np

from fractal_mcp.math.julia import generate_julia_grid, julia


class TestJulia(unittest.TestCase):
    expected_max_iterations = 100
    x_min = -2.0
    x_max = 2.0
    y_min = -2.0
    y_max = 2.0

    # Descriptive complex constants for reviewers
    c_default = complex(0.0, 0.0)
    z_extreme_escape = complex(1e10, 1e10)

    def test_julia(self) -> None:
        test_params = [
            # (z_initial, c, expected_iterations, label)
            (complex(0.0, 0.0), complex(-0.8, 0.156), self.expected_max_iterations, "Douady rabbit"),
            (complex(0.0, 0.0), complex(0.285, 0.01), 23, "dendrite"),
            (complex(0.0, 0.0), complex(0.0, -1.0), self.expected_max_iterations, "San Marco fractal"),
            (complex(0.0, 0.0), complex(0.0, 0.0), self.expected_max_iterations, "simple circle"),
            (complex(300.0, 0.0), complex(0.0, 0.0), 1, "immediate escape real"),
            (complex(0.0, 300.0), complex(0.0, 0.0), 1, "immediate escape imaginary"),
            (complex(0.1, 0.1), complex(0.0, 0.0), self.expected_max_iterations, "inside unit circle"),
        ]
        for z_initial, c, expected_iterations, label in test_params:
            iters = julia(z_initial, c, self.expected_max_iterations)
            self.assertEqual(
                round(iters),
                expected_iterations,
                f"Failed for {label} (z0={z_initial}, c={c})",
            )

    def test_generate_julia_grid(self) -> None:
        res = 10
        grid = generate_julia_grid(
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            self.c_default,
            res,
            res,
            self.expected_max_iterations,
        )
        expected_shape = (res, res)
        expected_dtype = np.float32
        self.assertEqual(grid.shape, expected_shape)
        self.assertEqual(grid.dtype, expected_dtype)

    def test_julia_extreme_escape(self) -> None:
        # Verify that an initial z far outside the unit/escape radius escapes immediately.
        # Escape counts are continuous floats due to the smooth coloring formula.
        iters = julia(self.z_extreme_escape, self.c_default, self.expected_max_iterations)
        expected_escape_threshold = 2.0
        self.assertLess(iters, expected_escape_threshold)

    def test_generate_julia_grid_inverted(self) -> None:
        # Inverted coordinate boundaries should produce a grid whose shared coordinates
        # mathematically match the normal grid in reverse order.
        width, height = 10, 10
        normal_grid = generate_julia_grid(
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            self.c_default,
            width,
            height,
            self.expected_max_iterations,
        )
        inverted_grid = generate_julia_grid(
            self.x_max,
            self.x_min,
            self.y_max,
            self.y_min,
            self.c_default,
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

    def test_generate_julia_grid_zero_dimension(self) -> None:
        # Zero dimension should raise ZeroDivisionError in grid generators
        width_zero, width_normal = 0, 10
        height_zero, height_normal = 0, 10
        with self.assertRaises(ZeroDivisionError):
            generate_julia_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                self.c_default,
                width_zero,
                height_normal,
                self.expected_max_iterations,
            )
        with self.assertRaises(ZeroDivisionError):
            generate_julia_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                self.c_default,
                width_normal,
                height_zero,
                self.expected_max_iterations,
            )


if __name__ == "__main__":
    unittest.main()
