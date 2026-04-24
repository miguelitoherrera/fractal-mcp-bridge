import numpy as np
import numba


@numba.njit(fastmath=True)
def julia(
    z_initial: complex,
    c: complex,
    max_iterations: int,
):
    """
    Checks if a starting complex number 'z_initial' escapes under iteration
    with a fixed constant 'c'.

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


# Parallelization happens here by using numba.prange for the rows.
@numba.njit(parallel=True, fastmath=True)
def julia_set(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    width: int,
    height: int,
    max_iterations,
):
    """
    Generates and displays an image of the Julia set.

    Args:
        x_min(float): the min value for the real-axis window
        x_max(float): the max value for the real-axis window
        y_min(float): the min value for the imaginary-axis window
        y_max(float): the max value for the imaginary-axis window
        c(complex): The julia complex constant 'c'.
        width(int): pixel width of the output grid
        height(int): pixel height of the output grid
        max_iterations(int): The maximum number of iterations for each point.
    """
    # Pre-calculate steps for mapping pixel coordinates to complex plane
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    # Use dtype=np.uint32 based on max_iterations for better cache locality
    grid = np.empty((height, width), dtype=np.uint32)
    
    for y in numba.prange(height):
        # Move y-component calculation to outer loop
        z_imag = y_min + y * y_step
        for x in range(width):
            z_initial = complex(x_min + x * x_step, z_imag)
            grid[y, x] = julia(z_initial, c, max_iterations)
    return grid
