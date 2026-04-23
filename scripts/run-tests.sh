#!/bin/bash

# Set PYTHONPATH and run pytest in a single command
# This ensures PYTHONPATH is only modified for this specific process.
PYTHONPATH=$PYTHONPATH:$(pwd)/src:$(pwd)/lib pytest tests "$@"
