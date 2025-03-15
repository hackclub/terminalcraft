#!/bin/bash

# Run this script to access zfind from anywhere

# Get the path of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "cd $DIR" > ~/.zfind.sh
echo "python3 -m venv \"$DIR/venv\"" >> ~/.zfind.sh
echo "source \"$DIR/venv/bin/activate\"" >> ~/.zfind.sh
echo "pip install -r \"$DIR/requirements.txt\"" >> ~/.zfind.sh
echo "python \"$DIR/zfind.py\"" >> ~/.zfind.sh
Echo "deactivate" >> ~/.zfind.sh
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo cp ~/.zfind.sh /usr/local/bin/zfind
    sudo chmod +x /usr/local/bin/zfind
elif [[ "$OSTYPE" == "darwin"* ]]; then
    cp ~/.zfind.sh /usr/local/bin/zfind
    chmod +x /usr/local/bin/zfind
fi

echo "zfind installed successfully"
