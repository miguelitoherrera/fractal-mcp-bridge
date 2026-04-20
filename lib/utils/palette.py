import numpy as np
from bokeh.palettes import all_palettes, Inferno256


def load_bokeh_palette(name: str) -> np.ndarray:
    """
    Load a named Bokeh palette and return an (256, 3) uint8 RGB array.
    Falls back to Inferno if the name is not found.
    """
    try:
        # Prefer 256-entry version; fall back to largest available
        family = all_palettes.get(name) or all_palettes.get(name.capitalize())
        if family is None:
            raise KeyError(name)
        size = 256 if 256 in family else max(family.keys())
        hex_colors = family[size]
        arr = np.array([[int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]
                        for h in hex_colors], dtype=np.uint8)
        # Resize to exactly 256 entries via linear interpolation if needed
        if len(arr) != 256:
            indices = np.linspace(0, len(arr) - 1, 256)
            arr = np.stack([
                np.interp(indices, np.arange(len(arr)), arr[:, c]).astype(np.uint8)
                for c in range(3)
            ], axis=1)
        return arr
    except Exception:
        # Hardcoded Inferno-256 fallback (first/last few entries shown for brevity)
        arr = np.array([[int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]
                        for h in Inferno256], dtype=np.uint8)
        return arr
