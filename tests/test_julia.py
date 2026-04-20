import unittest
from fractal_core.julia import julia, julia_set
from fractal_core.config import MAX_ITERATIONS, RESOLUTION


class TestJulia(unittest.TestCase):
    def test_julia(self):
        test_params = [
            # z_initial, c, expected_iterations
            [complex(0, 0), complex(-0.8, 0.156), MAX_ITERATIONS],  # Douady rabbit
            [complex(0, 0), complex(0.285, 0.01), 18],  # dendrite
            [complex(0, 0), complex(0, -1), MAX_ITERATIONS],  # San Marco fractal
            [complex(0, 0), complex(0), MAX_ITERATIONS],  # simple circle
        ]
        for z_initial, c, expected_iterations in test_params:
            self.assertEqual(
                julia(z_initial, c, max_iterations=MAX_ITERATIONS),
                expected_iterations,
            )

    def test_julia_set(self):
        x_min = 0
        x_max = 1
        y_min = 0
        y_max = 1
        c = complex(-0.8, 0.156)  # Douady rabbit

        width = RESOLUTION
        height = round(width * (y_max - y_min) / (x_max - x_min))

        # generate set for first quadrant of complex plane
        grid = julia_set(0, 1, 0, 1, c, width, height, MAX_ITERATIONS)
        self.assertEqual(
            grid.shape,
            (RESOLUTION, RESOLUTION),
        )
        self.assertEqual(grid[0][0], MAX_ITERATIONS)  # first set point (0, 0) has max escape value


if __name__ == '__main__':
    unittest.main()
