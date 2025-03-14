from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="doseper",
    version="1.0.1",
    author="HeronSky",
    author_email="heronskytw@gmail.com",
    description="A tool for sending multiple HTTP requests for website testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HeronSky/doseper",  
    project_urls={
        "Bug Tracker": "https://github.com/HeronSky/doseper/issues",
    },
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "doseper=doseper.main:main"
        ]
    },
    python_requires='>=3.6',
)