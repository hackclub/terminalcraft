#!/bin/bash

# GoMail Build Script
# This script builds the GoMail application for the current platform

set -e

# Get version from git or use 'dev'
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")
BINARY_NAME="gomail"

echo "Building GoMail version: $VERSION"

# Build the application
echo "Compiling Go application..."
CGO_ENABLED=1 go build -ldflags="-s -w -X main.Version=$VERSION" -o "$BINARY_NAME" .

# Make it executable
chmod +x "$BINARY_NAME"

echo "✓ Build successful: $BINARY_NAME"
echo "✓ Version: $VERSION"
echo ""
echo "To run the application:"
echo "  ./$BINARY_NAME --help"
echo "  ./run.sh --help"
