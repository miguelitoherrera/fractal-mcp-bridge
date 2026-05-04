from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path

from utils.image import (
    grid_to_image_bytes, generate_mandelbrot_grid, generate_julia_grid,
    RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS
)

router = APIRouter()

MANDELBROT = "mandelbrot"
JULIA = "julia"

def generate_image(
    fractal_type: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    max_iterations: int,
    resolution: int,
    colormap: str,
    reverse_colormap: bool,
    julia_c: complex,
) -> bytes:
    """
    Consolidated logic to compute a fractal grid and return its JPEG representation.

    Args:
        fractal_type: The type of fractal to render ("mandelbrot" or "julia").
        x_min, x_max: Bounds for the real axis.
        y_min, y_max: Bounds for the imaginary axis.
        max_iterations: The escape threshold for calculation.
        resolution: Pixel width/height for the output grid.
        colormap: Name of the Bokeh palette to apply.
        reverse_colormap: Whether to flip the color palette.
        julia_c: The complex constant 'c' used only for Julia set calculation.

    Returns:
        bytes: The rendered JPEG image data.

    Raises:
        ValueError: If the fractal_type is unsupported.
    """
    if fractal_type == MANDELBROT:
        grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, resolution, resolution, max_iterations)
    elif fractal_type == JULIA:
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, julia_c, resolution, resolution, max_iterations)
    else:
        raise ValueError(f"Unsupported fractal type: {fractal_type}")
    return grid_to_image_bytes(grid, max_iterations, "jpeg", 95, colormap, reverse_colormap)

@router.get("/render")
async def render(
    fractal_type: str = Query(MANDELBROT, pattern=f"^({MANDELBROT}|{JULIA})$"),
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    y_min: float = Y_MIN,
    y_max: float = Y_MAX,
    max_iterations: int = MAX_ITERATIONS,
    resolution: int = RESOLUTION,
    colormap: str = "Inferno",
    reverse_colormap: bool = False,
    julia_c: complex = -0.7 + 0.27j
):
    img_bytes = generate_image(
        fractal_type, x_min, x_max, y_min, y_max,
        max_iterations, resolution, colormap, reverse_colormap,
        julia_c
    )
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

@router.post("/save")
async def save(data: dict = Body(...)):
    # Extract with defaults if missing
    fractal_type = data.get("fractal_type", MANDELBROT)
    x_min = data.get("x_min", X_MIN)
    x_max = data.get("x_max", X_MAX)
    y_min = data.get("y_min", Y_MIN)
    y_max = data.get("y_max", Y_MAX)
    max_iterations = data.get("max_iterations", MAX_ITERATIONS)
    resolution = data.get("resolution", RESOLUTION)
    colormap = data.get("colormap", "Inferno")
    reverse_colormap = data.get("reverse_colormap", False)
    
    # Strictly expect julia_c
    c = data.get("julia_c", -0.7 + 0.27j)
    if isinstance(c, str):
        c = complex(c.replace(" ", ""))

    filename = data.get("filename", "fractal.jpg")

    img_bytes = generate_image(
        fractal_type, x_min, x_max, y_min, y_max,
        max_iterations, resolution, colormap, reverse_colormap,
        c
    )
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
