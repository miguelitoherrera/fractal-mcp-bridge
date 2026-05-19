# Numba-accelerated Newton's method fractal calculation.
import math

import numba
import numpy as np


@numba.njit(fastmath=True)
def newton_set(
    z: complex,
    power: float,
    max_iterations: int,
) -> tuple[float, float]:
    """
    Determines which root a point converges to using Newton's method for f(z) = z^p - 1.

    Calculation Logic:
        1. Iterative Mapping: z_{n+1} = z_n - f(z_n) / f'(z_n).
           For f(z) = z^p - 1, f'(z) = p * z^(p-1).
        2. Convergence: We stop when the absolute step size is below a tolerance (1e-6).
        3. Root Mapping: The final complex phase (angle) of 'z' identifies which root
           it reached.

    Args:
        z: Initial complex coordinate.
        power: The exponent 'p' in z^p - 1.
        max_iterations: Maximum iteration depth.

    Returns:
        A tuple (angle_normalized, iteration_count).
        angle_normalized is in [0.0, 1.0], identifying the root.
        iteration_count is the number of steps taken.
    """
    z_real, z_imag = z.real, z.imag
    tolerance_sq = 1e-12

    for i in range(max_iterations):
        # We perform complex arithmetic manually to ensure Numba optimization.
        # z^p = r^p * (cos(p*theta) + i*sin(p*theta))
        r_sq = z_real * z_real + z_imag * z_imag
        if r_sq == 0.0:
            return 0.0, float(max_iterations)

        r = math.sqrt(r_sq)
        theta = math.atan2(z_imag, z_real)

        # f(z) = z^p - 1
        f_real, f_imag = (
            math.pow(r, power) * math.cos(power * theta) - 1.0,
            math.pow(r, power) * math.sin(power * theta),
        )

        # f'(z) = p * z^(p-1)
        p_minus_1 = power - 1.0
        r_p_minus_1 = math.pow(r, p_minus_1)
        f_prime_real, f_prime_imag = (
            power * r_p_minus_1 * math.cos(p_minus_1 * theta),
            power * r_p_minus_1 * math.sin(p_minus_1 * theta),
        )

        # Step = f(z) / f'(z)
        # (a+bi)/(c+di) = (ac+bd)/(c^2+d^2) + i(bc-ad)/(c^2+d^2)
        denom = f_prime_real * f_prime_real + f_prime_imag * f_prime_imag
        if denom == 0.0:
            break

        step_real, step_imag = (
            (f_real * f_prime_real + f_imag * f_prime_imag) / denom,
            (f_imag * f_prime_real - f_real * f_prime_imag) / denom,
        )

        z_real, z_imag = z_real - step_real, z_imag - step_imag

        if step_real * step_real + step_imag * step_imag < tolerance_sq:
            angle = math.atan2(z_imag, z_real)
            if angle < 0:
                angle += 2.0 * math.pi
            return angle / (2.0 * math.pi), float(i)

    return 0.0, float(max_iterations)


@numba.njit(parallel=True, fastmath=True)
def generate_newton_grid(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    power: float,
    width: int,
    height: int,
    max_iterations: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates grids of Newton fractal root angles and iteration counts.

    Args:
        x_min: Minimum real value.
        x_max: Maximum real value.
        y_min: Minimum imaginary value.
        y_max: Maximum imaginary value.
        power: Exponent for the Newton iteration.
        width: Pixel width of the grid.
        height: Pixel height of the grid.
        max_iterations: Maximum iteration depth for each point.

    Returns:
        A tuple of (roots_grid, iters_grid) as 2D float32 arrays.
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    roots_grid = np.empty((height, width), dtype=np.float32)
    iters_grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z = complex(x_min + x * x_step, y_min + y * y_step)
            angle, iters = newton_set(z, power, max_iterations)
            roots_grid[y, x] = angle
            iters_grid[y, x] = iters

    return roots_grid, iters_grid
