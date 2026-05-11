import io
from PIL import Image
import numpy as np
from bokeh.palettes import all_palettes
from fractal_mcp.core.mandelbrot import generate_mandelbrot_grid
from fractal_mcp.core.julia import generate_julia_grid


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
        arr = np.stack([
            np.interp(indices, np.arange(len(arr)), arr[:, c]).astype(np.uint8)
            for c in range(3)
        ], axis=1)
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
           are usually rendered as the first color in the palette (typically black 
           in our convention).

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

def validate_fractal_params(fractal_type: str, julia_c: complex | None):
    """Business logic for fractal parameter consistency."""
    if fractal_type == "julia" and julia_c is None:
        raise ValueError("julia_c must be provided for Julia fractals")
    if fractal_type not in ["mandelbrot", "julia"]:
        raise ValueError(f"Unsupported fractal type: {fractal_type}")


def suggest_filename(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    colormap: str,
    reverse_colormap: bool,
    julia_c: complex | None = None
) -> str:
    """Generate a descriptive filename based on fractal parameters."""
    validate_fractal_params(fractal_type, julia_c)
    
    x_range = x_max - x_min
    x_center = x_min + x_range / 2
    y_center = y_min + (y_max - y_min) / 2

    name = f"{fractal_type}_x{x_center:.4f}_y{y_center:.4f}"

    if fractal_type == "julia":
        name = f"{fractal_type}_c{julia_c.real:.3f}_{julia_c.imag:.3f}_x{x_center:.4f}_y{y_center:.4f}"

    reversed_suffix = "_reversed" if reverse_colormap else ""
    return f"{name}_{colormap.lower()}{reversed_suffix}.jpg"

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
    julia_c: complex | None = None,
) -> bytes:
    """
    Unified orchestration for rendering fractals.
    Calculates aspect ratio, generates the grid, and converts to image bytes.
    """
    validate_fractal_params(fractal_type, julia_c)
    
    # Calculate height based on aspect ratio to prevent stretching
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))

    if fractal_type == "mandelbrot":
        grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, width, height, max_iterations)
    elif fractal_type ==  'julia':
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, julia_c, width, height, max_iterations)

    return grid_to_image_bytes(grid, max_iterations, colormap, reverse_colormap)
