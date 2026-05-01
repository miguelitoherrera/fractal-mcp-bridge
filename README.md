# Fractal MCP Bridge
**An MCP server for scaling fractal computations and rendering images.**

This repository serves as an AI agent backend, connecting the Model Context Protocol (MCP) to a high-performance
Python library for Mandelbrot and Julia sets.

## 🛠 Project Structure
The repository uses a source-layout to maintain clear separation between core mathematical logic and the MCP service
layer:

- `lib/fractal_core`: High-performance Numba-accelerated math for fractal math generation.
- `lib/utils`: image and other misc utils used by the code.
- `src/api`: contains a dedicated FastAPI router for an internal web explorer's backend logic (/render, /save).
- `src/bridge`:
  - `server.py`: MCP server implementation that exposes the library as tools for AI agents:
    - `generate_julia_image`: a tool that generates the Julia Set in the complex plane
    - `generate_mandelbrot_image`: a tool that generates the Mandelbrot Set complex plane
  - `fractal_app.py`: a clean "assembler" that plugs in the explorer router and mounts the static UI files

## 🚀 Local Setup & Development
To ensure the environment correctly resolves the internal package mappings, you must perform an editable installation.

### 1. Prerequisites
- **Python 3.14.1**
- **Node.js / npx** (required for the MCP Inspector)

### 2. Installation
From the repository root, run:
```bash
pip install -r requirements.txt.
````

From the repository root, run the following command, which uses the `pyproject.toml` to map `lib.fractal_core`
and `src.bridge` modules to your Python environment.
```bash
pip install -e .
```

### 3. Smoke Testing
You can manually verify the bridge and Numba-accelerated logic using the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector /absolute/path/to/python src/bridge/server.py
```
Open the browser link provided by the inspector to test the `generate_mandelbrot` and `generate_julia` tools.

### 3. Unit Tests
You can use this convenient executable to run unit tests with coverage. From the repository root, run:
```bash
bin/run-unit-tests
```

## Interactive Web Explorer
If you want to interactively explore the Mandelbrot and Julia sets in more detail, you can also spin up the
Fractal Web Explorer. From the repository root, run:
```bash
bin/run-interactive-server
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