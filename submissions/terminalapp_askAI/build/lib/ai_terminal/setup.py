from setuptools import setup, find_packages

setup(
    name="hc_ai_terminal",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
        "termcolor",
    ],
    entry_points={
        "console_scripts": [
            "ai = ai_terminal.ai:main",  # This assumes `main` is in `ai.py` within the `ai_terminal` package
        ],
    },
)
