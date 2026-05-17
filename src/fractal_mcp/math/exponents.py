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
           To optimize, we separate real and imaginary parts:
           exp(z) = exp(x) * (cos(y) + i*sin(y))
           c * exp(z) = (c_real + i*c_imag) * exp(x) * (cos(y) + i*sin(y))
           x_{n+1} = exp(x) * (c_real*cos(y) - c_imag*sin(y))
           y_{n+1} = exp(x) * (c_real*sin(y) + c_imag*cos(y))
        2. Escape Condition: Re(z) > 50.
        3. Smooth Coloring: Adapted for exponential growth.

    Args:
        z: Starting complex value (initial z).
        c: Fixed complex constant.
        max_iterations: Maximum iteration depth.

    Returns:
        Smooth iteration count (float) until escape, or max_iterations if bounded.
    """
    z_real = z.real
    z_imag = z.imag

    # Bailout based on Real(z) > 50 as per literature/instructions.
    bailout_real = 50.0

    for i in range(max_iterations):
        # Separate real and imaginary calculations for performance
        exp_x = np.exp(z_real)
        cos_y = np.cos(z_imag)
        sin_y = np.sin(z_imag)

        # Update coordinates directly (intermediates already captured)
        z_real = exp_x * (c.real * cos_y - c.imag * sin_y)
        z_imag = exp_x * (c.real * sin_y + c.imag * cos_y)

        if z_real > bailout_real:
            # Smooth coloring approximation for exponential maps.
            # We use the overshoot of the real part beyond the bailout.
            mu = i + 1 - (z_real - bailout_real) / z_real
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
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = exponential_set(z, c, max_iterations)

    return grid
