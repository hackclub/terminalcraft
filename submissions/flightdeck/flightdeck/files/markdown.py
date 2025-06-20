import colorama
from colorama import Fore, Back, Style

def print_markdown_fancy(file):
    colorama.init(autoreset=False)

    with open(file, "r") as f:
        lines = list(f.readlines())

    code = False

    for line in lines:
        line = line.replace("\n", "")
        if line.startswith("# "):
            print(f"{Style.BRIGHT + Fore.WHITE}┌─{len(line[2:]) * '─'}───┐")
            print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "| " + line + " |")
            print(f"{Style.BRIGHT + Fore.WHITE}└─{len(line[2:]) * '─'}───┘")
        elif line.startswith("## "):
            print(Style.RESET_ALL + Back.YELLOW + Fore.WHITE + line + "" + Style.RESET_ALL)
        elif line.startswith("### "):
            print(Style.RESET_ALL + Back.GREEN + line + "" + Style.RESET_ALL)
        elif line.startswith("#### "):
            print(Style.RESET_ALL + Back.BLUE + line + "" + Style.RESET_ALL)
        elif line.startswith("---"):
            print(Style.RESET_ALL + Fore.WHITE + Style.DIM + "──────" + Style.RESET_ALL)
        elif line.startswith("```"):
            if not code:
                print(Style.RESET_ALL + Back.LIGHTBLACK_EX + Fore.WHITE + Style.BRIGHT)
                code = True
            else:
                code = False
        elif not code:
            print(Style.RESET_ALL + Fore.WHITE + Style.RESET_ALL)
            print(Style.RESET_ALL + Fore.WHITE + line + Style.RESET_ALL)
        else:
            print(line)

if __name__ == "__main__":
    print_markdown_fancy("test.md")
