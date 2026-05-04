import unittest
from fractal_core.julia import julia
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
                f"Failed for z0={z_initial}, c={c}",
            )


if __name__ == "__main__":
    unittest.main()
