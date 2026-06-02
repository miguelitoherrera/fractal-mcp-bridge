# Fractal MCP Bridge
**An MCP server for scaling fractal computations and rendering images.**

This repository serves as an AI agent backend, connecting the Model Context Protocol (MCP) to a high-performance
Python library for Mandelbrot, Julia, and Exponential sets.

## 🧮 Mathematical Formulas

The computations in this library are based on the following iterative equations in the complex plane:

- **Mandelbrot Set**: $z_{n+1} = z_n^2 + c$
  - Initial condition: $z_0 = 0$
  - $c$ is the coordinate in the complex plane being evaluated.
- **Julia Set**: $z_{n+1} = z_n^2 + c$
  - Initial condition: $z_0$ is the coordinate in the complex plane being evaluated.
  - $c$ is a fixed complex constant for the entire set.
- **Exponential Set**: $z_{n+1} = c \cdot e^{z_n}$
  - Initial condition: $z_0$ is the coordinate in the complex plane being evaluated.
  - $c$ is a fixed complex constant.
- **Sine Set**: $z_{n+1} = c \cdot \sin(z_n)$
- **Cosine Set**: $z_{n+1} = c \cdot \cos(z_n)$
  - Initial condition: $z_0$ is the coordinate in the complex plane being evaluated.
  - $c$ is a fixed complex constant.

## 🏗 Project Architecture
The repository follows a standard Python "src layout" under a unified `fractal_mcp` package. This maintains clear separation between mathematical logic, image processing, and service orchestration:

- **Math Layer (`src/fractal_mcp/math`)**: 
  - `mandelbrot.py`, `julia.py`, `exponents.py`, & `sine.py`: Pure, Numba-accelerated mathematical functions for calculating fractal escape grids. This layer is strictly computational and has no knowledge of image formats or resolutions.
- **Orchestration & Imaging Layer (`src/fractal_mcp/renderer.py`)**: 
  - The unified "brain" of the library. It manages coordinate defaults, calculates aspect ratios to prevent image stretching, and converts numerical escape grids into colorful JPEG images using Bokeh colormaps.

### Service Layer
- **Fractal Explorer App (`src/fractal_mcp/app`)**: An encapsulated web application. Includes the FastAPI orchestrator (`main.py`), the API routing endpoints (`api/`), and the web assets (`static/`).
- **MCP Bridge (`src/fractal_mcp/bridge`)**: FastMCP server implementation that exposes the library as tools for AI agents.

## 🌍 Fractal Web Explorer
If you want to interactively explore the Mandelbrot, Julia, and Exponential sets in more detail, you can spin up the encapsulated
Fractal Web Explorer. From the repository root, run:
```bash
bin/run-fractal-web-explorer
```
Open the browser link provided in the terminal.

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
npx @modelcontextprotocol/inspector /absolute/path/to/python src/fractal_mcp/bridge/server.py
```
Open the browser link provided by the inspector to test the `generate_mandelbrot_image`, `generate_julia_image`, `generate_exponential_image`, and `generate_sine_image` tools.

### 4. Code Quality & Unit Tests
To ensure high standards for code style, type safety, and correctness, use the unified check script. This script runs:
1.  **Ruff Format**: Ensures consistent code styling.
2.  **Ruff Lint**: Catches common errors and smells.
3.  **Mypy**: Validates static types across the codebase.
4.  **Pytest**: Executes unit tests with coverage reporting.

From the repository root, run:
```bash
bin/run-checks
```

### 5. 🐛 Bug Hunt
When asked to **"go on a bug hunt"**, perform an all-encompassing search for bugs within the repository across the following four categories:

1. **Functional Bugs (Most Important):** Look for logic errors, off-by-one errors, null/undefined issues, race conditions, incorrect conditionals, missing edge cases, wrong variable usage, broken control flow, and any code that simply won't work as intended. This is by far the most important category.
2. **KISS Violations:** Overly complex solutions where simpler ones exist. Unnecessary abstractions, premature generalizations, or convoluted logic.
3. **DRY Violations:** Duplicated logic that should be extracted. Copy-and-pasted code with minor variations.
4. **Missing Tests:** New functionality or bug fixes lacking appropriate test coverage.

DO NOT report:
* Code formatting or style issues (we do this already with ruff)
* Minor type issues (also linted)
* Nitpicks that don't affect correctness or maintainability.

For each issue found, report:
* File and line number
* Severity: critical/high/medium/low
* Category: the items 1 thru 4.
* Description: what the issue is an d why it matters.
* Suggestion: how to fix it.

Return a structured list grouped by severity (critical first, then high, then medium, then low).
## 🤖 Claude Desktop Integration
To use this bridge as an AI Agent, update your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fractal-bridge": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/fractal-mcp-bridge/src/fractal_mcp/bridge/server.py"
      ]
    }
  }
}
```
Take special care to align the python path with this repo's path.

## ☁️ Antigravity CLI Integration
To use this bridge as an AI Agent, update your `mcp_config.json`:
```json
{
  "mcpServers": {
    "fractal-bridge": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/fractal-mcp-bridge/src/fractal_mcp/bridge/server.py"
      ]
    }
  }
}
```
