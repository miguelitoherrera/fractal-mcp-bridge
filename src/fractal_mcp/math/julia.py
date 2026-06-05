# Numba-accelerated Julia set calculation.
import numba
import numpy as np


@numba.njit(fastmath=True)
def julia(
    z: complex,
    c: complex,
    max_iterations: int,
) -> float:
    """
    Determines the smooth escape count for a point in the Julia set.

    Calculation Logic:
        1. Iterative Mapping: We apply the function z_{n+1} = z_n^2 + c starting
           with an initial variable z and a fixed complex constant 'c'.
        2. Escape Time: We iterate until the point escapes the bailout radius
           (|z| > bailout) or we reach max_iterations.
        3. Smooth Coloring (Renormalization): To prevent "staircase" color bands,
           we calculate a fractional escape value:
           nu = n + 1 - log2(log(abs(z)) / log(bailout))
           Simplified for bailout=256 (2^8): nu = n + 1 - log2(log2(|z|)).
           This maps the escape speed to a continuous scale.

    Args:
        z: Starting complex value.
        c: Fixed complex constant.
        max_iterations: Maximum iteration depth.

    Returns:
        Smooth iteration count (float) until escape, or max_iterations if bounded.
    """
    # Using a larger bailout radius (2^8 = 256) for smoother coloring
    bailout = 256.0
    bailout_sq = bailout * bailout

    z_real, z_imag = z.real, z.imag

    for i in range(max_iterations):
        z_abs_sq = z_real * z_real + z_imag * z_imag
        if z_abs_sq > bailout_sq:
            # Smooth coloring formula: v = i + 2 - log2(log2(|z|^2))
            mu = i + 2 - np.log2(np.log2(z_abs_sq))
            return float(mu)

        # z = z^2 + c
        z_real, z_imag = (
            z_real * z_real - z_imag * z_imag + c.real,
            2.0 * z_real * z_imag + c.imag,
        )

    return float(max_iterations)


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
) -> np.ndarray:
    """
    Generates a grid of Julia set escape values using smooth coloring.

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

        Grid loops are duplicated across modules intentionally. Centralizing
        them would require passing the JIT-compiled element functions, which
        introduces performance overhead and prevents full Numba optimization.
    """
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    grid = np.empty((height, width), dtype=np.float32)

    for y in numba.prange(height):
        for x in range(width):
            z_initial = complex(x_min + x * x_step, y_max - y * y_step)
            grid[y, x] = julia(z_initial, c, max_iterations)

    return grid
