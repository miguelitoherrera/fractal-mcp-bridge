import unittest
from fractal_core.julia import julia


class TestJulia(unittest.TestCase):
    def test_julia(self):
        expected_max_iterations = 100
        test_params = [
            # z_initial, c, expected_iterations
            [complex(0, 0), complex(-0.8, 0.156), expected_max_iterations],  # Douady rabbit
            [complex(0, 0), complex(0.285, 0.01), 18],  # dendrite
            [complex(0, 0), complex(0, -1), expected_max_iterations],  # San Marco fractal
            [complex(0, 0), complex(0), expected_max_iterations],  # simple circle
            [complex(2, 0), complex(0, 0), 0],  # immediately escapes
            [complex(0, 2), complex(0, 0), 0],  # immediately escapes (imaginary)
            [complex(0.1, 0.1), complex(0, 0), expected_max_iterations],  # well within unit circle
        ]
        for z_initial, c, expected_iterations in test_params:
            self.assertEqual(
                julia(z_initial, c, expected_max_iterations),
                expected_iterations,
                f"Failed for z0={z_initial}, c={c}",
            )


if __name__ == "__main__":
    unittest.main()
