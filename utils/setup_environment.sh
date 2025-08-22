#!/bin/bash
"""
Environment setup script for MellowMind deployment.
Creates a new conda environment called 'moly' and installs all required dependencies.
"""

set -e  # Exit on any error

echo "🐍 Setting up MellowMind conda environment..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ conda not found. Please install Miniconda or Anaconda first."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Initialize conda for bash (in case it's not already done)
eval "$(conda shell.bash hook)"

# Check if moly environment already exists
if conda env list | grep -q "^moly "; then
    echo "⚠️  Conda environment 'moly' already exists."
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing 'moly' environment..."
        conda env remove -n moly -y
    else
        echo "✅ Using existing 'moly' environment."
        conda activate moly
        echo "📦 Installing/updating requirements..."
        pip install -r requirements.txt
        echo "✅ Environment setup completed!"
        exit 0
    fi
fi

# Create new conda environment
echo "🆕 Creating new conda environment 'moly'..."
conda create -n moly python=3.9 -y

# Activate the environment
echo "🔄 Activating conda environment..."
conda activate moly

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in current directory."
    echo "   Make sure you're running this script from the deploy folder."
    exit 1
fi

# Install requirements
echo "📦 Installing Python packages from requirements.txt..."
pip install -r requirements.txt

# Verify installation
echo "🔍 Verifying installation..."
python -c "import sys; print(f'Python version: {sys.version}')"
echo "📋 Installed packages:"
pip list --format=freeze | head -10
echo "..."
echo "$(pip list --format=freeze | wc -l) total packages installed"

echo ""
echo "✅ Environment setup completed successfully!"
echo "🚀 To use the environment:"
echo "   conda activate moly"
echo "   python3 run_mellowmind_compiled.py"
echo ""
echo "💡 Or simply double-click the MellowMind.app on your Desktop!"