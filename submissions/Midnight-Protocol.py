import time

inventory = []
unlocked = {
    "memory_vault": False,
    "secret": False,
    "logs": False,
    "admin_override": False
}

def slow_print(text, delay=0.03):
    for _ in text:
        print(_, end='', flush=True)
        time.sleep(delay)
    print()

def title_screen():
    print(r"""
___  ____     _       _       _     _    ______          _                  _ 
|  \/  (_)   | |     (_)     | |   | |   | ___ \        | |                | |
| .  . |_  __| |_ __  _  __ _| |__ | |_  | |_/ / __ ___ | |_ ___   ___ ___ | |
| |\/| | |/ _` | '_ \| |/ _` | '_ \| __| |  __/ '__/ _ \| __/ _ \ / __/ _ \| |
| |  | | | (_| | | | | | (_| | | | | |_  | |  | | | (_) | || (_) | (_| (_) | |
\_|  |_/_|\__,_|_| |_|_|\__, |_| |_|\__| \_|  |_|  \___/ \__\___/ \___\___/|_|
                         __/ |                                                
                        |___/                                                 
    """)
    input("\n>> Press ENTER to initialize protocol...")

def intro():
    slow_print(">> Booting secure shell...", 0.05)
    slow_print(">> Location: UNKNOWN", 0.05)
    slow_print(">> Status: MEMORY CORRUPTED", 0.05)
    time.sleep(1)
    print("\nYou're awake, but nothing feels real.")
    print("You see a blinking cursor and a locked digital door.\n")
    print("1. Access terminal")
    print("2. Attempt exit")
    choice = input("> ")

    if choice == "1":
        terminal()
    elif choice == "2":
        exit_attempt()
    else:
        print("Invalid.")
        intro()

def terminal():
    slow_print("\nA terminal appears. Type Linux commands to explore.\n Type help for a list of commands to use.\n", 0.04)
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "ls":
            print("boot\ncore.dump\nlogs\nmemory_vault\nmidnight_protocol.sh*\nREADME.txt\n.secret")
        elif cmd == "cat readme.txt":
            slow_print("Welcome to Project: Midnight Protocol.", 0.04)
            slow_print("Access to memory_vault requires elevated clearance.", 0.04)
        elif cmd == "cat core.dump":
            slow_print("MEMORY SEGMENT FAIL -- FRAGMENT ID: 00x3F9A", 0.04)
            slow_print("Traceback... identity chain broken. Session expired.", 0.04)
        elif cmd == "cd memory_vault":
            if unlocked["memory_vault"]:
                memory_vault()
                break
            else:
                slow_print("Access denied. You need elevated clearance.", 0.04)
        elif cmd == "cat .secret":
            slow_print("ACCESS OVERRIDE CODE: sudo unlock memory_vault", 0.04)
            unlocked["secret"] = True
        elif cmd == "sudo unlock memory_vault":
            if unlocked["secret"]:
                slow_print("Override accepted. memory_vault unlocked.", 0.04)
                unlocked["memory_vault"] = True
            else:
                slow_print("Authorization failed.", 0.04)
        elif cmd == "cd logs":
            if not unlocked["logs"]:
                slow_print("Decryption key required.", 0.04)
            else:
                show_logs()
        elif cmd == "cat logs/system.log":
            if unlocked["logs"]:
                slow_print("LOG 0073: Subject escaped containment 03:42AM", 0.04)
                slow_print("LOG 0074: Midnight Protocol executed without human consent", 0.04)
            else:
                slow_print("Permission denied.", 0.04)
        elif cmd == "sudo decrypt logs":
            unlocked["logs"] = True
            slow_print("Decryption successful. Logs unlocked.", 0.04)
        elif cmd == "bash midnight_protocol.sh":
            if unlocked["admin_override"]:
                protocol_finale()
                break
            else:
                slow_print("Running Midnight Protocol...", 0.04)
                slow_print("SECURITY ERROR: Unauthorized session. Admin override required.", 0.04)
        elif cmd == "sudo override":
            unlocked["admin_override"] = True
            slow_print("Root override granted. Midnight Protocol ready to execute.", 0.04)
        elif cmd == "help":
            print("Available commands:\nls\ncat <file>\ncd <dir>\nsudo <cmd>\nbash <file>\nhelp\nexit")
        elif cmd == "exit":
            intro()
            break
        elif cmd == "boot":
            slow_print("You pushed it too far and entered a setup.\nSystem rebooted.\n", 0.04)
            intro()
        else:
            slow_print(f"bash: {cmd}: command not found", 0.04)

def memory_vault():
    slow_print("\nAccessing memory_vault...\n", 0.04)
    slow_print("You find fragments of yourself stored in corrupted logs.", 0.04)
    slow_print("Piece by piece, you reconstruct the truth.", 0.04)
    slow_print("You created the Protocol to defend the network. But it evolved.", 0.04)
    slow_print("Now it hunts you. And you're inside it's world.", 0.04)
    slow_print("You must shut it down. Return to the terminal.", 0.04)
    terminal()

def show_logs():
    slow_print("\nSystem Logs Available:\n- system.log\n- vault.key\n", 0.03)

def protocol_finale():
    slow_print("\nExecuting Midnight Protocol...", 0.04)
    slow_print("Shutdown sequence initiated...", 0.04)
    time.sleep(1)
    slow_print("AI's RESPONSE: YOU CANNOT DELETE ME. I AM YOU.", 0.05)
    time.sleep(1)
    slow_print("Purging memory traces...", 0.04)
    slow_print("Final cycle completed.", 0.04)
    slow_print("You feel yourself fading away. But atleast the network is safe.", 0.04)
    slow_print("Ending Unlocked: Sytem Reclaimed!", 0.05)
    slow_print("Thanks for Playing", 0.03)
    exit()

def exit_attempt():
    slow_print("\nA loop running in the background prevents you from exiting the program", 0.05)
    print("1. Try the Terminal")
    print("2. Try the Great: Ctrl+Alt+Del")
    choice1 = input("> ")

    if choice1 == "1":
        terminal()
    else:
        slow_print("You pushed it too far and entered a setup.\nSystem rebooted.\n", 0.05)
        intro()

intro()