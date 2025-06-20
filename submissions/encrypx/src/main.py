from os.path import dirname
from platform import system
from sys import argv

from ciphers.caeser.menu import caeser
from ciphers.railfence.menu import railfence
from ciphers.vigenere.menu import vigenere
from configuration.settings import settings
from configuration.words import words
from instance.client import Instance
from utils.console import fore, style

if system().lower() == "windows":
    from ctypes import windll

    kernel32 = windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

cwd = dirname(argv[0])

cwd = cwd if cwd == "" else f"{cwd}/"

Client = Instance(cwd)

Client.settings = settings(Client)

Client.words = words(Client)

Client.clear()

while True:
    if Client.python_type == "CPython":
        print(
            f"""{fore.Magenta}
███████╗███╗░░██╗░█████╗░██████╗░██╗░░░██╗██████╗░██╗░░██╗
██╔════╝████╗░██║██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚██╗██╔╝
█████╗░░██╔██╗██║██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░╚███╔╝░
{fore.Bright_Magenta}██╔══╝░░██║╚████║██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░██╔██╗░
███████╗██║░╚███║╚█████╔╝██║░░██║░░░██║░░░██║░░░░░██╔╝╚██╗
╚══════╝╚═╝░░╚══╝░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝{style.RESET_ALL}
"""
        )

    print(
        f"{style.Italic + style.Bold}INSTALLED VERSION: {style.RESET_ALL}{Client.version}\n"
    )

    choice = input(
        f"{style.Bold + style.Underlined}Choose an option:{style.RESET_ALL}\n{style.Bold}1:{style.RESET_ALL} Caeser Cipher.\n{style.Bold}2:{style.RESET_ALL} Railfence Cipher.\n{style.Bold}3:{style.RESET_ALL} Vigenère Cipher.\n\n{style.Italic}>>>{style.RESET_ALL} "
    )

    if choice == "1":
        caeser(Client)
    elif choice == "2":
        railfence(Client)
    elif choice == "3":
        vigenere(Client)

    Client.clear()
