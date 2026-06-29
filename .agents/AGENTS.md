# Gemini Repository Guidelines Index

This repository uses a consolidated guidelines and rules structure.

## Core Persona & Loop
- **Audience:** I expect high-quality code, with strict readability and lean implementations.
- **Core Loop & Workflow:**
  - **Direct Action & Tool Invocation:** For action requests that map to an existing tool (like playing/pausing Sonos or broadcasting messages), invoke the native MCP tool or the CLI fallback (`fastmcp call`) immediately. Do not perform codebase research, read tool source code, or prepare/test the environment unless execution fails.
  - **Implementation Planning:** When proposing a plan, always provide the **human context first**. Do not show any code changes until the context is explicitly approved.
  - **Verification Priority:** Always run local tests and style checks after making changes (but not for md files), and present the results in full.
  - **Git Summaries:** When asked to summarize a git diff or changes, always format the response as a Pull Request summary using the exact template, branch naming rules, and block formatting specified in the git_operations skill.
  - **CLI Tool Execution:** Do not assume MCP tools are inaccessible if they are not listed in the client permissions. Always check the README.md or .agents/mcp_config.json for how to execute and test tools directly from the terminal.
  - **MCP Tool Extensions:** If you find yourself bypassing the MCP tools and creating your own custom Python code or scripts to achieve an objective that should be served by a tool, let Mike know that you need a new MCP tool created.

---

## Formatting & Styling Rules

### Python Style & Quality
- **Cleanliness & Human Readability:** Keep code modifications minimal, direct, simple, and self-documenting. Avoid overengineering, convoluted logic, overly complex one-liners, and obscure naming. Minimize temporary variable usage inside functions to maximize readability.
- **Formatting, Linting & Typing:** Ensure all source files conform to Ruff formatting/linting guidelines and maintain correct, strict type annotations throughout the package.

---

## Testing & Verification Rules

### Testing Guidelines
- **Test Coverage:** All unit tests must target **100% statement coverage** (or at least 99% after trying).
- **Compulsory Unit Tests:** Always create a unit test for every function or class you create.
- **Dedicated Test Files:** When creating a new code module or source file, always create a corresponding, dedicated test file containing its unit tests. Do not place unit tests for a new module inside existing test files.
- **Automated Checks:** Always run `bin/run-checks` (if available) after making any code changes (but not for md files). This script executes:
  1. Ruff formatting checks: `ruff format --check src tests`
  2. Ruff linting checks: `ruff check src tests`
  3. Mypy type checking: `mypy`
  4. Pytest suite with coverage: `python -m pytest --cov=fractal_mcp tests` (Note: adjust project name if needed)
- **Reporting Output:** Present the **full output** of validation runs (such as terminal check scripts) to the user when requested or when executing checks.

---

## Safety & Behavioral Boundaries

### Git Restrictions
- **Never** make a git commit or run a git push unless explicitly instructed to do so.

### Documentation Integrity
- **Preserve Comments & Docstrings:** Maintain documentation integrity. Preserve all existing comments and docstrings that are unrelated to your code changes, unless explicitly asked to modify them.

### File System Restrictions
- **No Unapproved File Operations:** Do not move, rename, delete, or relocate files in the repository without explicit permission.
- **Base Directory Bounds:** Do not edit, create, write, or modify any files outside the current active workspace root directory (as defined in the workspace metadata) without explicit permission.

---

## Platform & Environment Constraints

### OS Assumptions
- **Operating System:** Although the target platform is macOS and linux, Windows is not excluded. Keep paths and CLI compatibility aligned.
