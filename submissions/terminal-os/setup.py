#!/usr/bin/env python3
"""Setup script for TerminalOS."""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="terminalos",
    version="1.0.0",
    author="000x",
    author_email="SITHUMSS9122@gmacil.com",
    description="A complete operating system experience in your terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/000xs/terminalos",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Topic :: System :: System Shells",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Console :: Curses",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "audio": ["pygame>=2.3.0", "mutagen>=1.47.0"],
        "media": ["pillow>=9.0.0", "opencv-python>=4.5.0"],
    },
   entry_points={
    'console_scripts': [
        'terminalos=terminalos.__main__:main',
    ],
},
    include_package_data=True,
    package_data={
        "terminalos": [
            "assets/themes/*.json",
            "assets/sounds/*.wav",
            "assets/icons/*.txt",
        ],
    },
    keywords="terminal, os, tui, cli, desktop, file-manager, text-editor",
    project_urls={
        "Bug Reports": "https://github.com/000xs/terminalos/issues",
        "Source": "https://github.com/000xs/terminalos",
        "Documentation": "https://terminalos.readthedocs.io/",
    },
)