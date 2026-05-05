from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from renderer import (
    render_fractal, RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS,
    DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, suggest_filename
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
    julia_c: complex = -0.7 + 0.27j
):
    result = render_fractal(
        fractal_type, x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
        julia_c
    )
    return StreamingResponse(io.BytesIO(result.image_bytes), media_type="image/jpeg")

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
    
    # Strictly expect julia_c
    c = data.get("julia_c", -0.7 + 0.27j)
    if isinstance(c, str):
        c = complex(c.replace(" ", ""))

    filename = data.get("filename")
    if not filename:
        filename = suggest_filename(fractal_type, x_min, x_max, y_min, y_max, colormap, c)

    result = render_fractal(
        fractal_type, x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
        c
    )
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"
        
    (Path("images") / filename).write_bytes(result.image_bytes)
    return {"status": "success", "filename": filename}
