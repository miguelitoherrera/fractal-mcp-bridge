# FastMCP server providing fractal generation tools.
"""MCP Bridge Server for Fractal Generation.
This module provides a FastMCP server that exposes fractal generation tools (Mandelbrot and Julia sets) to MCP clients.
"""

import os

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from fractal_mcp.renderer import (
    IMAGES_DIR,
    ensure_images_dir,
    parse_complex,
    render_fractal,
    suggest_filename,
)

# Initialize the MCP server
mcp = FastMCP("FractalBridge")


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
) -> Image:
    """Helper to render, save a fractal image, and structure the tool response."""
    ensure_images_dir()
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

    filename = suggest_filename(
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
    path = IMAGES_DIR / filename
    path.write_bytes(img_bytes)

    return Image(data=img_bytes, format="jpeg")


@mcp.tool
def generate_mandelbrot_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
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
    c: str,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
    """
    Render a Julia set image for a given complex constant c and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        c: The complex constant 'c' as a complex object or string.
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
        c=parse_complex(c),
    )


@mcp.tool
def generate_exponential_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: str,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
    """
    Render an exponential fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        c: The complex constant 'c' as a complex object or string.
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
        c=parse_complex(c),
    )


@mcp.tool
def generate_sine_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: str,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
    """
    Render a sine fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        c: The complex constant 'c' as a complex object or string.
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
        c=parse_complex(c),
    )


@mcp.tool
def generate_cosine_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    c: str,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
    """
    Render a cosine fractal image and save it to a file.

    Args:
        x_min: Minimum real value (horizontal axis).
        x_max: Maximum real value (horizontal axis).
        y_min: Minimum imaginary value (vertical axis).
        y_max: Maximum imaginary value (vertical axis).
        c: The complex constant 'c' as a complex object or string.
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
        c=parse_complex(c),
    )


@mcp.tool
def generate_newton_image(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    power: float,
    resolution: int = 1600,
    max_iterations: int = 200,
    colormap: str = "Turbo",
    reverse_colormap: bool = False,
) -> Image:
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


@mcp.tool
def list_colormaps() -> list[str]:
    """
    List all available colormap (palette) names supported by the fractal renderer.
    """
    from fractal_mcp.renderer import list_colormaps  # noqa: PLC0415

    return list_colormaps()


def main() -> None:
    port_env = os.environ.get("PORT")
    if port_env:
        mcp.run(transport="sse", host="0.0.0.0", port=int(port_env))
    else:
        mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
