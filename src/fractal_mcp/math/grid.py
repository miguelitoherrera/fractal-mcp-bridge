# Shared mathematical loop utility for JIT-accelerated fractal generation.
import typing

import numba
import numpy as np

# Generic element evaluation function typing
ElementFunc = typing.Callable[..., float]


def make_grid_generator(
    element_func: ElementFunc,
) -> typing.Callable[..., np.ndarray]:
    """
    Factory that JIT-compiles a parallelized grid generator for a given element-wise escape function.

    Args:
        element_func: JIT-compiled element-wise function (e.g. mandelbrot, julia).

    Returns:
        A parallel JIT-compiled grid generation function.
    """

    @numba.njit(parallel=True, fastmath=True)
    def generate_grid(
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        width: int,
        height: int,
        max_iterations: int,
        *args: typing.Any,
    ) -> np.ndarray:
        x_step = (x_max - x_min) / width
        y_step = (y_max - y_min) / height
        grid = np.empty((height, width), dtype=np.float32)

        for y in numba.prange(height):  # type: ignore[attr-defined, no-untyped-call]
            for x in range(width):
                z = complex(x_min + x * x_step, y_max - y * y_step)
                grid[y, x] = element_func(z, *args, max_iterations)

        return grid

    return typing.cast(typing.Callable[..., np.ndarray], generate_grid)
