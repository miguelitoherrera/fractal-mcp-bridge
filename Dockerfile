# Using the specific Python 3.14.1 slim image
FROM python:3.14.1-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for building Numba and NumPy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project first to ensure pyproject.toml and lib/ are present
COPY . .

# Install the project in editable mode.
# This uses your pyproject.toml to map lib/fractal_math correctly.
RUN pip install --no-cache-dir -e .

# Cloud Run listens on 8080 by default
EXPOSE 8080

# Run the bridge server
CMD ["python", "src/fractal_mcp/bridge/server.py"]
