from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from pathlib import Path

from fractal_core.mandelbrot import mandelbrot_set
from fractal_core.julia import julia_set
from fractal_core.config import MAX_ITERATIONS, RESOLUTION, X_MIN, X_MAX, Y_MIN, Y_MAX
from utils.image import grid_to_image_bytes

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
    c_real: float
    c_imag: float
    filename: str = ""

def generate_image(p: FractalParams) -> bytes:
    """Consolidated logic to compute fractal grid and return JPEG bytes."""
    if p.fractal_type == "mandelbrot":
        grid = mandelbrot_set(p.x_min, p.x_max, p.y_min, p.y_max, p.resolution, p.resolution, p.max_iterations)
    else:
        grid = julia_set(p.x_min, p.x_max, p.y_min, p.y_max, complex(p.c_real, p.c_imag), p.resolution, p.resolution, p.max_iterations)
    return grid_to_image_bytes(grid, p.max_iterations, fmt="jpeg", quality=95, colormap=p.colormap, reverse=p.reverse_colormap)

@router.get("/render")
async def render(
    fractal_type: str = Query("mandelbrot", pattern="^(mandelbrot|julia)$"),
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
    p = FractalParams(
        fractal_type=fractal_type,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        max_iterations=max_iterations,
        resolution=resolution,
        colormap=colormap,
        reverse_colormap=reverse_colormap,
        c_real=c_real,
        c_imag=c_imag
    )
    return StreamingResponse(io.BytesIO(generate_image(p)), media_type="image/jpeg")

@router.post("/save")
async def save(p: FractalParams):
    img_bytes = generate_image(p)
    filename = p.filename if p.filename.lower().endswith((".jpg", ".jpeg")) else f"{p.filename}.jpg"
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}
