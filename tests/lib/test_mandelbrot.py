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
            [complex(-2, 0), MAX_ITERATIONS],
            [complex(2.1, 0), 0],
        ]
        for c, expected_iterations in test_params:
            self.assertEqual(
                mandelbrot(c, max_iterations=MAX_ITERATIONS),
                expected_iterations,
            )

    def test_mandelbrot_set_dimensions(self):
        # Test various resolutions
        resolutions = [(100, 100), (200, 100), (100, 200)]
        for width, height in resolutions:
            grid = mandelbrot_set(-2, 1, -1.5, 1.5, width, height, 50)
            self.assertEqual(grid.shape, (height, width))

    def test_mandelbrot_set_values(self):
        # (0,0) is in the set
        # (2,2) is definitely not
        grid = mandelbrot_set(-2, 2, -2, 2, 10, 10, 100)
        self.assertEqual(grid[5, 5], 100) # Near (0,0)
        self.assertEqual(grid[9, 9], 0)   # Near (2,2)


if __name__ == '__main__':
    unittest.main()
