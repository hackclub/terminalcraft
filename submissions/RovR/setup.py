from setuptools import setup

setup(
    name="rovr",
    version="1.0",
    py_modules=["rovr"],
    entry_points={
        "console_scripts": ["rovr=rovr:main"],
    },
)