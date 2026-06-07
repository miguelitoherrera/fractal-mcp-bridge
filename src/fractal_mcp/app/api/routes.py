# FastAPI router for fractal exploration and image streaming.
import io
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator, model_validator

from fractal_mcp.renderer import (
    IMAGES_DIR,
    ensure_images_dir,
    parse_complex,
    render_fractal,
    suggest_filename,
    validate_fractal_params,
)
from fractal_mcp.renderer import list_colormaps as list_renderer_colormaps

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
        self._cache: tuple[dict[str, Any], bytes] | None = None

    def get(self, params: FractalParams) -> bytes | None:
        """Atomic read check. Returns cached bytes if they match params, else None."""
        cache = self._cache
        if cache is None:
            return None
        stored_params, img_bytes = cache
        if stored_params == params.model_dump(exclude={"filename"}):
            return img_bytes
        return None

    def update(self, params: FractalParams, image_bytes: bytes) -> None:
        self._cache = (params.model_dump(exclude={"filename"}), image_bytes)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache = None


_render_cache = LastRenderCache()


def clear_render_cache() -> None:
    """Clear the last rendered image cache (used primarily for test isolation)."""
    _render_cache.clear()


@router.get("/render")
def render(params: FractalParams = Depends()) -> StreamingResponse:
    # Check cache first
    img_bytes = _render_cache.get(params)
    if img_bytes is None:
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
def get_suggested_filename(params: FractalParams = Depends()) -> dict[str, str]:
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
    stripped = req.filename.strip()
    filename = Path(stripped).name
    if not filename or filename in (".", ".."):
        raise ValueError("Invalid filename")
    if not filename.lower().endswith((".jpg", ".jpeg")):
        filename += ".jpg"

    # Sanity check: Can we use the cached image?
    img_bytes = _render_cache.get(req)
    if img_bytes is None:
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
    ensure_images_dir()
    (IMAGES_DIR / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename, "path": str(IMAGES_DIR / filename)}
