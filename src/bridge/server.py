"""MCP Bridge Server for Fractal Generation.
This module provides a FastMCP server that exposes fractal generation tools (Mandelbrot and Julia sets) to MCP clients.
"""

from fastmcp import FastMCP
import numpy as np
import base64
from utils.image import (
    grid_to_image_bytes, generate_mandelbrot_grid, generate_julia_grid,
    RESOLUTION, MAX_ITERATIONS
)


# Initialize the MCP server
mcp = FastMCP("FractalBridge")

def _generate_fractal_response(
    grid: np.ndarray,
    fmt: str,
    quality: int,
    colormap: str,
    reverse_colormap: bool,
    filename_prefix: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    max_iterations: int
) -> dict:
    """
    Internal helper to convert a fractal grid into a standardized MCP response.

    Args:
        grid: 2D numpy array of escape iteration values.
        fmt: Image format ("jpeg" or "png").
        quality: JPEG quality (1-95).
        colormap: Name of the Bokeh palette to use.
        reverse_colormap: Whether to reverse the colormap.
        filename_prefix: Prefix for the generated filename (e.g., "mandelbrot").
        x_min, x_max, y_min, y_max: The viewport coordinates.
        max_iterations: The iteration limit used for calculation.

    Returns:
        A dictionary formatted for MCP client consumption, containing base64 image data
        and metadata.
    """
    img_bytes = grid_to_image_bytes(
        grid, max_iterations, fmt, quality, colormap, reverse_colormap
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

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        resolution: Pixel width of the image (height is calculated via aspect ratio).
        max_iterations: Maximum iterations before a point is considered part of the set.
        img_format: Output format, "jpeg" or "png".
        quality: JPEG compression quality (1-95).
        colormap: Bokeh colormap name (e.g., "Inferno", "Viridis", "Turbo").
        reverse_colormap: If true, reverses the color palette.
    """
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, width, height, max_iterations)

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
        julia_c: complex = -0.7 + 0.27j,
        resolution: int = RESOLUTION,
        max_iterations: int = MAX_ITERATIONS,
        img_format: str = "jpeg",
        quality: int = 95,
        colormap: str = "Inferno",
        reverse_colormap: bool = False,
):
    """
    Render a Julia set image for a given complex constant c.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        julia_c: The complex constant 'c' (e.g., -0.7+0.27j).
        resolution: Pixel width of the image (height is calculated via aspect ratio).
        max_iterations: Maximum iterations before a point is considered part of the set.
        img_format: Output format, "jpeg" or "png".
        quality: JPEG compression quality (1-95).
        colormap: Bokeh colormap name (e.g., "Inferno", "Viridis", "Turbo").
        reverse_colormap: If true, reverses the color palette.
    """
    width = resolution
    height = round(width * (y_max - y_min) / (x_max - x_min))
    grid = generate_julia_grid(x_min, x_max, y_min, y_max, julia_c, width, height, max_iterations)

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
