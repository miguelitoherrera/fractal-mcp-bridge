import numba
import numpy as np


@numba.njit(fastmath=True)
def mandelbrot(
    c: complex,
    max_iterations: int,
) -> float:
    """
    Determines the smooth escape count for a point in the Mandelbrot set.

    Calculation Logic:
        1. Iterative Mapping: We apply the function z_{n+1} = z_n^2 + c starting
           with z_0 = 0. A point 'c' belongs to the Mandelbrot set if the sequence
           remains bounded (absolute value <= 2).
        2. Escape Time: For points that escape, we find the first 'n' such that
           |z_n| > bailout.
        3. Smooth Coloring (Renormalization): To eliminate discrete color bands,
           we use the fractional iteration count formula:
           nu = n + 1 - log2(log2(|z_n|))
           This "renormalizes" the escape time based on how far the point actually
           traveled beyond the bailout radius.

    Args:
        c: Complex point to test.
        max_iterations: Maximum iteration depth.

    Returns:
        Smooth iteration count (float) until escape, or max_iterations if bounded.
    """
    z_real = 0.0
    z_imag = 0.0

    # Using a larger bailout radius (2^8 = 256) for smoother coloring
    bailout = 256.0
    bailout_sq = bailout * bailout

    for i in range(max_iterations):
        # z = z^2 + c
        z_real_sq = z_real * z_real
        z_imag_sq = z_imag * z_imag

        if z_real_sq + z_imag_sq > bailout_sq:
            # Smooth coloring formula: v = i + 1 - log2(log2(|z|))
            # Since we have |z|^2, we use: v = i + 1 - log2(0.5 * log2(|z|^2))
            # Which simplifies to: v = i + 2 - log2(log2(|z|^2))
            z_abs_sq = z_real_sq + z_imag_sq
            mu = i + 1 - np.log2(np.log2(z_abs_sq) / 2.0)
            return float(mu)

        z_imag = 2.0 * z_real * z_imag + c.imag
        z_real = z_real_sq - z_imag_sq + c.real

    return float(max_iterations)


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
    Generates a grid of Mandelbrot set escape values using smooth coloring.

    Args:
        x_min: Minimum real value.
        x_max: Maximum real value.
        y_min: Minimum imaginary value.
        y_max: Maximum imaginary value.
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
            c = complex(x_min + x * x_step, y_min + y * y_step)
            grid[y, x] = mandelbrot(c, max_iterations)

    return grid
