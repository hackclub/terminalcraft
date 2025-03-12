from setuptools import setup, find_packages

setup(
    name="terminal-bookmarks",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tb=terminal_bookmarks.cli.commands:cli",
        ],
    },
    python_requires=">=3.8",
) 