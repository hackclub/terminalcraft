from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="word-counter-cli",
    version="0.1.0",
    author="Word Counter CLI Author",
    author_email="author@example.com",
    description="A cross-platform CLI utility to analyze text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/word-counter-cli",
    packages=find_packages(),
    py_modules=["wordcounter"],
    entry_points={
        "console_scripts": [
            "wordcounter=wordcounter:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "tqdm>=4.62.0",
    ],
)
