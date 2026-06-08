#!/bin/bash
# Hacker green prompt
echo "Applying Hacker Theme..."
sed -i '/# TerminalTalks Theme/d' ~/.bashrc
echo '# TerminalTalks Theme' >> ~/.bashrc
echo 'export PS1="\[\033[1;32m\][HACKER] \u@\h:\w$ \[\033[0m\]"' >> ~/.bashrc
source ~/.bashrc
