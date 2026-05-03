from fastmcp import FastMCP
import numpy as np
import base64
from utils.image import grid_to_image_bytes
from fractal_core.mandelbrot import mandelbrot_set
from fractal_core.julia import julia_set
from fractal_core.config import MAX_ITERATIONS, RESOLUTION


# Initialize the MCP server
mcp = FastMCP("FractalBridge")

def _generate_fractal_response(grid, fmt, quality, colormap, reverse_colormap, filename_prefix, x_min, x_max, y_min, y_max, max_iterations):
    img_bytes = grid_to_image_bytes(
        grid,
        max_iterations=max_iterations,
        fmt=fmt,
        quality=quality,
        colormap=colormap,
        reverse=reverse_colormap,
    )

    ext = "jpg" if fmt == "jpeg" else "png"
    return {
        "type": "file",
        "filename": f"{filename_prefix}_{x_min}_{x_max}_{y_min}_{y_max}_{colormap}.{ext}",
        "mime_type": "image/jpeg" if fmt == "jpeg" else "image/png",
        "data": base64.b64encode(img_bytes).decode("utf-8"),
        "mean_escape": round(float(np.mean(grid)), 2),
        "shape": list(grid.shape),
        "colormap": colormap,
    }


@mcp.tool
def generate_mandelbrot_image(
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        resolution: int = RESOLUTION,
        max_iterations: int = MAX_ITERATIONS,
        img_format: str = "jpeg",
        quality: int = 95,
        colormap: str = "Inferno",
        reverse_colormap: bool = False,
):
    """
    Render a Mandelbrot set image.

    Parameters
    ----------
    x_min, x_max  : real-axis window
    y_min, y_max  : imaginary-axis window
    resolution    : pixel width (height computed from aspect ratio)
    max_iterations: escape threshold
    img_format    : "jpeg" or "png"
    quality       : JPEG quality 1-95
    colormap      : Bokeh palette name, e.g. "Viridis", "Inferno", "Plasma",
                    "Magma", "Turbo", "Cividis", "Spectral", "RdYlBu", ...
    reverse_colormap : flip the palette direction
    """
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    grid = mandelbrot_set(x_min, x_max, y_min, y_max, width, height, max_iterations=max_iterations)

    return _generate_fractal_response(
        grid=grid,
        fmt=img_format,
        quality=quality,
        colormap=colormap,
        reverse_colormap=reverse_colormap,
        filename_prefix="mandelbrot",
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        max_iterations=max_iterations
    )


@mcp.tool
def generate_julia_image(
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        c_real: float,
        c_imag: float,
        resolution: int = RESOLUTION,
        max_iterations: int = MAX_ITERATIONS,
        img_format: str = "jpeg",
        quality: int = 95,
        colormap: str = "Inferno",
        reverse_colormap: bool = False,
):
    """
    Generates a Julia set for a given complex constant c.
    """
    c = complex(c_real, c_imag)
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))

    # Calls the imported function directly from the virtual link
    grid = julia_set(x_min, x_max, y_min, y_max, c, width, height, max_iterations=max_iterations)

    return _generate_fractal_response(
        grid=grid,
        fmt=img_format,
        quality=quality,
        colormap=colormap,
        reverse_colormap=reverse_colormap,
        filename_prefix="julia",
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        max_iterations=max_iterations
    )


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
