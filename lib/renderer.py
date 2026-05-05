from dataclasses import dataclass
import numpy as np
from fractal_core.mandelbrot import generate_mandelbrot_grid
from fractal_core.julia import generate_julia_grid
from utils.image import grid_to_image_bytes

# Default Rendering Constants
RESOLUTION = 800
MAX_ITERATIONS = 100
X_MIN = -2.0
X_MAX = 1.0
Y_MIN = -1.5
Y_MAX = 1.5

@dataclass
class FractalResult:
    """Contract for fractal rendering results."""
    image_bytes: bytes
    mean_escape: float
    grid_shape: tuple[int, int]

def render_fractal(
    fractal_type: str,
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    y_min: float = Y_MIN,
    y_max: float = Y_MAX,
    resolution: int = RESOLUTION,
    max_iterations: int = MAX_ITERATIONS,
    colormap: str = "Inferno",
    reverse_colormap: bool = False,
    julia_c: complex = -0.7 + 0.27j,
) -> FractalResult:
    """
    Unified orchestration for rendering fractals.
    Calculates aspect ratio, generates the grid, computes metadata, and converts to image bytes.
    """
    # Calculate height based on aspect ratio to prevent stretching
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    
    if fractal_type == "mandelbrot":
        grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, width, height, max_iterations)
    elif fractal_type == "julia":
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, julia_c, width, height, max_iterations)
    else:
        raise ValueError(f"Unsupported fractal type: {fractal_type}")
        
    mean_escape = float(np.mean(grid))
    
    img_bytes = grid_to_image_bytes(
        grid, max_iterations, colormap, reverse_colormap
    )
    
    return FractalResult(
        image_bytes=img_bytes,
        mean_escape=round(mean_escape, 2),
        grid_shape=grid.shape
    )
