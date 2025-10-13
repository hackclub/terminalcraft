from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import urllib.request
import json

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        self._post_install()

    def _post_install(self):
        url = "https://raw.githubusercontent.com/cloudyio/clisearch/refs/heads/main/search/config/bang.json"
        bang_path = os.path.join(os.path.expanduser("~"), ".searchcli/bang.json")
        os.makedirs(os.path.dirname(bang_path), exist_ok=True)
        urllib.request.urlretrieve(url, bang_path)
        print(f"Downloaded bang.json to {bang_path}")

        config_path = os.path.join(os.path.expanduser("~"), ".searchcli/config.json")
        config_data = {"default": "g"}
        with open(config_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)
        print(f"Created config.json with default bang 'g' at {config_path}")

setup(
    name='clisearch',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points='''
        [console_scripts]
        search=search.main:search
    ''',
)
