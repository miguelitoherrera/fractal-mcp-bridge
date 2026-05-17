import unittest

import numpy as np

from fractal_mcp.math.exponents import exponential_set, generate_exponential_grid


class TestExponents(unittest.TestCase):
    def test_exponential_set_bounded(self):
        """Test a point that stays bounded."""
        # c=0 means z stays at 0
        self.assertEqual(exponential_set(complex(0.0, 0.0), complex(0.0, 0.0), 10), 10.0)

    def test_exponential_set_escapes(self):
        """Test a point that escapes."""
        # Start at z=1, c=2.0 -> escapes quickly
        val = exponential_set(complex(1.0, 0.0), complex(2.0, 0.0), 10)
        self.assertLess(val, 10.0)
        self.assertFalse(float(val).is_integer())

    def test_generate_exponential_grid(self):
        """Test grid generation dimensions and types."""
        width, height = 10, 5
        max_iter = 20
        c_param = complex(1.0, 0.0)
        grid = generate_exponential_grid(-2.0, 2.0, -2.0, 2.0, c_param, width, height, max_iter)

        self.assertEqual(grid.shape, (height, width))
        self.assertEqual(grid.dtype, np.float32)
        self.assertTrue(np.all(grid <= max_iter))
        self.assertTrue(np.all(grid >= 0))


if __name__ == "__main__":
    unittest.main()
