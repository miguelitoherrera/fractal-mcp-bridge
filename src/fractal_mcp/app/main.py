from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fractal_mcp.app.api.routes import router

app = FastAPI(title="Fractal Explorer")

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
