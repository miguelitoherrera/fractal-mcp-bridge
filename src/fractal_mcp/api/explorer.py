from fastapi import APIRouter, Query, Body
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from pydantic import BaseModel, field_validator
from fractal_mcp.renderer import (
    render_fractal, suggest_filename, parse_complex,
    RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS,
    DEFAULT_COLORMAP, DEFAULT_REVERSE_COLORMAP, DEFAULT_JULIA_C
)


router = APIRouter()

MANDELBROT = "mandelbrot"
JULIA = "julia"

# Simple one-item cache for the last rendered image to avoid redundant calculations
class LastRenderCache:
    def __init__(self):
        self.params = None
        self.image_bytes = None

    def matches(self, **kwargs) -> bool:
        if self.params is None:
            return False
        return all(kwargs.get(k) == v for k, v in self.params.items())

    def update(self, params: dict, image_bytes: bytes):
        self.params = params
        self.image_bytes = image_bytes

_render_cache = LastRenderCache()

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
    def parse_complex_field(cls, v):
        if v is None:
            return None
        try:
            return parse_complex(v)
        except ValueError:
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
    
    # Collect current parameters for cache checking
    current_params = {
        "fractal_type": fractal_type,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "max_iterations": max_iterations,
        "resolution": resolution,
        "colormap": colormap,
        "reverse_colormap": reverse_colormap,
        "julia_c": julia_c
    }

    # Check cache first
    if _render_cache.matches(**current_params):
        print("DEBUG: Using cached image bytes for /render")
        img_bytes = _render_cache.image_bytes
    else:
        img_bytes = render_fractal(
            fractal_type, x_min, x_max, y_min, y_max,
            resolution, max_iterations, colormap, reverse_colormap,
            julia_c
        )
        _render_cache.update(current_params, img_bytes)

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

    # Sanity check: Can we use the cached image?
    save_params = {
        "fractal_type": req.fractal_type,
        "x_min": req.x_min,
        "x_max": req.x_max,
        "y_min": req.y_min,
        "y_max": req.y_max,
        "max_iterations": req.max_iterations,
        "resolution": req.resolution,
        "colormap": req.colormap,
        "reverse_colormap": req.reverse_colormap,
        "julia_c": c
    }

    if _render_cache.matches(**save_params):
        print(f"DEBUG: /save using cached image bytes for {filename}")
        img_bytes = _render_cache.image_bytes
    else:
        print(f"DEBUG: /save cache miss - re-rendering {filename}")
        img_bytes = render_fractal(
            req.fractal_type, req.x_min, req.x_max, req.y_min, req.y_max,
            req.resolution, req.max_iterations, req.colormap, req.reverse_colormap,
            c
        )
        # Update cache with the new render
        _render_cache.update(save_params, img_bytes)
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
