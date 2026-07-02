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
           To avoid division-of-infinity (inf/inf -> nan) when z^p overflows, we
           algebraically rewrite the step as: step = (z - z / z^p) / p.
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
    tolerance_sq = 1e-12

    for i in range(max_iterations):
        if not (math.isfinite(z.real) and math.isfinite(z.imag)):
            return 0.0, float(max_iterations)

        if abs(z) == 0.0:
            return 0.0, float(max_iterations)

        z_power = z**power
        if z_power == 0.0 or power == 0.0:
            break

        # Algebraically rewritten to prevent inf/inf -> nan when z_power overflows
        step = (z - z / z_power) / power
        z = z - step

        if step.real * step.real + step.imag * step.imag < tolerance_sq:
            angle = math.atan2(z.imag, z.real)
            if angle < 0:
                angle += 2.0 * math.pi
            norm_angle = angle / (2.0 * math.pi)
            if norm_angle >= 0.999:
                norm_angle = 0.0
            return norm_angle, float(i)

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

    Notes:
        Maps top of image (y=0) to y_max to align math 'up' with screen 'top'.

        Pixel (x, y)      ->  Complex (Re, Im)
        --------------------------------------
        (0, 0)            ->  (x_min, y_max)
        (width, height)   ->  (x_max, y_min)

        Grid loops are duplicated across modules intentionally. Centralizing
        them would require passing the JIT-compiled element functions, which
        introduces performance overhead and prevents full Numba optimization.
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    roots_grid = np.empty((height, width), dtype=np.float32)
    iters_grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):  # type: ignore[attr-defined, no-untyped-call]
        for x in range(width):
            z = complex(x_min + x * x_step, y_max - y * y_step)
            angle, iters = newton_set(z, power, max_iterations)
            roots_grid[y, x] = angle
            iters_grid[y, x] = iters

    return roots_grid, iters_grid
