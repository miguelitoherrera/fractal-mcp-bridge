# FastAPI router for fractal exploration and image streaming.
import io
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator, model_validator

from fractal_mcp.renderer import (
    IMAGES_DIR,
    render_fractal,
    suggest_filename,
    validate_fractal_params,
)
from fractal_mcp.renderer import (
    list_colormaps as list_renderer_colormaps,
)

router = APIRouter()


def parse_complex(v: str | complex) -> complex:
    """
    Strictly parse complex numbers from strings or return the complex object.
    Used for web frontend input which may contain spaces.
    """
    if isinstance(v, complex):
        return v
    # Remove spaces and ensure it can be parsed by complex()
    return complex(str(v).replace(" ", ""))


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
    c: complex | None = None
    power: float | None = None

    @field_validator("c", mode="before")
    @classmethod
    def parse_complex_field(cls, v: Any) -> complex | None:
        return parse_complex(v) if v is not None else None

    @model_validator(mode="after")
    def validate_params(self) -> FractalParams:
        validate_fractal_params(
            self.fractal_type,
            self.c,
            self.power,
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            self.resolution,
            self.max_iterations,
            colormap=self.colormap,
        )
        return self


class SaveRequest(FractalParams):
    filename: str


# Simple one-item cache for the last rendered image to avoid redundant calculations
class LastRenderCache:
    def __init__(self) -> None:
        self.params: dict[str, Any] | None = None
        self.image_bytes: bytes | None = None

    def matches(self, params: FractalParams) -> bool:
        if self.params is None:
            return False
        return bool(self.params == params.model_dump(exclude={"filename"}))

    def update(self, params: FractalParams, image_bytes: bytes) -> None:
        self.params = params.model_dump(exclude={"filename"})
        self.image_bytes = image_bytes


_render_cache = LastRenderCache()


def clear_render_cache() -> None:
    """Clear the last rendered image cache (used primarily for test isolation)."""
    _render_cache.params = None
    _render_cache.image_bytes = None


@router.get("/render")
def render(params: FractalParams = Depends()) -> StreamingResponse:
    # Check cache first
    if _render_cache.matches(params):
        img_bytes = _render_cache.image_bytes
    else:
        img_bytes = render_fractal(
            params.fractal_type,
            params.x_min,
            params.x_max,
            params.y_min,
            params.y_max,
            params.resolution,
            params.max_iterations,
            params.colormap,
            params.reverse_colormap,
            c=params.c,
            power=params.power,
        )
        _render_cache.update(params, img_bytes)

    assert img_bytes is not None

    # Suggest a filename to be sent as a header for UI synchronization
    filename = suggest_filename(
        params.fractal_type,
        params.x_min,
        params.x_max,
        params.y_min,
        params.y_max,
        params.resolution,
        params.max_iterations,
        params.colormap,
        params.reverse_colormap,
        c=params.c,
        power=params.power,
    )

    return StreamingResponse(
        io.BytesIO(img_bytes),
        media_type="image/jpeg",
        headers={"X-Suggested-Filename": filename, "Access-Control-Expose-Headers": "X-Suggested-Filename"},
    )


@router.get("/suggest-filename")
async def get_suggested_filename(params: FractalParams = Depends()) -> dict[str, str]:
    filename = suggest_filename(
        params.fractal_type,
        params.x_min,
        params.x_max,
        params.y_min,
        params.y_max,
        params.resolution,
        params.max_iterations,
        params.colormap,
        params.reverse_colormap,
        c=params.c,
        power=params.power,
    )
    return {"filename": filename}


@router.get("/colormaps")
def list_colormaps() -> list[str]:
    """List all available colormap names."""
    return list_renderer_colormaps()


@router.post("/save")
def save(req: SaveRequest) -> dict[str, str]:
    filename = Path(req.filename).name
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"

    # Sanity check: Can we use the cached image?
    if _render_cache.matches(req):
        img_bytes = _render_cache.image_bytes
    else:
        img_bytes = render_fractal(
            req.fractal_type,
            req.x_min,
            req.x_max,
            req.y_min,
            req.y_max,
            req.resolution,
            req.max_iterations,
            req.colormap,
            req.reverse_colormap,
            c=req.c,
            power=req.power,
        )
        # Update cache with the new render
        _render_cache.update(req, img_bytes)

    assert img_bytes is not None
    (IMAGES_DIR / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename, "path": str(IMAGES_DIR / filename)}
