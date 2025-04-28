#!/bin/bash

echo "🚀 Setting up your Python Project Environment..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3 first!"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "📦 Creating a new virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "📦 Virtual environment (.venv) already exists. Skipping creation."
fi

echo "🔑 Activating the virtual environment..."
source .venv/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📚 Installing required Python packages..."
pip install networkx pyvis matplotlib pandas requests

echo "✅ Environment setup complete!"
echo "🔵 To activate it manually later, run: source .venv/bin/activate"
