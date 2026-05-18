import unittest

import numpy as np

from fractal_mcp.math.sine import generate_sine_grid, sine_set


class TestSine(unittest.TestCase):
    def test_sine_set_bounded(self) -> None:
        """Test a point that stays bounded."""
        # c=0 means z stays at 0
        self.assertEqual(sine_set(complex(0.0, 0.0), complex(0.0, 0.0), 10), 10.0)

    def test_sine_set_escapes(self) -> None:
        """Test a point that escapes."""
        # c=2.0, z=1.0j -> sin(i) = i sinh(1) -> 2.0i sinh(1)
        # sinh(1) approx 1.17 -> 2.35i. It will escape eventually.
        val = sine_set(complex(0.0, 1.0), complex(2.0, 0.0), 10)
        self.assertLess(val, 10.0)
        self.assertFalse(float(val).is_integer())

    def test_generate_sine_grid(self) -> None:
        """Test grid generation dimensions and types."""
        width, height = 10, 5
        max_iter = 20
        c_param = complex(1.0, 0.0)
        grid = generate_sine_grid(-2.0, 2.0, -2.0, 2.0, c_param, width, height, max_iter)

        self.assertEqual(grid.shape, (height, width))
        self.assertEqual(grid.dtype, np.float32)
        self.assertTrue(np.all(grid <= max_iter))
        self.assertTrue(np.all(grid >= 0))


if __name__ == "__main__":
    unittest.main()
