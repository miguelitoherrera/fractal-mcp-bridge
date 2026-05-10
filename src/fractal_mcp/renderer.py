import io
from PIL import Image
import numpy as np
from bokeh.palettes import all_palettes
from fractal_mcp.core.mandelbrot import generate_mandelbrot_grid
from fractal_mcp.core.julia import generate_julia_grid


def load_bokeh_palette(name: str) -> np.ndarray:
    """
    Load a named Bokeh palette and return an (256, 3) uint8 RGB array.
    Falls back to Turbo if the name is not found.
    """
    family = all_palettes.get(name) or all_palettes.get(name.capitalize()) or all_palettes["Turbo"]
        
    size = 256 if 256 in family else max(family.keys())
    hex_colors = family[size]

    # Convert hex colors to a Nx3 uint8 numpy array.
    rgb_list = []
    for hex_code in hex_colors:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        rgb_list.append((r, g, b))
    arr = np.array(rgb_list, dtype=np.uint8)

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
    Convert escape-iteration grid to a JPEG byte string using a named
    Bokeh palette. Hardcoded to JPEG with 95 quality.
    """
    palette = load_bokeh_palette(colormap)
    if reverse_colormap:
        palette = palette[::-1]

    # Avoid zero division and mathematical errors in log scaling by forcing 0 to 1 temporarily
    safe_grid = np.where(grid == 0, 1, grid)

    # Scale from 0 to 1
    t = np.clip(safe_grid / max_iterations, 0.0, 1.0)

    # Logarithmic scaling spreads out the colors near the fractal boundaries
    t_smooth = np.log1p(t * 9) / np.log(10)

    # Map the 0-1 range to palette indices 1-255
    idx = np.clip((t_smooth * 254 + 1).astype(np.int32), 1, 255)

    # Force points that escaped immediately to use index 0 (black)
    idx[grid == 0] = 0

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
