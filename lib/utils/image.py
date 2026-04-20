import io
from PIL import Image
import numpy as np
from utils.palette import load_bokeh_palette


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