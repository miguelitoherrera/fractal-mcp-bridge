from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from pydantic import BaseModel, field_validator
from fractal_mcp.renderer import (
    render_fractal, suggest_filename,
    RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS,
    DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, DEFAULT_JULIA_C
)


router = APIRouter()

MANDELBROT = "mandelbrot"
JULIA = "julia"

class SaveRequest(BaseModel):
    fractal_type: str = MANDELBROT
    x_min: float = X_MIN
    x_max: float = X_MAX
    y_min: float = Y_MIN
    y_max: float = Y_MAX
    max_iterations: int = MAX_ITERATIONS
    resolution: int = RESOLUTION
    colormap: str = DEFAULT_COLORMAP
    reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP
    julia_c: complex | None = None
    filename: str | None = None

    @field_validator('julia_c', mode='before')
    @classmethod
    def parse_complex(cls, v):
        try:
            return complex(v.replace(" ", ""))
        except (ValueError, AttributeError, TypeError):
            return None

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
    print(f"DEBUG: /render {fractal_type} rev={reverse_colormap} cmap={colormap}")
    img_bytes = render_fractal(
        fractal_type, x_min, x_max, y_min, y_max,
        resolution, max_iterations, colormap, reverse_colormap,
        julia_c
    )

    # Suggest a filename to be sent as a header for UI synchronization
    filename = suggest_filename(
        fractal_type, x_min, x_max, y_min, y_max, colormap, reverse_colormap, julia_c
    )

    return StreamingResponse(
        io.BytesIO(img_bytes),
        media_type="image/jpeg",
        headers={
            "X-Suggested-Filename": filename,
            "Access-Control-Expose-Headers": "X-Suggested-Filename"
        }
    )

@router.get("/suggest-filename")
async def get_suggested_filename(
    fractal_type: str = MANDELBROT,
    x_min: float = X_MIN,
    x_max: float = X_MAX,
    y_min: float = Y_MIN,
    y_max: float = Y_MAX,
    colormap: str = DEFAULT_COLORMAP,
    reverse_colormap: bool = DEFAULT_REVERSE_COLORMAP,
    julia_c: complex | None = None
):
    print(f"DEBUG: /suggest-filename rev={reverse_colormap} julia_c={julia_c}")
    filename = suggest_filename(fractal_type, x_min, x_max, y_min, y_max, colormap, reverse_colormap, julia_c)
    return {"filename": filename}


@router.post("/save")
async def save(req: SaveRequest):
    # Use provided julia_c or fallback for Julia fractal type
    c = req.julia_c
    if req.fractal_type == JULIA and c is None:
        c = DEFAULT_JULIA_C

    filename = req.filename
    if not filename:
        filename = suggest_filename(
            req.fractal_type, req.x_min, req.x_max, req.y_min, req.y_max,
            req.colormap, req.reverse_colormap, c
        )
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"

    img_bytes = render_fractal(
        req.fractal_type, req.x_min, req.x_max, req.y_min, req.y_max,
        req.resolution, req.max_iterations, req.colormap, req.reverse_colormap,
        c
    )
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
