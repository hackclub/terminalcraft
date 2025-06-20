from instance.client import Instance


def encode(Client: Instance, plaintext: str, key: str, preserve_non_alpha: bool) -> str:
    ciphertext = []

    key = [
        char
        for char in key
        if char in Client.alphabets[0] or char in Client.alphabets[1]
    ]
    key_length = len(key)

    if len(plaintext) != key_length:
        for index in range(len(plaintext) - key_length):
            key.append(key[index % key_length])

    index = -1

    for char in plaintext:
        index += 1

        if not char.isalpha():
            if preserve_non_alpha:
                ciphertext.append(char)

            index -= 1
            continue

        shift = Client.alphabets[0 if char.islower() else 1].index(
            char
        ) + Client.alphabets[0 if key[index].islower() else 1].index(key[index])

        shift = shift if shift < 26 else shift - 26

        ciphertext.append(Client.alphabets[0 if char.islower() else 1][shift])

    return "".join(ciphertext)
