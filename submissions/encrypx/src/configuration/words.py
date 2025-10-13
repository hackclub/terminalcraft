from instance.client import Instance
from utils.requests import request


def words(Client: Instance) -> dict:
    Client.log("DEBUG", "Loading words file.")

    try:
        with open(f"{Client.cwd}database/words", "r") as f:
            Client.log("DEBUG", "Parsed words.")

            return [line.strip() for line in f.read().split("\n")]
    except FileNotFoundError:
        Client.log("WARNING", "Words file was not found. Downloading new file.")

        return words_fixer(Client)


def words_fixer(Client: Instance) -> bool:
    req = request(
        Client,
        "https://raw.githubusercontent.com/skifli/Encrypx/main/src/database/words",
    )

    if not 199 < req.status_code < 300:
        Client.log(
            "ERROR",
            f"An error occured when getting the words file. Status code: {req.status_code}. Content: {req.content}.",
        )

    words = req.content

    with open(f"{Client.cwd}database/words", "w") as f:
        f.write(words)

    return words
