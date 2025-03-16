#!/bin/bash

# Create main directories
mkdir -p game tests

# Create game module files
touch game/__init__.py
touch game/main.py
touch game/api.py
touch game/gameplay.py
touch game/narrative.py
touch game/ui.py

# Create test files
touch tests/test_gameplay.py
touch tests/test_narrative.py

# Create root files
touch setup.py
touch requirements.txt
touch README.md
touch .env
