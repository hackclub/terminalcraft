from setuptools import setup

setup(
    name="codesec-cli",
    packages=["codesec"],
    install_requires=[
        "textual>=0.47.1",
        "rich>=13.0.0",
        "tree-sitter>=0.20.1",
        "typing-extensions>=4.0.0",
        "networkx>=3.0",
    ],
)