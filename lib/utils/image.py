import io
from PIL import Image
import numpy as np
from bokeh.palettes import all_palettes, Inferno256


def _hex_to_rgb_array(hex_colors: list[str]) -> np.ndarray:
    """Convert a list of hex strings to an Nx3 uint8 numpy array."""
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
    grid          : 2-D float array from mandelbrot_set()
    max_iterations: the max_iterations value used when computing grid
    fmt           : "jpeg" or "png"
    quality       : JPEG quality (ignored for PNG)
    colormap      : name of a Bokeh palette (case-sensitive, e.g. "Viridis")
    reverse       : if True, flip the palette direction
    """
    palette = load_bokeh_palette(colormap)  # (256, 3) uint8
    if reverse:
        palette = palette[::-1]

    inside = (grid == 0)  # set interior → index 0 (black for most palettes)

    # log1p remap stretches boundary detail into the bright palette range
    safe = np.where(inside, 1, grid)
    t = np.clip(safe / max_iterations, 0.0, 1.0)
    t_smooth = np.log1p(t * 9) / np.log(10)  # 0 → 1, log-compressed

    # Map t_smooth → palette index 1..255  (index 0 reserved for interior)
    idx = np.clip((t_smooth * 254 + 1).astype(np.int32), 1, 255)
    idx[inside] = 0  # force interior to palette[0]

    rgb = palette[idx]  # (H, W, 3)

    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    if fmt == "jpeg":
        img.save(buf, format="JPEG", quality=quality)
    else:
        img.save(buf, format="PNG")
    return buf.getvalue()