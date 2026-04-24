import unittest
from fractal_core.julia import julia, julia_set
from fractal_core.config import MAX_ITERATIONS


class TestJulia(unittest.TestCase):
    def test_julia(self):
        test_params = [
            # z_initial, c, expected_iterations
            [complex(0, 0), complex(-0.8, 0.156), MAX_ITERATIONS],  # Douady rabbit
            [complex(0, 0), complex(0.285, 0.01), 18],  # dendrite
            [complex(0, 0), complex(0, -1), MAX_ITERATIONS],  # San Marco fractal
            [complex(0, 0), complex(0), MAX_ITERATIONS],  # simple circle
            [complex(2, 0), complex(0, 0), 0],  # immediately escapes
            [complex(0, 2), complex(0, 0), 0],  # immediately escapes (imaginary)
            [complex(0.1, 0.1), complex(0, 0), MAX_ITERATIONS],  # well within unit circle
        ]
        for z_initial, c, expected_iterations in test_params:
            self.assertEqual(
                julia(z_initial, c, max_iterations=MAX_ITERATIONS),
                expected_iterations,
            )

    def test_julia_set_dimensions(self):
        # Test various resolutions
        resolutions = [(100, 100), (200, 100), (100, 200)]
        c = complex(0, 0)
        for width, height in resolutions:
            grid = julia_set(-1, 1, -1, 1, c, width, height, 50)
            self.assertEqual(grid.shape, (height, width))

    def test_julia_set_values(self):
        # Simple case: c=0, z0 should just be z0^2.
        # Points inside unit circle should stay, outside should escape.
        c = complex(0, 0)
        # Unit circle is within [-2, 2] x [-2, 2]
        # (0,0) is at index (5, 5) for a 10x10 grid on [-2, 2]
        grid = julia_set(-2, 2, -2, 2, c, 10, 10, 100)
        self.assertEqual(grid[5, 5], 100) # Center should not escape
        self.assertEqual(grid[0, 0], 0)   # corners (-2, -2) should escape immediately

    def test_julia_escape_branch(self):
        # specifically test an immediate escape to cover the line
        res = julia(complex(3, 3), complex(0, 0), max_iterations=10)
        self.assertEqual(res, 0)


if __name__ == '__main__':
    unittest.main()