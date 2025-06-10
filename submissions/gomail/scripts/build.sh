#!/bin/bash

# GoMail Release Script
# This script builds cross-platform binaries locally

set -e

VERSION=${1:-"dev"}
OUTPUT_DIR="dist"

echo "Building GoMail version: $VERSION"

# Clean previous builds
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# Build configurations
declare -a builds=(
    "windows/amd64/.exe"
    "windows/arm64/.exe"
    "darwin/amd64/"
    "darwin/arm64/"
    "linux/amd64/"
    "linux/arm64/"
    "linux/arm/"
    "freebsd/amd64/"
)

# Build for each platform
for build in "${builds[@]}"; do
    IFS='/' read -r GOOS GOARCH SUFFIX <<< "$build"
    
    echo "Building for $GOOS/$GOARCH..."
    
    binary_name="gomail-$GOOS-$GOARCH$SUFFIX"
    
    # Handle CGO for different platforms
    if [[ "$GOOS" == "linux" && "$GOARCH" == "amd64" ]]; then
        # Native build with CGO for linux/amd64
        env GOOS=$GOOS GOARCH=$GOARCH CGO_ENABLED=1 \
            go build -ldflags="-s -w -X main.version=$VERSION" \
            -o "$OUTPUT_DIR/$binary_name" .
    else
        # Cross-compile without CGO for other platforms
        env GOOS=$GOOS GOARCH=$GOARCH CGO_ENABLED=0 \
            go build -ldflags="-s -w -X main.version=$VERSION" \
            -o "$OUTPUT_DIR/$binary_name" .
    fi
    
    # Create archives
    cd $OUTPUT_DIR
    if [[ "$GOOS" == "windows" ]]; then
        zip "gomail-$VERSION-$GOOS-$GOARCH.zip" "$binary_name"
    else
        tar -czf "gomail-$VERSION-$GOOS-$GOARCH.tar.gz" "$binary_name"
    fi
    cd ..
    
    echo "✓ Built $binary_name"
done

echo ""
echo "Build complete! Binaries available in $OUTPUT_DIR/"
ls -la $OUTPUT_DIR/

echo ""
echo "To create a release:"
echo "1. Create and push a tag: git tag v$VERSION && git push origin v$VERSION"
echo "2. The GitHub Action will automatically create a release with these binaries"
