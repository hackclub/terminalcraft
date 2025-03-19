from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="hc_ai_terminal",
    version="0.3",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ai = ai_terminal.ai:main',  # Replace with correct module path
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)
