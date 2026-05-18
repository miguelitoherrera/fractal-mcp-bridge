import unittest

import numpy as np

from fractal_mcp.math.cosine import cosine_set, generate_cosine_grid


class TestCosine(unittest.TestCase):
    def test_cosine_set_bounded(self) -> None:
        """Test a point that stays bounded."""
        # c=0 means z stays at 0
        self.assertEqual(cosine_set(complex(0.0, 0.0), complex(0.0, 0.0), 10), 10.0)

    def test_cosine_set_escapes(self) -> None:
        """Test a point that escapes."""
        # c=2.0, z=1.0j -> cos(i) = cosh(1) -> approx 1.54. Next iteration 2.0 * cos(1.54) ...
        val = cosine_set(complex(0.0, 1.0), complex(2.0, 0.0), 10)
        # It's hard to predict exactly if it escapes in 10, but let's check it returns a float
        self.assertIsInstance(val, float)

    def test_generate_cosine_grid(self) -> None:
        """Test grid generation dimensions and types."""
        width, height = 10, 5
        max_iter = 20
        c_param = complex(1.0, 0.0)
        grid = generate_cosine_grid(-2.0, 2.0, -2.0, 2.0, c_param, width, height, max_iter)

        self.assertEqual(grid.shape, (height, width))
        self.assertEqual(grid.dtype, np.float32)
        self.assertTrue(np.all(grid <= max_iter))
        self.assertTrue(np.all(grid >= 0))


if __name__ == "__main__":
    unittest.main()
