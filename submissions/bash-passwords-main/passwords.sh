#!/bin/bash

type="$1"

fileName="password.txt"
file=/$fileName

if [ ! -f "$file" ]; then
  touch $fileName
fi

data=$(cat $fileName)

if [ "$type" = "list" ]; then
  echo "$data"
elif [ "$type" = "generate" ]; then
  char_set="A-Za-z0-9!@#$%^&*()-_=+[]{}|;:,.<>?"

  tr -dc "$char_set" < /dev/urandom | head -c "$2"
  echo
elif [ "$type" = "get" ]; then
  echo "$data" | grep -i "$2"
elif [ "$type" = "add" ]; then
  echo "${2}: ${3}" >> "$fileName"
  echo "Operation complete"
else
  echo "That is not an option"
fi
