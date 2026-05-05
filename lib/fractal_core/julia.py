import numba
import numpy as np


@numba.njit(fastmath=True)
def julia(
    z_initial: complex,
    c: complex,
    max_iterations: int,
):
    """
    Checks if a starting complex number 'z_initial' escapes under iteration
    with a fixed constant 'c'.
    
    The iteration follows the formula: z_{n+1} = z_n^2 + c, starting with z_0 = z_initial.
    The sequence is computed for a fixed 'c' and varying starting points 'z_initial'.

    Args:
        z_initial(complex): The complex number for the starting point (z0).
        c(complex): The fixed complex constant for the set.
        max_iterations(int): The maximum number of iterations for each point.

    Returns: (int) The number of iterations until escape (max_iterations if it doesn't escape).
    """
    z_real = z_initial.real
    z_imag = z_initial.imag
    z_real_sq = z_real * z_real
    z_imag_sq = z_imag * z_imag
    c_real = c.real
    c_imag = c.imag

    for i in range(max_iterations):
        z_imag = 2.0 * z_real * z_imag + c_imag
        z_real = z_real_sq - z_imag_sq + c_real
        
        z_real_sq = z_real * z_real
        z_imag_sq = z_imag * z_imag

        # Check if abs(z) > 2.0 (equivalent to checking if abs(z)^2 > 4.0)
        if z_real_sq + z_imag_sq > 4.0:
            return i

    return max_iterations


@numba.njit(parallel=True, fastmath=True)
def generate_julia_grid(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    width: int,
    height: int,
    max_iterations: int,
):
    """Creates a grid of escape values for the Julia set in the complex plane"""
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.uint32)
    
    for y in numba.prange(height):
        z_imag = y_min + y * y_step
        for x in range(width):
            z_initial = complex(x_min + x * x_step, z_imag)
            grid[y, x] = julia(z_initial, c, max_iterations)
    return grid
