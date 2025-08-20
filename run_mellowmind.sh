#!/bin/bash

# MellowMind Desktop App Launcher
# This script runs the Python app directly without needing the signed macOS bundle

# Set the working directory to the project root
cd "$(dirname "$0")"

# Set Python path to include src directory
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Run the app with the conda environment Python
/opt/miniconda3/envs/moly/bin/python3 src/app.py "$@"