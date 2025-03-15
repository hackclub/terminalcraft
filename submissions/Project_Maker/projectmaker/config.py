import os
import yaml
import importlib.resources

# CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".projectmaker")


def load_config():
    """Loads the cofig file"""
    with importlib.resources.files("projectmaker").joinpath("config.yaml").open("r") as f:
        return yaml.safe_load(f)