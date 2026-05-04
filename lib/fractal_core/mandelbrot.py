"""these are the functions used in the mandelbrot algorithm"""

import numba
from fractal_core.config import MAX_ITERATIONS


@numba.njit(fastmath=True)
def mandelbrot(
    c: complex,
    max_iterations: int = MAX_ITERATIONS,
):
    """
    Checks if a single complex number 'c' is in the Mandelbrot set.

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
