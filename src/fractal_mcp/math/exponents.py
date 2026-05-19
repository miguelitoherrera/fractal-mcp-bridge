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
    z_real, z_imag = z.real, z.imag
    for i in range(max_iterations):
        # Simultaneous assignment maintains mathematical correctness and minimalist style.
        # Real: exp(x) * (c.real * cos(y) - c.imag * sin(y))
        # Imag: exp(x) * (c.real * sin(y) + c.imag * cos(y))
        z_real, z_imag = (
            np.exp(z_real) * (c.real * np.cos(z_imag) - c.imag * np.sin(z_imag)),
            np.exp(z_real) * (c.real * np.sin(z_imag) + c.imag * np.cos(z_imag)),
        )

        if z_real > 50.0:
            # Smooth coloring approximation for exponential maps.
            mu = i + 1 - (z_real - 50.0) / z_real
            return float(mu)

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
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z = complex(x_min + x * x_step, y_max - y * y_step)
            grid[y, x] = exponential_set(z, c, max_iterations)

    return grid
