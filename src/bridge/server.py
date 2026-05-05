"""MCP Bridge Server for Fractal Generation.
This module provides a FastMCP server that exposes fractal generation tools (Mandelbrot and Julia sets) to MCP clients.
"""

from fastmcp import FastMCP
import base64
from renderer import (
    render_fractal, suggest_filename,
    RESOLUTION, MAX_ITERATIONS, DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, DEFAULT_JULIA_C
)


# Initialize the MCP server
mcp = FastMCP("FractalBridge")

@mcp.tool
def generate_mandelbrot_image(
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        resolution: int = RESOLUTION,
        max_iterations: int = MAX_ITERATIONS,
        colormap: str = DEFAULT_COLORMAP,
        reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP,
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
        colormap: Bokeh colormap name (e.g., "Inferno", "Viridis", "Turbo").
        reverse_colormap: If true, reverses the color palette.
    """
    result = render_fractal(
        "mandelbrot", x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap
    )
    return {
        "type": "file",
        "filename": suggest_filename("mandelbrot", x_min, x_max, y_min, y_max, colormap),
        "mime_type": "image/jpeg",
        "data": base64.b64encode(result.image_bytes).decode("utf-8"),
        "mean_escape": result.mean_escape,
        "shape": list(result.grid_shape),
        "colormap": colormap,
    }


@mcp.tool
def generate_julia_image(
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        julia_c: complex = DEFAULT_JULIA_C,
        resolution: int = RESOLUTION,
        max_iterations: int = MAX_ITERATIONS,
        colormap: str = DEFAULT_COLORMAP,
        reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP,
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
        colormap: Bokeh colormap name (e.g., "Inferno", "Viridis", "Turbo").
        reverse_colormap: If true, reverses the color palette.
    """
    result = render_fractal(
        "julia", x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
        julia_c=julia_c
    )
    return {
        "type": "file",
        "filename": suggest_filename("julia", x_min, x_max, y_min, y_max, colormap, julia_c),
        "mime_type": "image/jpeg",
        "data": base64.b64encode(result.image_bytes).decode("utf-8"),
        "mean_escape": result.mean_escape,
        "shape": list(result.grid_shape),
        "colormap": colormap,
    }


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
