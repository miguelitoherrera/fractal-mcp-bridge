# Unit tests for Newton's method fractal calculations.
import unittest

import numpy as np

from fractal_mcp.math.newton import generate_newton_grid, newton_set


class TestNewton(unittest.TestCase):
    expected_max_iterations = 100
    x_min = -2.0
    x_max = 2.0
    y_min = -2.0
    y_max = 2.0

    # Descriptive complex constants for reviewers
    z_convergence_start = complex(1.5, 0.0)
    z_origin = complex(0.0, 0.0)
    z_non_convergent_start = complex(0.0, 1.0)
    z_zero_derivative_start = complex(1.0, 1.0)
    z_power_four_start = complex(0.1, 1.5)

    def test_newton_set_convergence(self) -> None:
        # For f(z) = z^3 - 1, roots are at 1, e^(2pi/3)i, e^(4pi/3)i
        # Root 1 has angle 0.0
        angle, iters = newton_set(self.z_convergence_start, 3.0, self.expected_max_iterations)
        expected_root_angle = 0.0
        expected_converged_threshold = 10
        self.assertAlmostEqual(angle, expected_root_angle)
        self.assertLess(iters, expected_converged_threshold)

        # Origin should return max_iterations
        angle, iters = newton_set(self.z_origin, 3.0, self.expected_max_iterations)
        expected_iters = float(self.expected_max_iterations)
        self.assertEqual(iters, expected_iters)

    def test_newton_set_max_iterations(self) -> None:
        # A point that takes a long time or doesn't converge
        # Newton's method can be chaotic.
        max_iterations = 2
        angle, iters = newton_set(self.z_non_convergent_start, 3.0, max_iterations)
        expected_iterations = 2
        self.assertEqual(iters, expected_iterations)

    def test_newton_set_zero_derivative(self) -> None:
        # If power is 0.0, the derivative is zero, leading to denom == 0.0 and a break
        angle, iters = newton_set(self.z_zero_derivative_start, 0.0, self.expected_max_iterations)
        expected_root_angle = 0.0
        expected_iters = float(self.expected_max_iterations)
        self.assertEqual(angle, expected_root_angle)
        self.assertEqual(iters, expected_iters)

    def test_newton_set_different_power(self) -> None:
        # For f(z) = z^4 - 1, roots are 1, i, -1, -i
        # Root i has angle 0.25 (normalized from pi/2)
        angle, iters = newton_set(self.z_power_four_start, 4.0, self.expected_max_iterations)
        expected_root_angle = 0.25
        expected_converged_threshold = 10
        self.assertAlmostEqual(angle, expected_root_angle)
        self.assertLess(iters, expected_converged_threshold)

    def test_newton_set_negative_angle(self) -> None:
        # Starting point in the lower half-plane to converge to a root with negative imaginary part.
        # For f(z) = z^3 - 1, roots are 1, e^(2pi/3)i, e^(4pi/3)i.
        # e^(4pi/3) has phase 4pi/3 which is > pi, so math.atan2 returns -2pi/3 (< 0).
        # Normalization maps it to 4pi/3, which is (4/3 * pi) / (2pi) = 2/3 = 0.6666...
        z_start = complex(-0.5, -0.8)
        angle, iters = newton_set(z_start, 3.0, self.expected_max_iterations)
        self.assertAlmostEqual(angle, 2.0 / 3.0)
        self.assertLess(iters, 15)

    def test_newton_non_finite(self) -> None:
        # Test nan and inf starting coordinates
        for z in (complex(float("nan"), 1.0), complex(1.0, float("inf")), complex(float("-inf"), float("nan"))):
            angle, iters = newton_set(z, 3.0, self.expected_max_iterations)
            self.assertEqual(angle, 0.0)
            self.assertEqual(iters, float(self.expected_max_iterations))

    def test_generate_newton_grid(self) -> None:
        width, height = 10, 10
        roots, iters = generate_newton_grid(
            self.x_min, self.x_max, self.y_min, self.y_max, 3.0, width, height, self.expected_max_iterations
        )
        expected_shape = (height, width)
        expected_dtype = np.float32
        self.assertEqual(roots.shape, expected_shape)
        self.assertEqual(iters.shape, expected_shape)
        self.assertEqual(roots.dtype, expected_dtype)
        self.assertEqual(iters.dtype, expected_dtype)

    def test_newton_set_high_exponent(self) -> None:
        # For f(z) = z^7 - 1, check convergence to one of the roots
        # Start close to e^(i * 2pi/7)
        angle_rad = 2.0 * np.pi / 7.0
        z_start = complex(1.2 * np.cos(angle_rad), 1.2 * np.sin(angle_rad))
        angle, iters = newton_set(z_start, 7.0, self.expected_max_iterations)
        # Expected root index 1/7
        expected_root_angle = 1.0 / 7.0
        expected_precision = 4
        expected_converged_threshold = 15
        self.assertAlmostEqual(angle, expected_root_angle, places=expected_precision)
        self.assertLess(iters, expected_converged_threshold)

    def test_newton_set_low_derivative_origin_guard(self) -> None:
        # Origin start where r_sq == 0 returns early
        angle, iters = newton_set(self.z_origin, 3.0, self.expected_max_iterations)
        expected_iters = float(self.expected_max_iterations)
        expected_root_angle = 0.0
        self.assertEqual(iters, expected_iters)
        self.assertEqual(angle, expected_root_angle)

    def test_generate_newton_grid_inverted(self) -> None:
        # Inverted coordinate boundaries should produce a grid whose shared coordinates
        # mathematically match the normal grid in reverse order.
        width, height = 10, 10
        normal_roots, normal_iters = generate_newton_grid(
            self.x_min, self.x_max, self.y_min, self.y_max, 3.0, width, height, self.expected_max_iterations
        )
        inverted_roots, inverted_iters = generate_newton_grid(
            self.x_max, self.x_min, self.y_max, self.y_min, 3.0, width, height, self.expected_max_iterations
        )

        expected_shape = (height, width)
        self.assertEqual(inverted_roots.shape, expected_shape)
        self.assertEqual(inverted_iters.shape, expected_shape)

        # Verify mirroring of generated values for shared coordinates.
        # Exclude y=5 (the exact real axis) where chaotic boundaries and tiny floating-point
        # variations can lead to equivalent normalized angles (e.g. 0.0 vs 1.0) converging differently.
        expected_precision = 4
        for y in range(1, height):
            if y == 5:
                continue
            for x in range(1, width):
                self.assertAlmostEqual(
                    inverted_roots[y, x], normal_roots[height - y, width - x], places=expected_precision
                )
                self.assertAlmostEqual(
                    inverted_iters[y, x], normal_iters[height - y, width - x], places=expected_precision
                )

    def test_generate_newton_grid_zero_dimension(self) -> None:
        # Zero dimension should raise ZeroDivisionError in grid calculations
        width_zero, width_normal = 0, 10
        height_zero, height_normal = 0, 10
        with self.assertRaises(ZeroDivisionError):
            generate_newton_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                3.0,
                width_zero,
                height_normal,
                self.expected_max_iterations,
            )
        with self.assertRaises(ZeroDivisionError):
            generate_newton_grid(
                self.x_min,
                self.x_max,
                self.y_min,
                self.y_max,
                3.0,
                width_normal,
                height_zero,
                self.expected_max_iterations,
            )


if __name__ == "__main__":
    unittest.main()
