from setuptools import setup, find_packages

setup(
    name="termicast",
    version="1.0.0",
    description="Terminal-based offline weather forecasting using satellite TLE data",
    author="TermiCast Team",
    packages=find_packages(),
    install_requires=[
        "skyfield>=1.46",
        "rich>=13.0.0",
        "click>=8.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.6.0",
        "termplotlib>=0.3.0",
        "pyserial>=3.5",
        "geopy>=2.3.0",
        "python-dateutil>=2.8.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "termicast=termicast.cli:main",
        ],
    },
    python_requires=">=3.8",
) 