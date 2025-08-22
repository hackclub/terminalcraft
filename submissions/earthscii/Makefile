# Makefile for earthscii

.PHONY: help run build clean install test dist publish

help:
	@echo "Usage:"
	@echo "  make run         - Run the program"
	@echo "  make build       - Build PyInstaller binary"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make install     - Install locally with pip"
	@echo "  make dist        - Build wheel and sdist"
	@echo "  make publish     - Upload to PyPI (must have twine configured)"

run:
	python3 -m earthscii --globe

build:
	pyinstaller earthscii.spec

clean:
	rm -rf build dist *.egg-info __pycache__ src/__pycache__
	find . -name '*.pyc' -delete

install:
	pip install -e .

dist:
	python3 -m build

publish: dist
	twine upload dist/*
