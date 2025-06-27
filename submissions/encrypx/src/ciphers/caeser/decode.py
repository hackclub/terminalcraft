from instance.client import Instance


def decode(Client: Instance, ciphertext: str, key: int) -> str:
    key = -key

    shifted_alphabets = map(Client.shift, Client.alphabets, [key, key, key])
    joined_aphabets = "".join(Client.alphabets)
    joined_shifted_alphabets = "".join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)

    return ciphertext.translate(table)


def decode_bruteforce(Client: Instance, ciphertext: str) -> str:
    decodes = {}

    for key in range(1, 26):
        plaintext = decode(Client, ciphertext, key)

        probability = Client.sentence_probability(plaintext)

        if probability in decodes:
            decodes[probability].append(plaintext)
        else:
            decodes[probability] = [plaintext]

    return decodes
