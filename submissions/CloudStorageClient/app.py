import sys
import json

from Data.scripts.encoding import encode
from Data.scripts.decoding import decode
from Data.scripts.clear_terminal import clear_terminal
from Data.scripts.help import help
from Data.scripts.setup import open_urls, guide_user

def main():
    while True:
        clear_terminal()
        inp = str(input("Encode/Decode/Help (1/2/3/Exit): "))

        if int(inp) == 1:
            encode()
        elif int(inp) == 2:
            decode()
        elif int(inp) == 3:
            help()
        else:
            sys.exit(0)

if __name__ == "__main__":
    with open("Data/client_secret.json", "r") as file:
        try:
            config = json.load(file)
            l = len(config["installed"]["client_id"])

            if l == 0:
                open_urls()
                guide_user()
        except:
            open_urls()
            guide_user()
    clear_terminal()
    main()