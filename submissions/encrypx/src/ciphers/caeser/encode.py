from instance.client import Instance


def encode(Client: Instance, plaintext: str, key: int) -> str:
    shifted_alphabets = map(Client.shift, Client.alphabets, [key, key, key])
    joined_aphabets = "".join(Client.alphabets)
    joined_shifted_alphabets = "".join(shifted_alphabets)
    table = str.maketrans(joined_aphabets, joined_shifted_alphabets)

    return plaintext.translate(table)
