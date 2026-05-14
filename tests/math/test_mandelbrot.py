import unittest

import numpy as np

from fractal_mcp.math.mandelbrot import generate_mandelbrot_grid, mandelbrot


class TestMandelbrot(unittest.TestCase):
    expected_max_iterations = 100

    def test_mandelbrot(self):
        test_params = [
            # c, expected_iterations
            [complex(0, 0), self.expected_max_iterations],
            [complex(0, 1), self.expected_max_iterations],
            [complex(1, 1), 2],
            [complex(0.5, 0.5), 5],
            [complex(-2, 0), self.expected_max_iterations],
            [complex(2.1, 0), 2],
        ]
        for c, expected_iterations in test_params:
            self.assertEqual(
                round(mandelbrot(c, self.expected_max_iterations)),
                expected_iterations,
                f"Failed for c={c}",
            )

    def test_generate_mandelbrot_grid(self):
        res = 10
        grid = generate_mandelbrot_grid(
            -2.0, 1.0, -1.5, 1.5, res, res, max_iterations=self.expected_max_iterations
        )
        self.assertEqual(grid.shape, (res, res))
        self.assertEqual(grid.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
