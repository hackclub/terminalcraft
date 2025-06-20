from json import dumps, loads
from json.decoder import JSONDecodeError
from typing import Optional

from instance.client import Instance
from utils.merge import merge
from utils.requests import request


def settings(Client: Instance) -> dict:
    Client.log("DEBUG", "Loading settings.")

    try:
        with open(f"{Client.cwd}settings.json", "r") as f:
            try:
                settings = loads(f.read())
                Client.log("DEBUG", "Parsed settings.")

                keys = [
                    "['vigenere']",
                    "['vigenere']['bruteforce decode']",
                    "['vigenere']['bruteforce decode']['pause percentage']",
                    "['logging']",
                    "['logging']['debug']",
                    "['logging']['warning']",
                ]

                for option in keys:
                    try:
                        exec(f"settings{option}")
                    except KeyError:
                        Client.log(
                            "WARNING",
                            "Settings file is missing required keys. Salvaging config and downloading new file.",
                        )

                        return settings_salvager(Client, settings)

                Client.log("DEBUG", "Verified settings.")
                return settings
            except JSONDecodeError:
                Client.log(
                    "WARNING", "Settings file is corrupted. Downloading new file."
                )

                return settings_salvager(Client)
    except FileNotFoundError:
        Client.log("WARNING", "Settings file was not found. Downloading new file.")

        return settings_salvager(Client)


def settings_salvager(Client: Instance, old_settings: Optional[dict] = None) -> bool:
    req = request(
        Client,
        "https://raw.githubusercontent.com/skifli/Encrypx/main/src/current_version",
    )

    if not 199 < req.status_code < 300:
        Client.log(
            "ERROR",
            f"An error occured when getting the latest settings file. Status code: {req.status_code}. Content: {req.content}.",
        )

    new_settings = req.content

    if old_settings is not None:
        new_settings = merge(new_settings, old_settings)

    with open(f"{Client.cwd}settings.json", "w") as f:
        f.write(dumps(new_settings, indent=4))

    return new_settings
