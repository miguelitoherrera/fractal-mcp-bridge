import io
from pathlib import Path

import numpy as np
from bokeh.palettes import all_palettes
from PIL import Image

from fractal_mcp.math.cosine import generate_cosine_grid
from fractal_mcp.math.exponents import generate_exponential_grid
from fractal_mcp.math.julia import generate_julia_grid
from fractal_mcp.math.mandelbrot import generate_mandelbrot_grid
from fractal_mcp.math.newton import generate_newton_grid
from fractal_mcp.math.sine import generate_sine_grid

IMAGES_DIR = Path("images")


def ensure_images_dir() -> Path:
    """Ensure the images directory exists and return the Path object."""
    IMAGES_DIR.mkdir(exist_ok=True)
    return IMAGES_DIR


def load_bokeh_palette(name: str) -> np.ndarray:
    """
    Load a named Bokeh palette and return a standardized (256, 3) uint8 RGB array.
    The lookup is case-insensitive.
    """
    # Create a case-insensitive mapping of available palettes
    lowered_palettes = {k.lower(): v for k, v in all_palettes.items()}
    family = lowered_palettes.get(name.lower())

    if not family:
        raise KeyError(f"Palette '{name}' not found in Bokeh palettes.")

    # Pick the largest available size in the family
    max_size = max(family.keys())
    hex_colors = family[max_size]

    # Convert hex colors to a Nx3 uint8 numpy array.
    rgb_list = []
    for hex_code in hex_colors:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        rgb_list.append((r, g, b))
    arr = np.array(rgb_list, dtype=np.uint8)

    # Standardize to exactly 256 colors using linear interpolation
    if len(arr) != 256:
        indices = np.linspace(0, len(arr) - 1, 256)
        arr = np.stack([np.interp(indices, np.arange(len(arr)), arr[:, c]).astype(np.uint8) for c in range(3)], axis=1)
    return arr


