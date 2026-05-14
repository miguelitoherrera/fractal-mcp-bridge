# Unit tests for Julia set calculations.
import unittest

import numpy as np

from fractal_mcp.math.julia import generate_julia_grid, julia


class TestJulia(unittest.TestCase):
    expected_max_iterations = 100

    def test_julia(self):
        test_params = [
            # z_initial, c, expected_iterations
            [
                complex(0, 0),
                complex(-0.8, 0.156),
                self.expected_max_iterations,
            ],  # Douady rabbit
            [complex(0, 0), complex(0.285, 0.01), 20],  # dendrite
            [
                complex(0, 0),
                complex(0, -1),
                self.expected_max_iterations,
            ],  # San Marco fractal
            [complex(0, 0), complex(0), self.expected_max_iterations],  # simple circle
            [complex(2, 0), complex(0, 0), 1],  # immediately escapes
            [complex(0, 2), complex(0, 0), 1],  # immediately escapes (imaginary)
            [
                complex(0.1, 0.1),
                complex(0, 0),
                self.expected_max_iterations,
            ],  # well within unit circle
        ]
        for z_initial, c, expected_iterations in test_params:
            self.assertEqual(
                round(julia(z_initial, c, self.expected_max_iterations)),
                expected_iterations,
                f"Failed for z0={z_initial}, c={c}",
            )

    def test_generate_julia_grid(self):
        res = 10
        grid = generate_julia_grid(
            -2.0,
            2.0,
            -2.0,
            2.0,
            complex(0, 0),
            res,
            res,
            max_iterations=self.expected_max_iterations,
        )
        self.assertEqual(grid.shape, (res, res))
        self.assertEqual(grid.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
