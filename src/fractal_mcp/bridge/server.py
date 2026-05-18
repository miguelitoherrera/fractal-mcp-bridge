# FastMCP server providing fractal generation tools.
"""MCP Bridge Server for Fractal Generation.
This module provides a FastMCP server that exposes fractal generation tools (Mandelbrot and Julia sets) to MCP clients.
"""

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from fractal_mcp.renderer import render_fractal, suggest_filename

# Initialize the MCP server
mcp = FastMCP("FractalBridge")

# Ensure images directory exists
Path("images").mkdir(exist_ok=True)


@mcp.tool
def generate_mandelbrot_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> dict[str, Any]:
    """
    Render a Mandelbrot set image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    img_bytes = render_fractal(
        "mandelbrot", x_min, x_max, y_min, y_max, resolution, max_iterations, colormap, reverse_colormap
    )

    filename = suggest_filename("mandelbrot", x_min, x_max, y_min, y_max, colormap, reverse_colormap)
    (Path("images") / filename).write_bytes(img_bytes)

    return {
        "type": "file",
        "path": str(Path("images") / filename),
        "mime_type": "image/jpeg",
        "colormap": colormap,
    }


@mcp.tool
def generate_julia_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> dict[str, Any]:
    """
    Render a Julia set image for a given complex constant c and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        julia_c: The complex constant 'c' as a complex object.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    img_bytes = render_fractal(
        "julia", x_min, x_max, y_min, y_max, resolution, max_iterations, colormap, reverse_colormap, c=c
    )

    filename = suggest_filename("julia", x_min, x_max, y_min, y_max, colormap, reverse_colormap, c=c)
    (Path("images") / filename).write_bytes(img_bytes)

    return {
        "type": "file",
        "path": str(Path("images") / filename),
        "mime_type": "image/jpeg",
        "colormap": colormap,
    }


@mcp.tool
def generate_exponential_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> dict[str, Any]:
    """
    Render an exponential fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        julia_c: The complex constant 'c' as a complex object.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    img_bytes = render_fractal(
        "exponential",
        x_min,
        x_max,
        y_min,
        y_max,
        resolution,
        max_iterations,
        colormap,
        reverse_colormap,
        c=c,
    )

    filename = suggest_filename("exponential", x_min, x_max, y_min, y_max, colormap, reverse_colormap, c=c)
    (Path("images") / filename).write_bytes(img_bytes)

    return {
        "type": "file",
        "path": str(Path("images") / filename),
        "mime_type": "image/jpeg",
        "colormap": colormap,
    }


@mcp.tool
def generate_sine_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: complex,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> dict[str, Any]:
    """
    Render a sine fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        c: The complex constant 'c' as a complex object.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    img_bytes = render_fractal(
        "sine",
        x_min,
        x_max,
        y_min,
        y_max,
        resolution,
        max_iterations,
        colormap,
        reverse_colormap,
        c=c,
    )

    filename = suggest_filename("sine", x_min, x_max, y_min, y_max, colormap, reverse_colormap, c=c)
    (Path("images") / filename).write_bytes(img_bytes)

    return {
        "type": "file",
        "path": str(Path("images") / filename),
        "mime_type": "image/jpeg",
        "colormap": colormap,
    }


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
