from setuptools import setup, find_packages

setup(
    name="comboML",
    version="1.1.1",
    author="Abdur Rehman Tariq",
    author_email="artariqdev@gmail.com",
    description="A Textual-based application for exploring linear regression models.",
    packages=find_packages(),
    install_requires=[
        "textual",
        "pandas",
        "numpy",
        "scikit-learn"
    ],
    entry_points={
        "console_scripts": [
            "comboML=comboML.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
