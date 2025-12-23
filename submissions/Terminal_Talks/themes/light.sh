#!/bin/bash
# Light terminal prompt
echo "Applying Light Theme..."
sed -i '/# TerminalTalks Theme/d' ~/.bashrc
echo '# TerminalTalks Theme' >> ~/.bashrc
echo 'export PS1="\[\033[1;34m\]\u@\h:\w$ \[\033[0m\]"' >> ~/.bashrc
source ~/.bashrc
