from setuptools import setup, find_packages

setup(
    name="projectmaker",
    version="0.1",
    packages=find_packages(),
    install_requires=["click", "pyyaml"],
    entry_points={
        "console_scripts": [
            "projectmaker=projectmaker.main:cli"
        ]
    },
    include_package_data=True,
    package_data={
        'projectmaker': ['config.yaml'],
    },
)