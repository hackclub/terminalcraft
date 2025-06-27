from ciphers.caeser.decode import decode as caeser_decode
from ciphers.caeser.decode import decode_bruteforce as caeser_decode_bruteforce
from ciphers.caeser.encode import encode as caeser_encode
from instance.client import Instance
from utils.console import fore, style


def caeser(Client: Instance) -> None:
    while True:
        Client.clear()

        if Client.python_type == "CPython":
            print(
                f"""{fore.Red}
░█████╗░░█████╗░███████╗░██████╗███████╗██████╗░
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗
██║░░╚═╝███████║█████╗░░╚█████╗░█████╗░░██████╔╝
{fore.Bright_Red}██║░░██╗██╔══██║██╔══╝░░░╚═══██╗██╔══╝░░██╔══██╗
╚█████╔╝██║░░██║███████╗██████╔╝███████╗██║░░██║
░╚════╝░╚═╝░░╚═╝╚══════╝╚═════╝░╚══════╝╚═╝░░╚═╝{style.RESET_ALL}\n"""
            )

        choice = input(
            f"{style.Bold + style.Underlined}Choose an option:{style.RESET_ALL}\n{style.Bold}1:{style.RESET_ALL} Encrypt\n{style.Bold}2:{style.RESET_ALL} Decrypt\n{style.Bold}3:{style.RESET_ALL} Decrypt (Brute Force)\n{style.Bold}4:{style.RESET_ALL} Return to main menu\n\n{style.Italic}>>>{style.RESET_ALL} "
        )

        Client.clear()

        if choice == "1":
            plaintext = Client.get_plaintext()

            key = Client.get_key(limit_max=26)

            print(
                f"\n{style.RESET_ALL}The {style.Bold}encrypted{style.RESET_ALL} plaintext is: {style.Italic}{caeser_encode(Client, plaintext, key)}{style.RESET_ALL}"
            )
        elif choice == "2":
            ciphertext = Client.get_ciphertext()

            key = Client.get_key(limit_max=26)

            print(
                f"\n{style.RESET_ALL}The {style.Bold}decrypted{style.RESET_ALL} ciphertext is: {style.Italic}{caeser_decode(Client, ciphertext, key)}{style.RESET_ALL}"
            )
        elif choice == "3":
            decodes = caeser_decode_bruteforce(Client, Client.get_ciphertext())

            decodes_sorted = sorted(list(decodes), reverse=False)

            print("")

            for probability in decodes_sorted:
                for plaintext in decodes[probability]:
                    print(
                        f"{style.Bold}{probability}%{style.RESET_ALL} - {style.Italic}{plaintext}{style.RESET_ALL}"
                    )

        elif choice == "4":
            return

        input(
            f"\n{style.Italic and style.Faint}Press ENTER to continue...{style.RESET_ALL}\n"
        )
