from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from fractal_mcp.app.api.routes import router

app = FastAPI(title="Fractal Explorer")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Get the path to the static directory within the package
STATIC_DIR = Path(__file__).parent / "static"

# Ensure images directory exists in the root
Path("images").mkdir(exist_ok=True)

# Include the explorer API routes
app.include_router(router)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Serve static files (UI)
app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8001)
