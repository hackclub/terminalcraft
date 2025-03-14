from setuptools import setup, find_packages

setup(
    name="system_monitor",
    version="1.0.0",
    description="A terminal-based system resource monitor",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "sysmon=system_monitor:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
)
