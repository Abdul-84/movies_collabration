#!/bin/bash

echo "🚀 Setting up your Python Project Environment..."

# Step 1: Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3 first!"
    exit 1
fi

# Step 2: Make this script executable (self-permission)
chmod +x setup_project.sh

# Step 3: Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating a new virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "📦 Virtual environment (.venv) already exists. Skipping creation."
fi

# Step 4: Activate the virtual environment
echo "🔑 Activating the virtual environment..."
source .venv/bin/activate

# Step 5: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 6: Install project dependencies
echo "📚 Installing required Python packages..."
pip install networkx pyvis matplotlib pandas requests

# Step 7: Done
echo "✅ Environment setup complete!"
echo "🔵 To activate it manually later, just run: source .venv/bin/activate"