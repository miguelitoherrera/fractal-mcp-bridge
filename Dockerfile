# ==============================================================================
# STAGE 1: Builder
# ==============================================================================
FROM python:3.14.1-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Numba and NumPy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the entire project first to run tests and checks
COPY . .

# Install the project in editable mode with development dependencies
RUN pip install --no-cache-dir -e .[dev]

# Run formatting, linting, type checks, and unit tests
RUN ./bin/run-checks

# Re-create/clean the venv and install only production dependencies
RUN rm -rf /opt/venv && python -m venv /opt/venv
RUN pip install --no-cache-dir .

# ==============================================================================
# STAGE 2: Runner (Bare-bones final image)
# ==============================================================================
FROM python:3.14.1-slim AS runner

# Set working directory
WORKDIR /app

# Copy the virtual environment containing only production dependencies from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the production source code and configuration files
COPY src/ /app/src/
COPY pyproject.toml /app/pyproject.toml

# Install the app in editable mode without re-downloading dependencies
# This creates the 'fractal-mcp' command and ensures image outputs go to /app/images
RUN pip install --no-cache-dir --no-deps -e .

# Expose ports for the bridge server (8080) and the web explorer (8001)
EXPOSE 8080
EXPOSE 8001

# Run the web explorer by default
CMD ["fractal-web-explorer"]

