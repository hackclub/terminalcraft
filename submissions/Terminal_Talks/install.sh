#!/bin/bash

echo "📦 Installing Terminal Talks..."

# Install Python dependencies
echo "🔧 Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

# Define install target
TARGET="$HOME/.local/bin"
CMD_NAME="terminal-talks"

# Create directory if it doesn't exist
mkdir -p "$TARGET"

# Copy executable
if cp terminal-talks "$TARGET/$CMD_NAME"; then
    chmod +x "$TARGET/$CMD_NAME"
    echo "✅ Installed to $TARGET/$CMD_NAME"
else
    echo "❌ Failed to copy script to $TARGET"
    echo "Please try manually:"
    echo "   sudo cp terminal-talks /usr/local/bin/$CMD_NAME"
    echo "   sudo chmod +x /usr/local/bin/$CMD_NAME"
    exit 1
fi

# Check if $TARGET is in PATH
if ! echo "$PATH" | grep -q "$TARGET"; then
    echo ""
    echo "⚠️ $TARGET is not in your PATH."
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
else
    echo "🚀 You can now run the tool using:"
    echo "    terminal-talks"
fi
