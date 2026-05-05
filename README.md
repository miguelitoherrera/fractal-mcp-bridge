# Fractal MCP Bridge
**An MCP server for scaling fractal computations and rendering images.**

This repository serves as an AI agent backend, connecting the Model Context Protocol (MCP) to a high-performance
Python library for Mandelbrot and Julia sets.

## 🏗 Project Architecture
The repository follows a strict three-tier architecture to maintain clear separation between core mathematical logic, image processing, and service orchestration:

- **1. Math Layer (`lib/fractal_core`)**: 
  - `mandelbrot.py` & `julia.py`: Pure, Numba-accelerated mathematical functions for calculating fractal escape grids. This layer is strictly computational and has no knowledge of image formats or resolutions.
- **2. Imaging Layer (`lib/utils/image.py`)**: 
  - Specialized logic for converting numerical escape grids into colorful images. It handles colormap application (using Bokeh palettes) and logarithmic scaling. Hardcoded to produce high-quality JPEG output.
- **3. Orchestration Layer (`lib/renderer.py`)**: 
  - The unified "brain" of the library. It manages coordinate defaults, calculates aspect ratios to prevent image stretching, and orchestrates the flow between the Math and Imaging layers. It returns a standardized `FractalResult` dataclass.

### Service Layer
- **FastAPI Bridge (`src/api/explorer.py`)**: A dedicated router for the web explorer backend, providing `/render` and `/save` endpoints.
- **MCP Bridge (`src/bridge/server.py`)**: FastMCP server implementation that exposes the library as tools for AI agents.
- **Application Assembler (`src/fractal_app.py`)**: Plugs in the API routes and mounts the static UI.

## 🚀 Local Setup & Development
To ensure the environment correctly resolves the internal package mappings, you must perform an editable installation.

### 1. Prerequisites
- **Python 3.14.1**
- **Node.js / npx** (required for the MCP Inspector)

### 2. Installation
From the repository root, run:
```bash
pip install -r requirements.txt
```

From the repository root, run the following command, which uses the `pyproject.toml` to map the internal modules to your Python environment.
```bash
pip install -e .
```

### 3. Smoke Testing
You can manually verify the bridge and Numba-accelerated logic using the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector /absolute/path/to/python src/bridge/server.py
```
Open the browser link provided by the inspector to test the `generate_mandelbrot` and `generate_julia` tools.

### 4. Unit Tests
You can use this convenient executable to run unit tests with coverage. From the repository root, run:
```bash
bin/run-tests
```

## Fractal Web Explorer
If you want to interactively explore the Mandelbrot and Julia sets in more detail, you can also spin up the
Fractal Web Explorer. From the repository root, run:
```bash
bin/run-fractal-app
```
Open the browser link provided in the terminal.

## 🤖 Claude Desktop Integration
To use this bridge as an AI Agent, update your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fractal-bridge": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/fractal-mcp-bridge/src/bridge/server.py"
      ]
    }
  }
}
```
Take special care to align the python path with this repo's path.

## ☁️ Gemini CLI Integration
To use this bridge as an AI Agent, update your `settings.json`:
```json
{
  "mcpServers": {
    "fractal-bridge": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/fractal-mcp-bridge/src/bridge/server.py"
      ]
    }
  }
}
```
