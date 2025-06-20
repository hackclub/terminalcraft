from instance.client import Instance
from utils.console import style


def decode(Client: Instance, ciphertext: str, key: str) -> str:
    plaintext = []

    key = [
        char
        for char in key
        if char in Client.alphabets[0] or char in Client.alphabets[1]
    ]
    key_length = len(key)

    if len(ciphertext) != key_length:
        for index in range(len(ciphertext) - key_length):
            key.append(key[index % key_length])

    index = -1

    for char in ciphertext:
        index += 1

        if not char.isalpha():
            plaintext.append(char)
            index -= 1
            continue

        shift = Client.alphabets[0 if key[index].islower() else 1].index(
            key[index]
        ) - Client.alphabets[0 if char.islower() else 1].index(char)

        shift = abs(shift) if 0 > shift else -shift

        plaintext.append(Client.alphabets[0 if char.islower() else 1][shift])

    return "".join(plaintext)


def decode_bruteforce(Client: Instance, ciphertext: str) -> None:
    Client.clear()

    print(
        f"Press {style.Bold}Ctrl + C{style.RESET_ALL} ({style.Italic}KeyboardInterrupt{style.RESET_ALL}) at any time to stop the bruteforce process.\n"
    )

    try:
        for word in Client.words:
            Client.log("DEBUG", f"Attempting bruteforce with key {word}.")

            plaintext = decode(Client, ciphertext, word)

            probability = Client.sentence_probability(plaintext)

            Client.log(
                "DEBUG",
                f"{style.Bold}{probability}%{style.RESET_ALL} - {style.Italic}{plaintext}{style.RESET_ALL}\n",
            )

            if (
                probability
                > Client.settings["vigenere"]["bruteforce decode"]["pause percentage"]
            ):
                choice = input(
                    f"{style.Bold}Is this correct (Y/N): {style.RESET_ALL}{style.Italic}"
                ).lower()

                if choice == "y":
                    return

    except KeyboardInterrupt:
        return
