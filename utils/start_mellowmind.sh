#!/bin/bash

# MellowMind Desktop App Launcher
# This script launches the MellowMind application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project root directory (parent of utils)
cd "$SCRIPT_DIR/.."

echo "🧘 Starting MellowMind Desktop Application..."
echo "📂 Working directory: $(pwd)"

# Check if Python environment exists
if [ -d "/opt/miniconda3/envs/moly" ]; then
    echo "🐍 Using conda environment: moly"
    PYTHON_PATH="/opt/miniconda3/envs/moly/bin/python"
elif command -v python3 &> /dev/null; then
    echo "🐍 Using system Python3"
    PYTHON_PATH="python3"
else
    echo "❌ Error: Python3 not found!"
    echo "Please install Python3 or activate the moly conda environment"
    exit 1
fi

# Check if app.py exists in src directory
if [ ! -f "src/app.py" ]; then
    echo "❌ Error: src/app.py not found in $(pwd)"
    echo "Please make sure you're running this script from the MellowMind project root"
    exit 1
fi

# Launch the application
echo "🚀 Launching MellowMind..."
"$PYTHON_PATH" src/app.py

echo "👋 MellowMind application has closed"