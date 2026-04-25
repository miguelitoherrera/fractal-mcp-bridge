import io
from PIL import Image
import numpy as np
from bokeh.palettes import all_palettes, Inferno256


def _hex_to_rgb_array(hex_colors: list[str]) -> np.ndarray:
    """Convert a list of hex strings to a Nx3 uint8 numpy array."""
    # Convert '#RRGGBB' strings into tuples of integers: (R, G, B)
    rgb_list = []
    for hex_code in hex_colors:
        # Skip the '#' character and parse each 2-character hex pair
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        rgb_list.append((r, g, b))
        
    return np.array(rgb_list, dtype=np.uint8)


def load_bokeh_palette(name: str) -> np.ndarray:
    """
    Load a named Bokeh palette and return an (256, 3) uint8 RGB array.
    Falls back to Inferno if the name is not found.
    """
    family = all_palettes.get(name) or all_palettes.get(name.capitalize())
    
    # Fallback if palette doesn't exist
    if family is None:
        return _hex_to_rgb_array(Inferno256)
        
    size = 256 if 256 in family else max(family.keys())
    hex_colors = family[size]
    arr = _hex_to_rgb_array(hex_colors)
    
    # Resize to exactly 256 entries via linear interpolation if needed
    if len(arr) != 256:
        indices = np.linspace(0, len(arr) - 1, 256)
        arr = np.stack([
            np.interp(indices, np.arange(len(arr)), arr[:, c]).astype(np.uint8)
            for c in range(3)
        ], axis=1)
        
    return arr


def grid_to_image_bytes(
        grid,
        max_iterations: int,
        fmt: str,
        quality: int,
        colormap: str = "Inferno",
        reverse: bool = False,
) -> bytes:
    """
    Convert escape-iteration grid to a JPEG/PNG byte string using a named
    Bokeh palette.

    Parameters
    ----------
    grid          : 2-D array of escape iterations
    max_iterations: the max_iterations value used when computing grid
    fmt           : "jpeg" or "png"
    quality       : JPEG quality (ignored for PNG)
    colormap      : name of a Bokeh palette (case-sensitive, e.g. "Viridis")
    reverse       : if True, flip the palette direction

    Notes
    -----
    In the fractal algorithms, points that escape immediately return the iteration index i. We map
    points that NEVER escape (grid == max_iterations) to the last palette index. Points that escape
    at i=0 (immediate escape) will map to palette index 0.
    """
    palette = load_bokeh_palette(colormap)
    if reverse:
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
    if fmt == "jpeg":
        img.save(buf, format="JPEG", quality=quality)
    else:
        img.save(buf, format="PNG")
    return buf.getvalue()
