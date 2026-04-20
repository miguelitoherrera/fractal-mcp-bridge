"""these are the functions used in the mandelbrot algorithm"""

import numpy as np
import numba


@numba.njit
def mandelbrot(
    c: complex,
    max_iterations: int,
):
    """
    Checks if a single complex number 'c' is in the Mandelbrot set.

    Args:
        c(complex): The complex number for the starting point.
        max_iterations(optional, int): The maximum number of iterations to perform.

    Returns: (int) The number of iterations until escape (max_iterations if it doesn't escape).
    """
    z = 0
    for i in range(max_iterations):
        z = z*z + c
        if abs(z) > 2:
            return i
    return max_iterations


# Parallelization happens here by using numba.prange for the rows.
@numba.jit(nopython=True, parallel=True)
def mandelbrot_set(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    max_iterations: int,
):
    """
    Creates a grid of escape values for complex points in the window
    (x_min, x_max) x (y_min, y_max).

    Args:
        x_min(float): the min value for the real-axis window
        x_max(float): the max value for the real-axis window
        y_min(float): the min value for the imaginary-axis window
        y_max(float): the max value for the imaginary-axis window
        width(int): pixel width of the output grid
        height(int): pixel height of the output grid
        max_iterations(int): max iterations before escaping
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    grid = np.zeros((height, width))
    for y in numba.prange(height):
        for x in range(width):
            c = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = mandelbrot(c, max_iterations)
    return grid
