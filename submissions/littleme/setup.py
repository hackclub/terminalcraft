from setuptools import setup, find_packages

setup(
    name="littleme",
    version="0.1", 
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "rich",
        "typer"
        "pyfiglet",

    ],
    entry_points={
        "console_scripts": [
            "littleme = littleme.main:main"
        ]
    },
)