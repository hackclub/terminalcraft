from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='flightdeck',
    version='10.10.23',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'flightdeck = flightdeck.main:main_loop',
        ],
    },
    install_requires=[
        'requests',
        'rich',
        'pyAesCrypt',
        'pillow',
        'colorama'
    ],
    author='Advait Contractor',
    author_email='advait@advaitconty.com',
    description='A multi-tool CLI for the masses, with a file encrypter.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/advaitconty/flightdeck',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,  # Important: Include non-code files
    package_data={'flightdeck': ['background.jpg']},  # Include background.jpg
)