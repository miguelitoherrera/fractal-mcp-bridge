import unittest
import numpy as np
from fractal_mcp.core.mandelbrot import mandelbrot, generate_mandelbrot_grid


class TestMandelbrot(unittest.TestCase):
    expected_max_iterations = 100
    def test_mandelbrot(self):
        test_params = [
            # c, expected_iterations
            [complex(0, 0), self.expected_max_iterations],
            [complex(0, 1), self.expected_max_iterations],
            [complex(1, 1), 1],
            [complex(0.5, 0.5), 4],
            [complex(-2, 0), self.expected_max_iterations],
            [complex(2.1, 0), 0],
        ]
        for c, expected_iterations in test_params:
            self.assertEqual(
                mandelbrot(c, self.expected_max_iterations),
                expected_iterations,
                f"Failed for c={c}",
            )

    def test_generate_mandelbrot_grid(self):
        res = 10
        grid = generate_mandelbrot_grid(-2.0, 1.0, -1.5, 1.5, res, res, max_iterations=self.expected_max_iterations)
        self.assertEqual(grid.shape, (res, res))
        self.assertEqual(grid.dtype, np.uint32)


if __name__ == "__main__":
    unittest.main()
