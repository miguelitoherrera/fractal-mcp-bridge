from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import io
import os
from fractal_core.mandelbrot import mandelbrot_set
from fractal_core.julia import julia_set
from utils.image import grid_to_image_bytes

app = FastAPI(title="Fractal Interactive Explorer")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

@app.get("/render")
async def render_fractal(
    fractal_type: str = Query("mandelbrot", alias="type", pattern="^(mandelbrot|julia)$"),
    x_min: float = Query(-2.0),
    x_max: float = Query(1.0),
    y_min: float = Query(-1.5),
    y_max: float = Query(1.5),
    max_iterations: int = Query(100),
    resolution: int = Query(800),
    colormap: str = Query("Inferno"),
    reverse_colormap: bool = Query(False),
    c_real: float = Query(-0.7),
    c_imag: float = Query(0.27015),
):
    if fractal_type == "mandelbrot":
        grid = mandelbrot_set(x_min, x_max, y_min, y_max, resolution, resolution, max_iterations)
    else:
        c = complex(c_real, c_imag)
        grid = julia_set(x_min, x_max, y_min, y_max, c, resolution, resolution, max_iterations)

    image_bytes = grid_to_image_bytes(
        grid, max_iterations, fmt="jpeg", quality=95, colormap=colormap, reverse=reverse_colormap
    )
    
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/jpeg")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as f:
        return f.read()

# Mount the static directory to serve other files (styles.css, script.js)
app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
