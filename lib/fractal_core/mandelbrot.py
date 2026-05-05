"""these are the functions used in the mandelbrot algorithm"""

import numba
import numpy as np


@numba.njit(fastmath=True)
def mandelbrot(
    c: complex,
    max_iterations: int,
) -> int:

    """
    Checks if a single complex number 'c' is in the Mandelbrot set.
    
    The iteration follows the formula: z_{n+1} = z_n^2 + c, starting with z_0 = 0.
    A point 'c' is in the set if the sequence remains bounded (abs(z) <= 2.0).

    Args:
        c(complex): The complex number for the starting point.
        max_iterations(optional, int): The maximum number of iterations to perform.

    Returns: (int) The number of iterations until escape (max_iterations if it doesn't escape).
    """
    z_real = 0.0
    z_imag = 0.0
    z_real_sq = 0.0
    z_imag_sq = 0.0
    c_real = c.real
    c_imag = c.imag

    for i in range(max_iterations):
        # Calculate z^2 + c avoiding complex object creation overhead
        z_imag = 2.0 * z_real * z_imag + c_imag
        z_real = z_real_sq - z_imag_sq + c_real
        
        z_real_sq = z_real * z_real
        z_imag_sq = z_imag * z_imag

        # Check if abs(z) > 2.0  (equivalent to checking if abs(z)^2 > 4.0)
        if z_real_sq + z_imag_sq > 4.0:
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
):
    """Creates a grid of escape values for the Mandelbrot set in the complex plane"""
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.uint32)
    
    for y in numba.prange(height):
        c_imag = y_min + y * y_step
        for x in range(width):
            c = complex(x_min + x * x_step, c_imag)
            grid[y, x] = mandelbrot(c, max_iterations)
    return grid