def grid_to_image_bytes(
    grid: np.ndarray,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> bytes:
    """
    Convert a smooth escape-iteration grid to a JPEG image.

    Mapping Logic:
        1. Linear Mapping: Since the input grid uses renormalized (smooth) escape
           values, the iteration space is already linearized. We no longer need
           logarithmic scaling.
        2. Normalization: We map the range [1, max_iterations] to the palette
           range [0, 255].
        3. Background Protection: Points that never escaped (grid >= max_iterations)
           are naturally mapped to the end of the colormap range (index 255),
           contrasting with the early-escaping background points mapped near index 0.

    Args:
        grid: 2D float32 array of smooth iteration counts.
        max_iterations: The threshold used during generation.
        colormap: Name of the Bokeh colormap to apply.
        reverse_colormap: Whether to flip the color scale.

    Returns:
        JPEG-encoded bytes of the resulting fractal image.
    """
    palette = load_bokeh_palette(colormap)
    if reverse_colormap:
        palette = palette[::-1]

    # We shift by 1.0 to ensure that the very first escape (at n=1)
    # starts near index 0. We clip to handle immediate escapes.
    t = np.clip((grid - 1.0) / max_iterations, 0.0, 1.0)

    # Map the 0-1 range to palette indices 0-255.
    # Because our palette is standardized to 256 colors, this is direct.
    idx = (t * 255).astype(np.int32)

    rgb = palette[idx]

    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def newton_to_image_bytes(
    roots_grid: np.ndarray,
    iters_grid: np.ndarray,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> bytes:
    """
    Convert Newton fractal root and iteration grids to a shaded JPEG image.

    Args:
        roots_grid: 2D float32 array of normalized root angles [0.0, 1.0].
        iters_grid: 2D float32 array of iteration counts.
        max_iterations: Maximum iteration threshold.
        colormap: Name of the Bokeh colormap.
        reverse_colormap: Whether to flip the color scale.
    """
    palette = load_bokeh_palette(colormap)
    if reverse_colormap:
        palette = palette[::-1]

    # Map normalized root angle to palette index.
    root_idx = (np.clip(roots_grid, 0.0, 1.0) * 255).astype(np.int32)
    rgb = palette[root_idx]

    # Apply shading based on iterations (convergence speed).
    # Shading factor is 1.0 for immediate convergence, decreasing for slow convergence.
    shading = 1.0 - (iters_grid / max_iterations)
    shading = np.clip(shading, 0.2, 1.0)  # Maintain minimum visibility

    # Broadcast shading to RGB channels.
    rgb = (rgb.astype(np.float32) * shading[:, :, np.newaxis]).astype(np.uint8)

    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def validate_fractal_params(
    fractal_type: str,
    c: complex | None,
    power: float | None = None,
    x_min: float | None = None,
    x_max: float | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
    resolution: int | None = None,
    max_iterations: int | None = None,
) -> None:
    """Business logic for fractal parameter consistency."""
    if x_min is not None and x_max is not None and x_min >= x_max:
        raise ValueError("x_min must be strictly less than x_max")
    if y_min is not None and y_max is not None and y_min >= y_max:
        raise ValueError("y_min must be strictly less than y_max")
    if resolution is not None and resolution <= 0:
        raise ValueError("resolution must be strictly positive")
    if max_iterations is not None and max_iterations <= 0:
        raise ValueError("max_iterations must be strictly positive")
    if fractal_type in ["julia", "exponential", "sine", "cosine"] and c is None:
        raise ValueError(f"c must be provided for {fractal_type} fractals")
    if fractal_type == "newton" and power is None:
        raise ValueError("power must be provided for newton fractals")
    if fractal_type not in [
        "mandelbrot",
        "julia",
        "exponential",
        "sine",
        "cosine",
        "newton",
    ]:
        raise ValueError(f"Unsupported fractal type: {fractal_type}")


def suggest_filename(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
    c: complex | None = None,
    power: float | None = None,
) -> str:
    """Generate a descriptive filename based on fractal parameters."""
    validate_fractal_params(fractal_type, c, power, x_min, x_max, y_min, y_max, resolution, max_iterations)

    x_range = x_max - x_min
    x_center = x_min + x_range / 2
    y_center = y_min + (y_max - y_min) / 2

    name = f"{fractal_type}_x{x_center:.4f}_y{y_center:.4f}"

    if fractal_type in ["julia", "exponential", "sine", "cosine"]:
        assert c is not None
        name = f"{fractal_type}_c{c.real:.3f}_{c.imag:.3f}_x{x_center:.4f}_y{y_center:.4f}"
    elif fractal_type == "newton":
        assert power is not None
        name = f"newton_p{power:.1f}_x{x_center:.4f}_y{y_center:.4f}"

    reversed_suffix = "_reversed" if reverse_colormap else ""
    return f"{name}_res{resolution}_iter{max_iterations}_{colormap.lower()}{reversed_suffix}.jpg"


def render_fractal(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
    c: complex | None = None,
    power: float | None = None,
) -> bytes:
    """
    Unified orchestration for rendering fractals.
    Calculates aspect ratio, generates the grid, and converts to image bytes.
    """
    validate_fractal_params(fractal_type, c, power, x_min, x_max, y_min, y_max, resolution, max_iterations)

    # Calculate height based on aspect ratio to prevent stretching
    width = resolution
    height = max(1, round(width * (y_max - y_min) / (x_max - x_min)))

    if fractal_type == "mandelbrot":
        grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, width, height, max_iterations)
        return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
    elif fractal_type == "julia":
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations)
        return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
    elif fractal_type == "exponential":
        grid = generate_exponential_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations)
        return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
    elif fractal_type == "sine":
        grid = generate_sine_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations)
        return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
    elif fractal_type == "cosine":
        grid = generate_cosine_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations)
        return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
    elif fractal_type == "newton":
        assert power is not None
        roots, iters = generate_newton_grid(x_min, x_max, y_min, y_max, power, width, height, max_iterations)
        return newton_to_image_bytes(roots, iters, max_iterations, colormap, reverse_colormap)
    else:
        # Should be caught by validate_fractal_params
        raise ValueError(f"Unsupported fractal type: {fractal_type}")
