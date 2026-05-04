import numba
from fractal_core.config import MAX_ITERATIONS


@numba.njit(fastmath=True)
def julia(
    z_initial: complex,
    c: complex,
    max_iterations: int = MAX_ITERATIONS,
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
