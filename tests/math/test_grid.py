# Unit tests for JIT-accelerated grid generation factory.
import unittest

import numba
import numpy as np

from fractal_mcp.math.grid import make_grid_generator


@numba.njit(fastmath=True)
def dummy_escape_func(z: complex, max_iterations: int) -> float:
    """Simple escape function for verification."""
    return float(z.real + z.imag + max_iterations)


@numba.njit(fastmath=True)
def dummy_escape_func_with_args(z: complex, multiplier: float, offset: float, max_iterations: int) -> float:
    """Simple escape function accepting extra arguments."""
    return float((z.real + z.imag) * multiplier + offset + max_iterations)


class TestGridGenerator(unittest.TestCase):
    def test_make_grid_generator_basic(self) -> None:
        # Create a generator using the dummy evaluator
        generator = make_grid_generator(dummy_escape_func)

        # Generate a small 3x4 grid
        # x_min=-1.0, x_max=1.0, y_min=-1.0, y_max=1.0, width=4, height=3, max_iterations=10
        grid = generator(-1.0, 1.0, -1.0, 1.0, 4, 3, 10)

        self.assertEqual(grid.shape, (3, 4))
        self.assertEqual(grid.dtype, np.float32)

        # Calculations:
        # x_step = (1.0 - (-1.0)) / 4 = 0.5
        # y_step = (1.0 - (-1.0)) / 3 = 0.66666667
        #
        # For pixel (0, 0):
        # z = complex(x_min + 0 * x_step, y_max - 0 * y_step) = complex(-1.0, 1.0)
        # dummy_escape_func(-1.0 + 1.0j, 10) -> -1.0 + 1.0 + 10 = 10.0
        self.assertAlmostEqual(grid[0, 0], 10.0, places=5)

        # For pixel (2, 2):
        # z = complex(-1.0 + 2 * 0.5, 1.0 - 2 * (2.0/3.0)) = complex(0.0, -1/3)
        # dummy_escape_func(0.0 - 0.33333333j, 10) -> 0.0 - 0.33333333 + 10 = 9.666667
        self.assertAlmostEqual(grid[2, 2], 9.666667, places=5)

    def test_make_grid_generator_with_args(self) -> None:
        # Create a generator requiring extra arguments
        generator = make_grid_generator(dummy_escape_func_with_args)

        # Generate a small 3x4 grid passing extra JIT arguments (multiplier=2.5, offset=12.0)
        grid = generator(-1.0, 1.0, -1.0, 1.0, 4, 3, 10, 2.5, 12.0)

        self.assertEqual(grid.shape, (3, 4))
        self.assertEqual(grid.dtype, np.float32)

        # Calculations:
        # For pixel (0, 0): z = -1.0 + 1.0j
        # dummy_escape_func_with_args(-1.0 + 1.0j, 2.5, 12.0, 10)
        #   -> (-1.0 + 1.0) * 2.5 + 12.0 + 10 = 22.0
        self.assertAlmostEqual(grid[0, 0], 22.0, places=5)


if __name__ == "__main__":
    unittest.main()
