from setuptools import setup, find_packages

setup(
    name="CliTunesGithub",
    version="0.1.1",
    description="Terminal Music Player",
    long_description="CliTunes is a terminal music player that supports playing local music files and streaming from Spotify.",
    author="Ye Gao",
    author_email="ye.gao@student.tdsb.on.ca",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pygame",
        "requests",
        "spotipy",
        "mutagen",
    ],
    entry_points={
        "console_scripts": [
            "clitunes=clitunes.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    python_requires=">=3.7",
)