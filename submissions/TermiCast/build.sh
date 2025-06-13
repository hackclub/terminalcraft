#!/bin/bash
# Quick build script for Unix/Linux/macOS
# Just run: ./build.sh

echo "🛰️  TermiCast Build Script"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "   Install it from https://python.org"
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies if needed
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "   Try: pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies installed"

# Run the build script
echo "🔨 Building executable..."
python3 build_executable.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Build complete!"
    echo "📍 Your executable is in: dist/"
    echo "🚀 Run it with: ./dist/termicast"
    
    # Make it executable just in case
    chmod +x dist/termicast 2>/dev/null
else
    echo "❌ Build failed - check the output above"
    exit 1
fi 