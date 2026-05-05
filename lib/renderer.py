from dataclasses import dataclass
import numpy as np
from fractal_core.mandelbrot import generate_mandelbrot_grid
from fractal_core.julia import generate_julia_grid
from utils.image import grid_to_image_bytes

# Default Rendering Constants
RESOLUTION = 800
MAX_ITERATIONS = 100
DEFAULT_COLORMAP = "Turbo"
DEFAULT_REVERSE_COLORMAP = False
DEFAULT_JULIA_C = -0.7 + 0.27j
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

def suggest_filename(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    colormap: str,
    julia_c: complex = None
) -> str:
    """Generate a descriptive filename based on fractal parameters."""
    x_range = x_max - x_min
    x_center = x_min + x_range / 2
    y_center = y_min + (y_max - y_min) / 2

    name = f"{fractal_type}_x{x_center:.4f}_y{y_center:.4f}"

    if fractal_type == "julia" and julia_c is not None:
        name = f"{fractal_type}_c{julia_c.real:.3f}_{julia_c.imag:.3f}_x{x_center:.4f}_y{y_center:.4f}"

    return f"{name}_{colormap.lower()}.jpg"

def render_fractal(
    fractal_type: str,
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    y_min: float = Y_MIN,
    y_max: float = Y_MAX,
    resolution: int = RESOLUTION,
    max_iterations: int = MAX_ITERATIONS,
    colormap: str = DEFAULT_COLORMAP,
    reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP,
    julia_c: complex = None,
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
        c = julia_c if julia_c is not None else DEFAULT_JULIA_C
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations)
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
