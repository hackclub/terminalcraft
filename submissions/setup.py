from setuptools import setup, find_packages

setup(
    name="socketpeek",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
        "textual>=0.27.0", 
    ],
    entry_points={
        'console_scripts': [
            'socketpeek=src.main:main',
        ],
    },
    author="AndreansxTech",
    author_email="koliberekart@icloud.com",
    description="A tool to check port connectivity, trace network routes, and perform WHOIS lookups",
    keywords="network, socket, port, scan, traceroute, whois",
    url="https://github.com/AndreansxTech/socketpeek",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
