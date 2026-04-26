from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import io
from pathlib import Path
from fractal_core.mandelbrot import mandelbrot_set
from fractal_core.julia import julia_set
from utils.image import grid_to_image_bytes

app = FastAPI(title="Fractal Explorer")
Path("images").mkdir(exist_ok=True)

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

@app.get("/render")
async def render(
    fractal_type: str = Query("mandelbrot", pattern="^(mandelbrot|julia)$"),
    x_min: float = -2.0,
    x_max: float = 1.0,
    y_min: float = -1.5,
    y_max: float = 1.5,
    max_iterations: int = 100,
    resolution: int = 800,
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

@app.post("/save")
async def save(p: FractalParams):
    img_bytes = generate_image(p)
    filename = p.filename if p.filename.lower().endswith((".jpg", ".jpeg")) else f"{p.filename}.jpg"
    (Path("images") / filename).write_bytes(img_bytes)
    return {"status": "success", "filename": filename}

@app.get("/")
async def index():
    return FileResponse("static/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
