from setuptools import setup, find_packages

setup(
    name="pngtools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=11.1.0",
        "numpy>=1.26.4",
    ],
    entry_points={
        'console_scripts': [
            'pngtools=pngtools.pngtools:main_cli',
        ],
    },
    author="YeetTheAnson",
    author_email="ansonlai019@gmail.com",
    description="A tool for manipulating PNG images",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)