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

# Ensure scripts are executable
RUN chmod +x bin/run-checks bin/run-fractal-web-explorer

# Install the project in editable mode with development dependencies.
# This uses your pyproject.toml to map lib/fractal_math correctly and includes test/lint tools.
RUN pip install --no-cache-dir -e .[dev]

# Run formatting, linting, type checks, and unit tests, then clean up generated test artifacts
RUN ./bin/run-checks && rm -rf htmlcov .coverage


# Expose ports for the bridge server (8080) and the web explorer (8001)
EXPOSE 8080
EXPOSE 8001

# Run the web explorer by default
CMD ["./bin/run-fractal-web-explorer"]

