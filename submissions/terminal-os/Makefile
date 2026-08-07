.PHONY: help install install-dev test lint format clean build upload docs

help:
	@echo "TerminalOS Development Commands:"
	@echo "  install      Install TerminalOS"
	@echo "  install-dev  Install in development mode"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"
	@echo "  docs         Build documentation"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=terminalos --cov-report=html

lint:
	flake8 terminalos tests
	mypy terminalos

format:
	black terminalos tests
	isort terminalos tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

docs:
	cd docs && make html

run:
	python -m terminalos

demo:
	python -m terminalos --theme matrix --no-boot

dev-run:
	python -m terminalos --debug --theme cyberpunk