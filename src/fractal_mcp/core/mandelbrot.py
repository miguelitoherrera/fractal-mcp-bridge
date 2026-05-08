import numba
import numpy as np


@numba.njit(fastmath=True)
def mandelbrot(
    c: complex,
    max_iterations: int,
) -> int:
    """
    Determines the escape count for a point in the Mandelbrot set.

    Args:
        c: Complex point to test.
        max_iterations: Maximum iteration depth.

    Returns:
        Iteration count until escape, or max_iterations if bounded.
    """
    z_real = 0.0
    z_imag = 0.0

    for i in range(max_iterations):
        # z = z^2 + c
        z_real, z_imag = (
            z_real * z_real - z_imag * z_imag + c.real,
            2.0 * z_real * z_imag + c.imag
        )
        # check if |z| > 2 (i.e. |z| squared > 4 for computational efficiency)
        if z_real * z_real + z_imag * z_imag > 4.0:
            return i

    return max_iterations


@numba.njit(parallel=True, fastmath=True)
def generate_mandelbrot_grid(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    max_iterations: int,
) -> np.ndarray:
    """
    Generates a grid of Mandelbrot set escape values.

    Args:
        x_min: Minimum real value.
        x_max: Maximum real value.
        y_min: Minimum imaginary value.
        y_max: Maximum imaginary value.
        width: Pixel width of the grid.
        height: Pixel height of the grid.
        max_iterations: Maximum iteration depth for each point.

    Returns:
        2D array of iteration counts (uint32).
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.uint32)
    
    for y in numba.prange(height):
        for x in range(width):
            c = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = mandelbrot(c, max_iterations)
            
    return grid
