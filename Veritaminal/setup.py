"""
Setup script for the Veritaminal package.
"""
from setuptools import setup, find_packages
import os

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

# Read version from the package
with open(os.path.join("game", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("'\"")
            break

setup(
    name="veritaminal",
    version=version,
    author="Maverick",
    author_email="kamaludeenmoussa@gmail.com",
    description="A terminal-based document verification game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maverickkamal/veritaminal",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Games/Entertainment",
        "Intended Audience :: End Users/Desktop",
    ],
    python_requires=">=3.8",
    install_requires=[
        "google-genai>=1.5.0",
        "prompt_toolkit>=3.0.50",
        "python-dotenv>=1.0.1",
        "requests>=2.32.1",
        "colorama>=0.4.6",
        "pydantic>=2.10.6",
    ],
    entry_points={
        "console_scripts": [
            "veritaminal=game.main:main",
        ],
    },
    include_package_data=True,
)
