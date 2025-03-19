from setuptools import setup

setup(
    name="clipkeep",
    version="2.0.0",
    py_modules=["clipkeep"],
    install_requires=[
        "requests",
        "pyperclip",
        "python-socketio"
    ],
    extras_require={
        "crypto": ["cryptography"]
    },
    entry_points={
        "console_scripts": [
            "clipkeep=clipkeep:main"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A clipboard synchronization tool with auto-sync, real-time updates, backup/restore, and optional encryption.",
    url="https://github.com/yourusername/clipkeep",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
