from instance.client import Instance


def encode(
    Client: Instance, plaintext: str, key: int, preserve_non_alpha: bool, row: int = 0
) -> str:
    if key == 1:
        return plaintext

    rail = [["" for _ in range(len(plaintext))] for _ in range(key)]
    ciphertext = []
    increasing = True

    index = -1

    for char in plaintext:
        index += 1

        if not char.isalpha() and not preserve_non_alpha:
            index -= 1
            continue

        rail[row][index] = char

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

    for row in rail:
        for char in row:
            if char != "":
                ciphertext.append(char)

    return "".join(ciphertext)
