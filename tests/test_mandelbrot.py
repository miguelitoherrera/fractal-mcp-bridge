import unittest
from fractal_core.mandelbrot import mandelbrot, mandelbrot_set
from fractal_core.config import MAX_ITERATIONS, RESOLUTION


class TestMandelbrot(unittest.TestCase):
    def test_mandelbrot(self):
        test_params = [
            # c, expected_iterations
            [complex(0, 0), MAX_ITERATIONS],
            [complex(0, 1), MAX_ITERATIONS],
            [complex(1, 1), 1],
            [complex(0.5, 0.5), 4],
        ]
        for c, expected_iterations in test_params:
            self.assertEqual(
                mandelbrot(c, max_iterations=MAX_ITERATIONS),
                expected_iterations,
            )

    def test_mandelbrot_set(self):
        # generate set for first quadrant of complex plane
        x_min = 0
        x_max = 1
        y_min = 0
        y_max = 1
        width = RESOLUTION
        height = round(width * (y_max - y_min) / (x_max - x_min))
        grid = mandelbrot_set(0, 1, 0, 1, width, height, MAX_ITERATIONS)
        self.assertEqual(
            grid.shape,
            (RESOLUTION, RESOLUTION),
        )
        self.assertEqual(grid[0][0], MAX_ITERATIONS)  # first set point (0, 0) has max escape value


if __name__ == '__main__':
    unittest.main()
