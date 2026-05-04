import unittest
from fractal_core.mandelbrot import mandelbrot


class TestMandelbrot(unittest.TestCase):
    def test_mandelbrot(self):
        expected_max_iterations = 100
        test_params = [
            # c, expected_iterations
            [complex(0, 0), expected_max_iterations],
            [complex(0, 1), expected_max_iterations],
            [complex(1, 1), 1],
            [complex(0.5, 0.5), 4],
            [complex(-2, 0), expected_max_iterations],
            [complex(2.1, 0), 0],
        ]
        for c, expected_iterations in test_params:
            self.assertEqual(
                mandelbrot(c, expected_max_iterations),
                expected_iterations,
                f"Failed for c={c}",
            )


if __name__ == "__main__":
    unittest.main()
