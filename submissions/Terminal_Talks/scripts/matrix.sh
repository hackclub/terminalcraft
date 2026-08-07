#!/bin/bash
# scripts/matrix.sh

echo "💻 Entering Matrix mode..."
echo -e "\e[1;40m"
tr -c "[:alnum:]" "A" < /dev/urandom | head -c 10000 | fold -w 80 | while read line; do
  echo -e "\e[32m$line\e[0m"
  sleep 0.05
done
