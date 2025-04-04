# setup.py
from setuptools import setup, find_packages

setup(
    name="git-guardian-cli",
    version="1.0.2",
    description="A CLI tool to scan Git repositories for sensitive information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="000x",
    author_email="sithumss9122@gmail.com",
    url="https://github.com/000xs/git-guardian-cli",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "git-guardian=git_guardian.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
