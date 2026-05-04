import unittest
from fractal_core.mandelbrot import mandelbrot
from fractal_core.config import MAX_ITERATIONS


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
                mandelbrot(c, MAX_ITERATIONS),
                expected_iterations,
                f"Failed for c={c}",
            )


if __name__ == "__main__":
    unittest.main()
