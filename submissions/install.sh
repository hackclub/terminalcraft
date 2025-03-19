#!/usr/bin/env bash
set -e

# Check for required commands: python3, pip3, curl
for cmd in python3 pip3 curl; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed. Please install $cmd and try again."
    exit 1
  fi
done

CLIENT_URL="https://raw.githubusercontent.com/yazidears/clipkeep/refs/heads/main/clipkeep.py"
INSTALL_DIR="$HOME/.local/bin"
INSTALL_FILE="$INSTALL_DIR/clipkeep"

# Create the installation directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download the client code
echo "Downloading clipkeep client..."
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

# Add INSTALL_DIR to PATH permanently if not already present
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo "export PATH=\$HOME/.local/bin:\$PATH" >> "$SHELL_RC"
  echo "Added $INSTALL_DIR to PATH in $SHELL_RC."
fi


# Apply the changes immediately
export PATH="$HOME/.local/bin:$PATH"

# Source the shell configuration file only if it exists
if [ -f "$SHELL_RC" ]; then
  source "$SHELL_RC"
else
  echo "Warning: $SHELL_RC not found. Restart your terminal for changes to take effect."
fi

# Automatically update the user's shell configuration file
if [ -n "$ZSH_VERSION" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
  SHELL_RC="$HOME/.bashrc"
else
  SHELL_RC="$HOME/.profile"
fi

if [ -f "$SHELL_RC" ]; then
  if ! grep -q "$INSTALL_DIR" "$SHELL_RC"; then
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$SHELL_RC"
    echo "Added $INSTALL_DIR to PATH in $SHELL_RC."
  fi
else
  echo "No shell configuration file found. Please add $INSTALL_DIR to your PATH manually."
fi

# Test connection to the server
echo "Testing connection to the server..."
PING_OUTPUT=$(curl -sSL http://clipkeep.yzde.es/ping || true)
if echo "$PING_OUTPUT" | grep -q '"status": "ok"'; then
  echo "Server connection successful: $PING_OUTPUT"
else
  echo "Warning: Unable to connect to the server. Please check your network or server status."
  echo "warning, but honest: it's probably us and not you :D"

fi
echo "if clipkeep doesn't run when you try to summon it, try with the next command:"
echo "export PATH=$HOME/.local/bin:$PATH"
echo "note that this is a temporal solution"
echo "clipkeep installed successfully! You can now run 'clipkeep' from your terminal."

# Optionally, offer to reload the shell to update the PATH immediately
if [ -t 1 ]; then
  read -r -p "Do you want to reload your shell now to update your PATH? (y/N) " answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Reloading shell..."
    exec "$SHELL" -l
  fi
fi
