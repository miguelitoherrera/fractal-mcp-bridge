from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from pydantic import BaseModel, field_validator
from fractal_mcp.renderer import render_fractal, suggest_filename, parse_complex


router = APIRouter()


class FractalParams(BaseModel):
    fractal_type: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    max_iterations: int
    resolution: int
    colormap: str
    reverse_colormap: bool
    julia_c: complex | None = None

    @field_validator('julia_c', mode='before')
    @classmethod
    def parse_complex_field(cls, v):
        return parse_complex(v) if v is not None else None

class SaveRequest(FractalParams):
    filename: str | None = None

# Simple one-item cache for the last rendered image to avoid redundant calculations
class LastRenderCache:
    def __init__(self):
        self.params = None
        self.image_bytes = None

    def _extract_params(self, p: FractalParams) -> dict:
        """Internal helper to get rendering params from model."""
        return p.model_dump(exclude={'filename'})

    def matches(self, params: FractalParams) -> bool:
        if self.params is None:
            return False
        return self.params == self._extract_params(params)

    def update(self, params: FractalParams, image_bytes: bytes):
        self.params = self._extract_params(params)
        self.image_bytes = image_bytes

_render_cache = LastRenderCache()

@router.get("/render")
async def render(params: FractalParams = Depends()):
    # Check cache first
    if _render_cache.matches(params):
        img_bytes = _render_cache.image_bytes
    else:
        img_bytes = render_fractal(
            params.fractal_type, params.x_min, params.x_max, params.y_min, params.y_max,
            params.resolution, params.max_iterations, params.colormap, params.reverse_colormap,
            julia_c=params.julia_c
        )
        _render_cache.update(params, img_bytes)

    # Suggest a filename to be sent as a header for UI synchronization
    filename = suggest_filename(
        params.fractal_type, params.x_min, params.x_max, params.y_min, params.y_max, 
        params.colormap, params.reverse_colormap, julia_c=params.julia_c
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
async def get_suggested_filename(params: FractalParams = Depends()):
    filename = suggest_filename(
        params.fractal_type, params.x_min, params.x_max, params.y_min, params.y_max, 
        params.colormap, params.reverse_colormap, julia_c=params.julia_c
    )
    return {"filename": filename}


@router.post("/save")
async def save(req: SaveRequest):
    filename = req.filename
    if not filename:
        filename = suggest_filename(
            req.fractal_type, req.x_min, req.x_max, req.y_min, req.y_max,
            req.colormap, req.reverse_colormap, julia_c=req.julia_c
        )
    
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"

    # Sanity check: Can we use the cached image?
    if _render_cache.matches(req):
        img_bytes = _render_cache.image_bytes
    else:
        img_bytes = render_fractal(
            req.fractal_type, req.x_min, req.x_max, req.y_min, req.y_max,
            req.resolution, req.max_iterations, req.colormap, req.reverse_colormap,
            julia_c=req.julia_c
        )
        # Update cache with the new render
        _render_cache.update(req, img_bytes)
        
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
