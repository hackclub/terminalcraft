#!/bin/bash

# GoMail Run Script
# This script runs the GoMail application with optional arguments

set -e

# Default binary name
BINARY_NAME="gomail"

# Check if binary exists
if [ ! -f "$BINARY_NAME" ]; then
    echo "Binary '$BINARY_NAME' not found. Building first..."
    ./build.sh
fi

# Run the application with any provided arguments
echo "Running GoMail..."
./$BINARY_NAME "$@"