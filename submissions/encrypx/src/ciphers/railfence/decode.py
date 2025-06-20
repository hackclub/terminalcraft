from instance.client import Instance


def decode(Client: Instance, ciphertext: str, key: int, row: int = 0) -> str:
    if key == 1:
        return ciphertext

    old_row = row
    rail = [["" for _ in range(len(ciphertext))] for _ in range(key)]

    plaintext = []
    increasing = True

    for index in range(len(ciphertext)):
        rail[row][index] = "*"

        if increasing:
            if row == key - 1:
                increasing = False
                row -= 1
            else:
                row += 1
        else:
            if row - 1 == -1:
                increasing = True
                row += 1
            else:
                row -= 1

    index = 0

    for index2 in range(key):
        for index3 in range(len(ciphertext)):
            if rail[index2][index3] == "*" and index < len(ciphertext):
                rail[index2][index3] = ciphertext[index]
                index += 1

    increasing = True
    row = old_row

    for index in range(len(ciphertext)):
        plaintext.append(rail[row][index])

        if increasing:
            if row == key - 1:
                increasing = False
                row -= 1
            else:
                row += 1
        else:
            if row - 1 == -1:
                increasing = True
                row += 1
            else:
                row -= 1

    return "".join(plaintext)


def decode_bruteforce(Client: Instance, ciphertext: str, row: int = 0) -> str:
    decodes = {}

    for key in range(2, len(ciphertext) - 1):
        plaintext = decode(Client, ciphertext, key, row)

        probability = Client.sentence_probability(plaintext)

        if probability in decodes:
            decodes[probability].append(plaintext)
        else:
            decodes[probability] = [plaintext]

    return decodes
