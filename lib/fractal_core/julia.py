import numpy as np
import numba


@numba.njit
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
    z = z_initial
    for i in range(max_iterations):
        z = z*z + c
        if abs(z) > 2:
            return i
    return max_iterations


# Parallelization happens here by using numba.prange for the rows.
@numba.jit(nopython=True, parallel=True)
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

    grid = np.zeros((height, width))
    for y in numba.prange(height):
        for x in range(width):
            z_initial = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = julia(z_initial, c, max_iterations)
    return grid
