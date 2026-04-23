# Fractal MCP Bridge
**An MCP server for scaling fractal computations and BigQuery data pipelines on Google Cloud.**

This repository serves as an AI agent backend, connecting the Model Context Protocol (MCP) to a high-performance Python fractal library and Google Cloud Platform services.

## 🛠 Project Structure
The repository uses a source-layout to maintain clear separation between core mathematical logic and the MCP service layer:

- `lib/fractal_core/`: High-performance Numba-accelerated math for Mandelbrot and Julia sets.
- `src/bridge/`: MCP server implementation (`server.py`) that exposes the library as tools for AI agents.

## 🚀 Local Setup & Development
To ensure the environment correctly resolves the internal package mappings, you must perform an editable install.

### 1. Prerequisites
- **Python 3.14.1**
- **Node.js / npx** (required for the MCP Inspector)

### 2. Installation
From the repository root, run:
```bash
pip install -e .
```

This command uses the `pyproject.toml` to map `lib/fractal_core` and `src/bridge` to your Python environment.

### 3. Smoke Testing
Verify the bridge and Numba-accelerated logic using the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python src/bridge/server.py
```

Open the browser link provided by the inspector to test the `generate_mandelbrot` and `generate_julia` tools.

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

## Interactive Web Explorer
If you want to interactively explore the Mandelbrot and Julia sets in more detail, you can also spin up the Fractal Explorer:
```bash
/absolute/path/to/python src/interactive_server.py 
```