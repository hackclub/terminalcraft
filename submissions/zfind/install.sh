#!/bin/bash

#run this script to access zfind from anywhere

# Get the path of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "cd $DIR" > ~/.zfind.sh
echo "python3 -m venv "$DIR/venv"" > ./zfind.sh
echo "source "$DIR/venv/bin/activate"" >> ./zfind.sh
echo "pip install -r "$DIR/requirements.txt"" >> ./zfind.sh
echo "python "$DIR/zfind.py"" >> ./zfind.sh
cp ./zfind.sh /usr/local/bin/zfind
chmod +x /usr/local/bin/zfind
echo "zfind installed successfully"