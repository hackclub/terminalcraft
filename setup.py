from setuptools import setup, find_packages

setup(
    name="CLI-multiplayer",
    version="0.2",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],  # Add dependencies here if needed
    entry_points = {
        "console_scripts" : [
        "Start_2PlayerGames = TwoPlayerGamesCLI.Multiplayer_CLI:main",
        ],
    },
)

# after updatind remember to update version and type  "python setup.py sdist bdist_wheel" to command promt without speech marks
