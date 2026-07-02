from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fractal_mcp.app.api.routes import router
from fractal_mcp.renderer import ensure_images_dir


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ensure_images_dir()
    yield


app = FastAPI(title="Fractal Explorer", lifespan=lifespan)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Get the path to the static directory within the package
STATIC_DIR = Path(__file__).parent / "static"

# Include the explorer API routes
app.include_router(router)


# Serve static files (UI)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":  # pragma: no cover
    main()
