from fastmcp import FastMCP
import numpy as np
import base64
from utils.image import (
    grid_to_image_bytes, generate_mandelbrot_grid, generate_julia_grid, RESOLUTION
)
from fractal_core.config import MAX_ITERATIONS


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
    """Render a Mandelbrot set image."""
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, width, height, max_iterations=max_iterations)

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
    """Generates a Julia set for a given complex constant c."""
    c = complex(c_real, c_imag)
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    grid = generate_julia_grid(x_min, x_max, y_min, y_max, c, width, height, max_iterations=max_iterations)

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
