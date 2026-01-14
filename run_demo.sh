#!/bin/bash
# Quick demo script for CollectiveBrain

echo "============================================================"
echo "CollectiveBrain Multi-Agent System - Demo"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Install dependencies if needed
echo ""
echo "Checking dependencies..."
pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true

echo ""
echo "============================================================"
echo "Option 1: Run Main Application"
echo "============================================================"
echo ""
read -p "Run main application demo? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python collective_brain.py
fi

echo ""
echo "============================================================"
echo "Option 2: Run Basic Usage Example"
echo "============================================================"
echo ""
read -p "Run basic usage example? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python examples/basic_usage.py
fi

echo ""
echo "============================================================"
echo "Option 3: Run Tests"
echo "============================================================"
echo ""
read -p "Run test suite? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python -m pytest tests/ -v
fi

echo ""
echo "============================================================"
echo "Option 4: Start API Server"
echo "============================================================"
echo ""
read -p "Start API server? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting API server at http://localhost:8000"
    echo "Swagger UI: http://localhost:8000/docs"
    echo "Press Ctrl+C to stop"
    echo ""
    python api.py
fi

echo ""
echo "Demo completed!"
