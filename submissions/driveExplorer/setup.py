from setuptools import setup, find_packages

setup(
    name="driveExplorer",
    version="0.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "urwid",
        "click",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
    ],
    entry_points={
        "console_scripts": [
            "dexp=driveExplorer.dexp:cli",
        ],
    },
)