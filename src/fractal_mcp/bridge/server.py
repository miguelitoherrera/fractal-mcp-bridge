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


def _generate_and_save_image(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
    c: complex | None = None,
    power: float | None = None,
) -> dict[str, Any]:
    """Helper to render, save a fractal image, and structure the tool response."""
    img_bytes = render_fractal(
        fractal_type,
        x_min,
        x_max,
        y_min,
        y_max,
        resolution,
        max_iterations,
        colormap,
        reverse_colormap,
        c=c,
        power=power,
    )

    filename = suggest_filename(fractal_type, x_min, x_max, y_min, y_max, colormap, reverse_colormap, c=c, power=power)
    path = Path("images") / filename
    path.write_bytes(img_bytes)

    return {
        "type": "file",
        "path": str(path),
        "mime_type": "image/jpeg",
        "colormap": colormap,
    }


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
    return _generate_and_save_image(
        "mandelbrot",
        x_min,
        x_max,
        y_min,
        y_max,
        resolution,
        max_iterations,
        colormap,
        reverse_colormap,
    )


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
        c: The complex constant 'c' as a complex object.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    return _generate_and_save_image(
        "julia",
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
        c: The complex constant 'c' as a complex object.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    return _generate_and_save_image(
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
    return _generate_and_save_image(
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


@mcp.tool
def generate_cosine_image(
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
    Render a cosine fractal image and save it to a file.

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
    return _generate_and_save_image(
        "cosine",
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


@mcp.tool
def generate_newton_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    power: float,
    resolution: int,
    max_iterations: int,
    colormap: str,
    reverse_colormap: bool,
) -> dict[str, Any]:
    """
    Render a Newton's method fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        power: The exponent 'p' in z^p - 1.
        resolution: Pixel width of the image.
        max_iterations: Maximum iterations.
        colormap: Bokeh colormap name.
        reverse_colormap: If true, reverses the color palette.
    """
    return _generate_and_save_image(
        "newton",
        x_min,
        x_max,
        y_min,
        y_max,
        resolution,
        max_iterations,
        colormap,
        reverse_colormap,
        power=power,
    )


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
