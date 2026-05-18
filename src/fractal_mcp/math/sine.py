# Numba-accelerated sine fractal set calculation.
import numba
import numpy as np


@numba.njit(fastmath=True)
def sine_set(
    z: complex,
    c: complex,
    max_iterations: int,
) -> float:
    """
    Determines the escape count for a point in the sine fractal set.

    Calculation Logic:
        1. Iterative Mapping: z_{n+1} = c * sin(z_n) starting with z_0 = z.
           sin(x + iy) = sin(x)cosh(y) + i cos(x)sinh(y)
        2. Escape Condition: |Im(z)| > 50.
        3. Smooth Coloring: Adapted for sine growth.

    Args:
        z: Starting complex value (initial z).
        c: Fixed complex constant.
        max_iterations: Maximum iteration depth.

    Returns:
        Smooth iteration count (float) until escape, or max_iterations if bounded.
    """
    z_real, z_imag = z.real, z.imag
    for i in range(max_iterations):
        z_real, z_imag = (
            c.real * np.sin(z_real) * np.cosh(z_imag) - c.imag * np.cos(z_real) * np.sinh(z_imag),
            c.real * np.cos(z_real) * np.sinh(z_imag) + c.imag * np.sin(z_real) * np.cosh(z_imag),
        )

        if abs(z_imag) > 50.0:
            # Smooth coloring approximation
            mu = i + 1 - (abs(z_imag) - 50.0) / abs(z_imag)
            return float(mu)

    return float(max_iterations)


@numba.njit(parallel=True, fastmath=True)
def generate_sine_grid(
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
    Generates a grid of sine fractal escape values.

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
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = sine_set(z, c, max_iterations)

    return grid
