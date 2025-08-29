from setuptools import setup, find_packages

with open('README.md', 'rb') as f:
    description = f.read().decode('utf-8')

setup(
    name='plazma-cloc',
    version='1.2.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cloc=cloc.__main__:main',
        ],
    },
    include_package_data=True,
    package_data={
        "cloc": ["languages.json"]
    },
    install_requires=[],
    long_description=description,
    long_description_content_type="text/markdown",
)