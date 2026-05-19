# Unit tests for Newton's method fractal calculations.
import unittest

import numpy as np

from fractal_mcp.math.newton import generate_newton_grid, newton_set


class TestNewton(unittest.TestCase):
    def test_newton_set_convergence(self) -> None:
        # For f(z) = z^3 - 1, roots are at 1, e^(2pi/3)i, e^(4pi/3)i
        # Root 1 has angle 0.0
        angle, iters = newton_set(complex(1.5, 0.0), 3.0, 100)
        self.assertAlmostEqual(angle, 0.0)
        self.assertLess(iters, 10)

        # Origin should return max_iterations
        angle, iters = newton_set(complex(0.0, 0.0), 3.0, 100)
        self.assertEqual(iters, 100)

    def test_newton_set_max_iterations(self) -> None:
        # A point that takes a long time or doesn't converge
        # Newton's method can be chaotic.
        angle, iters = newton_set(complex(0.0, 1.0), 3.0, 2)
        self.assertEqual(iters, 2)

    def test_newton_set_different_power(self) -> None:
        # For f(z) = z^4 - 1, roots are 1, i, -1, -i
        # Root i has angle 0.25 (normalized from pi/2)
        angle, iters = newton_set(complex(0.1, 1.5), 4.0, 100)
        self.assertAlmostEqual(angle, 0.25)
        self.assertLess(iters, 10)

    def test_generate_newton_grid(self) -> None:
        width, height = 10, 10
        roots, iters = generate_newton_grid(-2.0, 2.0, -2.0, 2.0, 3.0, width, height, 100)
        self.assertEqual(roots.shape, (height, width))
        self.assertEqual(iters.shape, (height, width))
        self.assertEqual(roots.dtype, np.float32)
        self.assertEqual(iters.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
