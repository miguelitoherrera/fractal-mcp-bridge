from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from fractal_mcp.renderer import (
    render_fractal, suggest_filename,
    RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS,
    DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, DEFAULT_JULIA_C
)


router = APIRouter()

MANDELBROT = "mandelbrot"
JULIA = "julia"

@router.get("/render")
async def render(
    fractal_type: str = Query(MANDELBROT, pattern=f"^({MANDELBROT}|{JULIA})$"),
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    y_min: float = Y_MIN,
    y_max: float = Y_MAX,
    max_iterations: int = MAX_ITERATIONS,
    resolution: int = RESOLUTION,
    colormap: str = DEFAULT_COLORMAP,
    reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP,
    julia_c: complex | None = None
):
    img_bytes = render_fractal(
        fractal_type, x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
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
    colormap = data.get("colormap", DEFAULT_COLORMAP)
    reverse_colormap = data.get("reverse_colormap", DEFAULT_REVERSE_COLORMAP)
    
    # Strictly expect julia_c only if fractal_type is julia
    c = data.get("julia_c")
    if isinstance(c, str):
        c = complex(c.replace(" ", ""))
    
    if c is None and fractal_type == JULIA:
        c = DEFAULT_JULIA_C

    filename = data.get("filename")
    if not filename:
        filename = suggest_filename(fractal_type, x_min, x_max, y_min, y_max, colormap, c)
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"

    img_bytes = render_fractal(
        fractal_type, x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
        c
    )
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
