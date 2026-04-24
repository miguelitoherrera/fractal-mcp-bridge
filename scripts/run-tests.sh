#!/bin/bash

# Disable Numba JIT during tests so that pytest-cov can accurately track coverage.
export NUMBA_DISABLE_JIT=1

# Set PYTHONPATH and run pytest with coverage enabled by default.
# This ensures PYTHONPATH is only modified for this specific process.
PYTHONPATH=$PYTHONPATH:$(pwd)/src:$(pwd)/lib pytest --cov=src --cov=lib --cov-report=term-missing --cov-report=html tests "$@"
