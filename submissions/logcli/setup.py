from setuptools import setup, find_packages

setup(
    name="logcli",
    version="0.1.1",
    packages=find_packages(),  # Finds all packages inside logcli/
    install_requires=[
        "requests",
        "click",
        "rich",
        "argparse"
    ],
    entry_points={
        "console_scripts": [
            "logcli=logcli.main:main",  # Ensure this points to main()
        ],
    },
)
