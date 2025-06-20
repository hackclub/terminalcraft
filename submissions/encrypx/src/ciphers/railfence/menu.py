from ciphers.railfence.decode import decode as railfence_decode
from ciphers.railfence.decode import decode_bruteforce as railfence_decode_bruteforce
from ciphers.railfence.encode import encode as railfence_encode
from instance.client import Instance
from utils.console import fore, style


def railfence(Client: Instance) -> None:
    while True:
        Client.clear()

        if Client.python_type == "CPython":
            print(
                f"""{fore.Blue}
██████╗░░█████╗░██╗██╗░░░░░███████╗███████╗███╗░░██╗░█████╗░███████╗
██╔══██╗██╔══██╗██║██║░░░░░██╔════╝██╔════╝████╗░██║██╔══██╗██╔════╝
██████╔╝███████║██║██║░░░░░█████╗░░█████╗░░██╔██╗██║██║░░╚═╝█████╗░░
{fore.Bright_Blue}██╔══██╗██╔══██║██║██║░░░░░██╔══╝░░██╔══╝░░██║╚████║██║░░██╗██╔══╝░░
██║░░██║██║░░██║██║███████╗██║░░░░░███████╗██║░╚███║╚█████╔╝███████╗
╚═╝░░╚═╝╚═╝░░╚═╝╚═╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚══╝░╚════╝░╚══════╝{style.RESET_ALL}\n"""
            )

        choice = input(
            f"{style.Bold + style.Underlined}Choose an option:{style.RESET_ALL}\n{style.Bold}1:{style.RESET_ALL} Encrypt\n{style.Bold}2:{style.RESET_ALL} Decrypt\n{style.Bold}3:{style.RESET_ALL} Decrypt (Brute Force)\n{style.Bold}4:{style.RESET_ALL} Return to main menu\n\n{style.Italic}>>>{style.RESET_ALL} "
        )

        Client.clear()

        if choice == "1":
            plaintext = Client.get_plaintext()

            key = Client.get_key()

            preserve_non_alpha = (
                True
                if input(
                    f"{style.Bold}Preserve non alpha characters (Y/N): {style.RESET_ALL}{style.Italic}"
                ).lower()
                == "y"
                else False
            )

            print(
                f"\n{style.RESET_ALL}The {style.Bold}encrypted{style.RESET_ALL} plaintext is: {style.Italic}{railfence_encode(Client, plaintext, key, preserve_non_alpha)}{style.RESET_ALL}"
            )
        elif choice == "2":
            ciphertext = Client.get_ciphertext()

            key = Client.get_key()

            print(
                f"\n{style.RESET_ALL}The {style.Bold}decrypted{style.RESET_ALL} ciphertext is: {style.Italic}{railfence_decode(Client, ciphertext, key)}{style.RESET_ALL}"
            )
        elif choice == "3":
            decodes = railfence_decode_bruteforce(Client, Client.get_ciphertext())

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
