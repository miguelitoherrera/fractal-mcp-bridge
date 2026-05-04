from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path

from fractal_core.config import MAX_ITERATIONS
from utils.image import (
    grid_to_image_bytes, generate_mandelbrot_grid, generate_julia_grid,
    RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX
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
    c_real: float,
    c_imag: float,
) -> bytes:
    """Consolidated logic to compute fractal grid and return JPEG bytes."""
    if fractal_type == MANDELBROT:
        grid = generate_mandelbrot_grid(x_min, x_max, y_min, y_max, resolution, resolution, max_iterations=max_iterations)
    elif fractal_type == JULIA:
        grid = generate_julia_grid(x_min, x_max, y_min, y_max, complex(c_real, c_imag), resolution, resolution, max_iterations=max_iterations)
    else:
        raise ValueError(f"Unsupported fractal type: {fractal_type}")
    return grid_to_image_bytes(grid, max_iterations=max_iterations, fmt="jpeg", quality=95, colormap=colormap, reverse=reverse_colormap)

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
    c_real: float = -0.7,
    c_imag: float = 0.27
):
    img_bytes = generate_image(
        fractal_type, x_min, x_max, y_min, y_max,
        max_iterations, resolution, colormap, reverse_colormap,
        c_real, c_imag
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
    c_real = data.get("c_real", -0.7)
    c_imag = data.get("c_imag", 0.27)
    filename = data.get("filename", "fractal.jpg")

    img_bytes = generate_image(
        fractal_type, x_min, x_max, y_min, y_max,
        max_iterations, resolution, colormap, reverse_colormap,
        c_real, c_imag
    )
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
