#!/bin/bash

echo "📦 Installing Terminal Talks..."

# Install Python dependencies forcefully
echo "🔧 Installing Python dependencies "
python3 -m pip install --user --break-system-packages --force-reinstall -r requirements.txt

# Define install target
TARGET="$HOME/.local/bin"
CMD_NAME="terminal-talks"

# Create target directory if needed
mkdir -p "$TARGET"

# Copy script
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

# Warn if not in PATH
if ! echo "$PATH" | grep -q "$TARGET"; then
    echo ""
    echo "⚠️ $TARGET is not in your PATH."
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo "Then run: source ~/.bashrc"
else
    echo "🚀 You can now run the tool by typing:"
    echo "    $CMD_NAME"
fi
