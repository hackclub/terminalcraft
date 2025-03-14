from setuptools import setup, find_packages

setup(
    name="termigit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "textual>=0.27.0",
        "gitpython>=3.1.30",
    ],
    entry_points={
        'console_scripts': [
            'termigit=termigit.main:main',
        ],
    },
    author="PawiX25",
    description="A terminal-based Git client built with Python and Textual",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PawiX25/Termigit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
