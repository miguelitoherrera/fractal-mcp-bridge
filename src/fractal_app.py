from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api.explorer import router as explorer_router

app = FastAPI(title="Fractal Explorer")

# Ensure images directory exists
Path("images").mkdir(exist_ok=True)

# Include the explorer API routes
app.include_router(explorer_router)

@app.get("/")
async def index():
    return FileResponse("static/index.html")

# Serve static files (UI)
app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
