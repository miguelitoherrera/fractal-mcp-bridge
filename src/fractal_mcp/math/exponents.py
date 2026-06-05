# Numba-accelerated exponential fractal set calculation.
import numba
import numpy as np


@numba.njit(fastmath=True)
def exponential_set(
    z: complex,
    c: complex,
    max_iterations: int,
) -> float:
    """
    Determines the escape count for a point in the exponential fractal set.

    Calculation Logic:
        1. Iterative Mapping: z_{n+1} = c * exp(z_n) starting with z_0 = z.
           exp(x + iy) = exp(x) * (cos(y) + i*sin(y))
        2. Escape Condition: Re(z) > 50.
        3. Smooth Coloring: Adapted for exponential growth.

    Args:
        z: Starting complex value (initial z).
        c: Fixed complex constant.
        max_iterations: Maximum iteration depth.

    Returns:
        Smooth iteration count (float) until escape, or max_iterations if bounded.
    """
    if z.real > 50.0:
        return 0.0

    for i in range(max_iterations):
        prev_real = z.real
        z = c * np.exp(z)

        if z.real > 50.0:
            denom = z.real - prev_real
            mu = i + (50.0 - prev_real) / denom if denom > 0.0 else float(i)
            return max(0.0, float(mu))

    return float(max_iterations)


@numba.njit(parallel=True, fastmath=True)
def generate_exponential_grid(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    width: int,
    height: int,
    max_iterations: int,
) -> np.ndarray:
    """
    Generates a grid of exponential fractal escape values.

    Args:
        x_min: Minimum real value.
        x_max: Maximum real value.
        y_min: Minimum imaginary value.
        y_max: Maximum imaginary value.
        c: Fixed complex constant.
        width: Pixel width of the grid.
        height: Pixel height of the grid.
        max_iterations: Maximum iteration depth for each point.

    Returns:
        2D array of smooth iteration counts (float32).

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
    grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z = complex(x_min + x * x_step, y_max - y * y_step)
            grid[y, x] = exponential_set(z, c, max_iterations)

    return grid
