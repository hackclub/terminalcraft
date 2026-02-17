from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="git-narrate",
    version="1.0.3",
    description="The Repository Storyteller - Analyze git repos and generate development narratives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sithum Sathsara Rajapakshe | 000x",
    author_email="SITHUMSS9122@gmail.com",
    url="https://github.com/000xs/git-narrate",
    project_urls={
        "Bug Tracker": "https://github.com/000xs/git-narrate/issues",
        "Documentation": "https://github.com/000xs/git-narrate/wiki",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="git version-control repository-analysis storytelling visualization",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.2.1",
        "rich>=14.1.0",
        "GitPython>=3.1.44",
        "matplotlib>=3.10.5",
        "numpy>=2.3.2",
        "openai>=1.99.1",
        "python-dotenv>=1.0.1",
        "questionary>=2.1.0",
        "pyfiglet>=1.0.3",
        "requests>=2.28.0",
        "markdown2>=2.5.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "viz": ["kaleido>=0.2.1"],  # For static image export
    },
    entry_points={
        "console_scripts": [
            "git-narrate=git_narrate.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
