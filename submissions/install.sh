#!/usr/bin/env bash
set -e

# Check for required commands: python3, pip3, curl
for cmd in python3 pip3 curl; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed. Please install $cmd and try again."
    exit 1
  fi
done

# Determine the shell RC file
if [ -n "$ZSH_VERSION" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
  SHELL_RC="$HOME/.bashrc"
else
  SHELL_RC="$HOME/.profile"
fi

CLIENT_URL="https://raw.githubusercontent.com/yazidears/clipkeep/main/clipkeep.py"
INSTALL_DIR="$HOME/.local/bin"
INSTALL_FILE="$INSTALL_DIR/clipkeep"

# Create the installation directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download the client code
echo "Downloading ClipKeep client..."
TEMP_FILE=$(mktemp)
curl -sSL "$CLIENT_URL" -o "$TEMP_FILE"

# Prepend a shebang if missing
if ! head -n 1 "$TEMP_FILE" | grep -q "^#!"; then
  echo "Adding shebang to the client code..."
  TEMP_WITH_SHEBANG=$(mktemp)
  echo '#!/usr/bin/env python3' > "$TEMP_WITH_SHEBANG"
  cat "$TEMP_FILE" >> "$TEMP_WITH_SHEBANG"
  mv "$TEMP_WITH_SHEBANG" "$TEMP_FILE"
fi

# Move the file to the installation directory and make it executable
mv "$TEMP_FILE" "$INSTALL_FILE"
chmod +x "$INSTALL_FILE"
echo "Client installed to $INSTALL_FILE"

# Install required Python dependencies
echo "Installing required Python packages..."
pip3 install --upgrade --user requests pyperclip python-socketio

# Optional: check for cryptography support (for encryption features)
if python3 -c "import cryptography" &> /dev/null; then
  echo "Cryptography support available."
else
  echo "Cryptography not installed. Optional encryption features will be disabled."
fi

# Add INSTALL_DIR to PATH permanently if not already present
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo "export PATH=\$HOME/.local/bin:\$PATH" >> "$SHELL_RC"
  echo "Added $INSTALL_DIR to PATH in $SHELL_RC."
fi

# Apply the changes immediately
export PATH="$HOME/.local/bin:$PATH"

# Source the shell configuration file if it exists
if [ -f "$SHELL_RC" ]; then
  source "$SHELL_RC"
else
  echo "Warning: $SHELL_RC not found. Restart your terminal for changes to take effect."
fi

echo "ClipKeep installed successfully! You can now run 'clipkeep' from your terminal."
