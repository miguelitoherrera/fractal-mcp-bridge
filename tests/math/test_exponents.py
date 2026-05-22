import unittest

import numpy as np

from fractal_mcp.math.exponents import exponential_set, generate_exponential_grid


class TestExponents(unittest.TestCase):
    expected_max_iterations = 10
    x_min = -2.0
    x_max = 2.0
    y_min = -2.0
    y_max = 2.0

    # Descriptive complex constants for reviewers
    z_origin = complex(0.0, 0.0)
    c_origin = complex(0.0, 0.0)
    z_escape_start = complex(1.0, 0.0)
    c_escape_param = complex(2.0, 0.0)
    c_default = complex(1.0, 0.0)
    z_real_boundary_escape = complex(51.0, 0.0)
    c_real_boundary_escape = complex(1.0, 0.0)

    def test_exponential_set_bounded(self) -> None:
        """Test a point that stays bounded."""
        # c=0 means z stays at 0
        iters = exponential_set(self.z_origin, self.c_origin, self.expected_max_iterations)
        expected_iters = float(self.expected_max_iterations)
        self.assertEqual(iters, expected_iters)

    def test_exponential_set_escapes(self) -> None:
        """Test a point that escapes."""
        # Start at z=1, c=2.0 -> escapes quickly
        escape_iterations = exponential_set(self.z_escape_start, self.c_escape_param, self.expected_max_iterations)
        expected_max_iterations = float(self.expected_max_iterations)
        # Escape counts are continuous floats due to the smooth coloring formula
        self.assertLess(escape_iterations, expected_max_iterations)

    def test_generate_exponential_grid(self) -> None:
        """Test grid generation dimensions and types."""
        width, height = 10, 5
        max_iter = 20
        grid = generate_exponential_grid(
            self.x_min, self.x_max, self.y_min, self.y_max, self.c_default, width, height, max_iter
        )

        expected_shape = (height, width)
        expected_dtype = np.float32
        expected_max_val = max_iter
        expected_min_val = 0.0

        self.assertEqual(grid.shape, expected_shape)
        self.assertEqual(grid.dtype, expected_dtype)
        self.assertTrue(np.all(grid <= expected_max_val))
        self.assertTrue(np.all(grid >= expected_min_val))

    def test_exponential_set_boundary_escape(self) -> None:
        # Start immediately outside the absolute real boundary of 50.0.
        # Escape counts are continuous floats due to the smooth coloring formula.
        iters = exponential_set(self.z_real_boundary_escape, self.c_real_boundary_escape, self.expected_max_iterations)
        expected_escape_threshold = 2.0
        self.assertLess(iters, expected_escape_threshold)

    def test_generate_exponential_grid_inverted(self) -> None:
        # Inverted coordinate boundaries should produce a grid whose shared coordinates
        # mathematically match the normal grid in reverse order.
        width, height = 10, 10
        max_iter = 20
        normal_grid = generate_exponential_grid(
            self.x_min, self.x_max, self.y_min, self.y_max, self.c_default, width, height, max_iter
        )
        inverted_grid = generate_exponential_grid(
            self.x_max, self.x_min, self.y_max, self.y_min, self.c_default, width, height, max_iter
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

    def test_generate_exponential_grid_zero_dimension(self) -> None:
        # Zero dimension raises ZeroDivisionError
        width_zero, width_normal = 0, 10
        height_zero, height_normal = 0, 10
        max_iter = 20
        with self.assertRaises(ZeroDivisionError):
            generate_exponential_grid(
                self.x_min, self.x_max, self.y_min, self.y_max, self.c_default, width_zero, height_normal, max_iter
            )
        with self.assertRaises(ZeroDivisionError):
            generate_exponential_grid(
                self.x_min, self.x_max, self.y_min, self.y_max, self.c_default, width_normal, height_zero, max_iter
            )


if __name__ == "__main__":
    unittest.main()
