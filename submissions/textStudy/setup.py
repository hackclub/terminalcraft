from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
if sys.version_info >= (3, 12):
    sys.exit("textStudy requires Python <= 3.11 due to sentencepiece compatibility issues.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textStudy",
    version="1.0.0",
    author="Mohamed Nady",
    author_email="mohamed0011199@gmail.com",
    description="Turn YouTube videos or local videos into enhanced study guides for loves reading with text, images, summaries, and questions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohamedNadyS/textStudy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8,<3.12",
    install_requires=[
        "torch",
        "openai-whisper",
        "opencv-python",
        "transformers",
        "sentencepiece",
        "accelerate",
        "typer[all]",
        "imageio-ffmpeg",
        "yt-dlp",
        "yt-dlp[extractors]",
        "browser-cookie3",
        "rich",
        "ffmpeg-python",
        "nltk",
        "semantic_text_splitter",
        "tokenizers",
        "weasyprint",
        "requests",
        "secretstorage",
    ],
    entry_points={
        "console_scripts": [
            "textStudy=textStudy.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
