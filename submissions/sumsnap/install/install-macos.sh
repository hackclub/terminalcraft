#!/bin/bash
set -e
REPO_OWNER="frinshhd"
REPO_NAME="sumsnap"

USE_PRERELEASE=0
if [[ "$1" == "--prerelease" ]]; then
  USE_PRERELEASE=1
fi

if [[ $USE_PRERELEASE -eq 1 ]]; then
  echo "Downloading latest *pre-release* sumsnap for macOS..."
  URL=$(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases" | \
    jq -r '[.[] | select(.prerelease)][0].assets[] | select(.name | test("sumsnap-macos$")) | .browser_download_url')
else
  echo "Downloading latest sumsnap for macOS..."
  URL=$(curl -s https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest | grep "browser_download_url.*sumsnap-macos" | cut -d '"' -f 4)
fi

if [ -z "$URL" ]; then
  echo "No suitable binary found!"
  exit 1
fi

curl -L "$URL" -o sumsnap
chmod +x sumsnap
echo "Moving sumsnap to /usr/local/bin (requires sudo)..."
sudo mv sumsnap /usr/local/bin/sumsnap
echo "Installed! Run 'sumsnap' from anywhere."