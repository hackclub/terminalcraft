from contextlib import suppress
from datetime import datetime
from os import mkdir, name, system
from platform import python_implementation
from typing import Optional

from utils.console import fore, style


class Instance:
    def __init__(self, cwd: str) -> None:
        self.alphabets = (
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "0123456789",
        )

        self.cwd = cwd
        self.python_type = python_implementation()

        try:
            with open(f"{self.cwd}version", "r+") as f:
                self.version = f.read()
        except FileNotFoundError:
            self.log(
                "WARNING",
                "Version file was not found. Setting current version to `Unknown`.",
            )

            with open(f"{self.cwd}version", "w") as f:
                f.write("Unknown")

            self.version = "Unkown"

        with suppress(FileExistsError):
            mkdir(f"{cwd}logs/")

        with suppress(FileExistsError):
            mkdir(f"{cwd}logs/{self.version}")

        self.log_file = open(
            f"{cwd}logs/{self.version}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log",
            "a",
            errors="ignore",
        )

    def clear(self) -> None:
        system("cls" if name == "nt" else "clear")

    def get_plaintext(self) -> str:
        while True:
            plaintext = input(
                f"{style.Bold}Enter the plaintext:{style.RESET_ALL} {style.Italic}"
            )

            if plaintext.strip() == "":
                self.log("WARNING", "Invalid plaintext. Try again.\n")
                continue

            return plaintext

    def get_ciphertext(self) -> str:
        while True:
            ciphertext = input(
                f"{style.Bold}Enter the ciphertext:{style.RESET_ALL} {style.Italic}"
            )

            if ciphertext.strip() == "":
                self.log("WARNING", "Invalid ciphertext. Try again.\n")
                continue

            return ciphertext

    def get_key(
        self,
        input_type: str = "int",
        limit_min: int = 1,
        limit_max: Optional[int] = None,
    ) -> str:
        while True:
            key = input(
                f"{style.RESET_ALL + style.Bold}Enter the key:{style.RESET_ALL} {style.Italic}"
            )

            if input_type == "int":
                try:
                    key = int(key)

                    if key <= limit_min:
                        self.log(
                            "WARNING",
                            f"Invalid key (must be greater than {limit_min}). Try again.\n",
                        )
                        continue

                    if limit_max is not None:
                        if key >= limit_max:
                            self.log(
                                "WARNING",
                                f"Invalid key (must smaller than {limit_max}). Try again.\n",
                            )
                            continue
                except ValueError:
                    self.log(
                        "WARNING", "Invalid key (must be an integer). Try again.\n"
                    )
                    continue

            if input_type == "str" and any(not char.isalpha() for char in key):
                self.log(
                    "WARNING", "Invalid key (must only contain letters). Try again.\n"
                )
                continue

            return key

    def sentence_probability(self, text: str) -> float:
        percentage = 0
        split = text.split(" ")

        for word in split:
            if word.lower() in self.words or not word.isalpha():
                percentage += 1

        return percentage / len(split) * 100

    def shift(self, alphabet: str, key: int) -> str:
        return alphabet[key:] + alphabet[:key]

    def log(self, level: str, text: str) -> bool:
        if "settings" in self.__dict__:
            if level == "DEBUG" and not self.settings["logging"]["debug"]:
                return False
            elif level == "WARNING" and not self.settings["logging"]["warning"]:
                return False

        time = datetime.now().strftime("[%x-%X]")

        print(
            f"{time} - {style.Italic}{fore.Bright_Red if level == 'ERROR' else fore.Bright_Blue if level == 'DEBUG' else fore.Bright_Yellow}[{level}]{style.RESET_ALL} | {text}"
        )

        if "log_file" not in self.__dict__:
            return False

        self.log_file.write(f"{time} - [{level}] | {text}\n")
        self.log_file.flush()

        if level == "ERROR":
            input(
                f"\n{style.Italic and style.Faint}Press ENTER to exit the program...{style.RESET_ALL}\n"
            )
            exit(1)
