#!/bin/bash
# Dark terminal prompt
echo "Applying Dark Theme..."
sed -i '/# TerminalTalks Theme/d' ~/.bashrc
echo '# TerminalTalks Theme' >> ~/.bashrc
echo 'export PS1="\[\033[0;32m\]\u@\h:\w$ \[\033[0m\]"' >> ~/.bashrc
source ~/.bashrc
