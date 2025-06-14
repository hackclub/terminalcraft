import os, configparser, sys, threading, time, subprocess, urllib.request, random, base64, hashlib, string
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from colorama import init

try:
    from cryptography.fernet import Fernet
    from termcolor import colored
except Exception:
    print("Please run requirements.py first", "yellow")
    sys.exit()

operatingsys = sys.platform

if operatingsys == "win32":
    from colorama import just_fix_windows_console

    just_fix_windows_console()
init()

configfile = "settings.ini"
config = configparser.ConfigParser()
bughuntconfigfile = "bughunt.ini"
bughuntconfig = configparser.ConfigParser()
t = None
tt = None
running202020 = False
runninganimation = False
autoclear = False

try:
    config.read(configfile)
    if not config.sections():
        print(
            colored(
                "The settings file is empty or formatted incorrectly! Adding default values...",
                "yellow",
            )
        )
        config["General"] = {"termcolor": "white", "termname": "Type termname"}
        config.add_section("Shortcuts")
        with open(configfile, "w") as file:
            config.write(file)
except FileNotFoundError:
    print(
        colored("The settings file does not exist! A new one will be created.", "red")
    )
    config["General"] = {"termcolor": "white", "termname": "Type termname"}
    with open(configfile, "w") as file:
        config.write(file)
except Exception as e:
    print(colored(f"An error occurred: {e}", "red"))
    sys.exit(1)

os.system("@echo off && cls" if operatingsys == "win32" else "clear")

termcolor = config["General"]["termcolor"]

if operatingsys == "win32":
    os.system(f"title {config['General']['termname']}")
elif operatingsys == "linux":
    os.system(f'echo -ne "{config["General"]["termname"]}"')
elif operatingsys == "darwin":
    os.system(
        f'osascript -e \'tell application "Terminal" to set custom title of window 1 to "{config["General"]["termname"]}"\''
    )


class bughunt:
    def start(self):
        try:
            bughuntconfig.read(bughuntconfigfile)
            if not bughuntconfig.sections():
                print(
                    colored(
                        "The settings file is empty or formatted incorrectly! Adding default values...",
                        "yellow",
                    )
                )
                bughuntconfig["General"] = {"level": "1"}
                with open(bughuntconfigfile, "w") as file:
                    bughuntconfig.write(file)
        except FileNotFoundError:
            print(
                colored(
                    "The settings file does not exist! A new one will be created.",
                    "red",
                )
            )
            bughuntconfig["General"] = {"level": "1"}
            with open(bughuntconfigfile, "w") as file:
                bughuntconfig.write(file)
        except Exception as e:
            print(colored(f"An error occurred: {e}", "red"))
            self.getinput()
            return
        os.system("cls" if operatingsys == "win32" else "clear")
        print(
            colored(
                "Welcome to bughunt! 🪰\n\nHere you will be given code and asked to find out what is wrong.\n"
                "If you figure it out correctly, you complete the level!\n\nType 'help' to get familiar to the commands!\n\n",
                termcolor,
            )
        )
        self.getinput()

    def getinput(self):
        try:
            input1 = (
                input("\033[0;37mbughunt>>> ")
                .replace(" ", "_")
                .replace("-", "_")
                .lower()
            )
            if hasattr(self, input1) and callable(getattr(self, input1)):
                getattr(self, input1)()
            else:
                print(
                    colored(
                        f"'{input1}' is not a valid command, use help for a list of commands",
                        "red",
                        attrs=["bold", "underline"],
                    )
                )
                self.getinput()
        except Exception as e:
            print(colored("Error: " + str(e), "red"))
            self.getinput()

    def enter(self):
        level = input(
            colored(
                "Which level would you like to try?\n\033[0;37mbughunt>>> ", termcolor
            )
        ).capitalize()
        if level.lower() == "exit":
            self.getinput()
            return
        if level in bughuntconfig:
            answerkeywords = [
                kw.strip()
                for kw in bughuntconfig[level].get("answerkeywords", "").split(",")
            ]
            code = (
                bughuntconfig[level]
                .get("code", "")
                .replace("\\n", "\n")
                .replace("<tab>", "    ")
            )
            print(colored(code, termcolor))

            def hint():
                print(
                    colored(
                        "Hint:\n"
                        + bughuntconfig[level].get("hint", "No hint available."),
                        termcolor,
                    )
                )
                getsolve()

            def getsolve():
                solve = input(
                    colored("\nYour guess\n\033[0;37mbughunt>>> ", termcolor)
                ).lower()
                if solve == "hint":
                    hint()
                elif any(word in answerkeywords for word in solve.split()):
                    print(
                        colored(
                            "That's right! Explanation:\n"
                            + bughuntconfig[level].get(
                                "explanation", "No explanation."
                            ),
                            termcolor,
                        )
                    )
                    self.getinput()
                elif solve == "exit":
                    print(colored("Exiting.", termcolor))
                    self.getinput()
                elif solve == "code":
                    print(colored(code, termcolor))
                else:
                    print(
                        colored(
                            "That isn't quite right, keep trying. Use 'hint' for a hint.",
                            termcolor,
                        )
                    )
                    getsolve()

            getsolve()
        else:
            print(
                colored(
                    "That level is not available! Please choose another available level.",
                    "red",
                )
            )
            self.enter()

    def list_levels(self):
        levels = [
            section
            for section in bughuntconfig.sections()
            if section.lower().startswith("level")
        ]
        if levels:
            print(colored("Available levels:\n", termcolor))
            for level in levels:
                print(
                    colored(
                        f"• {level} - {bughuntconfig[level]['language'].capitalize()}",
                        termcolor,
                    )
                )
            print("\n")
        else:
            print(colored("No levels found.", "red"))
        self.getinput()

    def help(self):
        print(
            colored(
                "\nAvailable Commands:\n"
                "  list levels   - View all available challenge levels\n"
                "  enter         - Start or retry a specific level\n"
                "  clear         - Clear the screen\n"
                "  help          - Show this help message\n"
                "  exit          - Exit the game\n",
                termcolor,
            )
        )

        print(
            colored(
                "\nWhile Playing a Level:\n"
                "  Type your answer and press Enter to submit it.\n"
                "  Type 'hint'   - Get a clue if you're stuck\n"
                "  Type 'exit'   - Return to the main menu\n",
                termcolor,
            )
        )

        self.getinput()

    def exit(self):
        os.system("cls" if operatingsys == "win32" else "clear")
        getinput()

    def code(self):
        print("You can only use 'code' after you are inside a bughunt.")
        self.getinput()

    def hint(self):
        print("You can only use 'hint' after you are inside a bughunt.")
        self.getinput()

    def clear(self):
        os.system("cls" if operatingsys == "win32" else "clear")
        self.getinput()


def help():
    commands = {
        "General": {
            "help": "Displays this help message.",
            "color": "Changes the terminal's text color.",
            "clear": "Clears all text from the terminal screen.",
            "exit": "Exits the application.",
        },
        "Utilities": {
            "termname": "Changes the title of the terminal window.",
            "animatetermname": "Toggles a typing animation for the terminal title.",
            "generatepassword": "Generates a secure, random password.",
            "speedtest": "Measures your internet download speed.",
            "cleanup": "Deletes temporary files to free up space.",
        },
        "Health & Productivity": {
            "start 20-20-20": "Starts a 20-minute timer to remind you to rest your eyes.",
            "stop 20-20-20": "Stops the 20-20-20 timer.",
            "autoclear": "Toggles clearing the screen before each input. (Very buggy!)",
        },
        "Shortcuts": {
            "shortcut list": "Displays all saved application/file shortcuts.",
            "shortcut create": "Creates a new shortcut.",
            "shortcut delete": "Removes an existing shortcut.",
        },
        "Fun & Games": {
            "bughunt": "Starts the 'Bughunt' code-debugging game.",
            "hackermode": "Launches a simulated 'hacker' interface.",
        },
    }

    print(colored("Commands:", termcolor, attrs=["bold", "underline"]))

    for category, cmds in commands.items():
        print(colored(f"\n--- {category} ---", termcolor, attrs=["bold"]))
        max_len = max(len(cmd) for cmd in cmds)
        for command, description in cmds.items():
            padding = " " * (max_len - len(command))
            print(
                colored(f"  {command}{padding} : ", "yellow")
                + colored(description, termcolor)
            )

    print(
        colored(
            "\nNote: Most commands with spaces can also be used with hyphens (-) or underscores (_).",
            "grey",
        )
    )
    getinput()


def termcolorchange():
    global termcolor
    termcolorinput = input(colored("Type a color\n\033[0;37m>>> ", termcolor)).lower()
    try:
        colored(None, termcolorinput)
        config["General"]["termcolor"] = termcolorinput
        termcolor = termcolorinput
        with open(configfile, "w") as file:
            config.write(file)
        print(colored("Color changed", termcolor))
    except KeyError:
        print(colored("That color option is not available\n"))
        termcolorchange()
        return
    getinput()


def speedtest():
    try:
        serverlist = list(
            {
                "https://freetestdata.com/wp-content/uploads/2022/11/Free_Test_Data_10.5MB_PDF.pdf",
                "https://examplefile.com/file-download/24",
                "https://file-examples.com/wp-content/storage/2017/04/file_example_MP4_640_3MG.mp4",
                "https://file-examples.com/wp-content/storage/2017/04/file_example_MP4_1920_18MG.mp4",
                "https://examplefile.com/file-download/203",
                "https://filesamples.com/samples/video/mp4/sample_3840x2160.mp4",
                "https://getsamplefiles.com/download/gif/sample-1.gif",
            }
        )
        server = input(
            colored(
                "Choose a server to download from (all file sizes are estimates, bigger files will take longer):\n1. https://freetestdata.com/wp-content/uploads/2022/11/Free_Test_Data_10.5MB_PDF.pdf (10 MB PDF)\n2. https://examplefile.com/file-download/24 (10 MB TXT)\n3. https://file-examples.com/wp-content/storage/2017/04/file_example_MP4_640_3MG.mp4 (3 MB MP4)\n4. https://file-examples.com/wp-content/storage/2017/04/file_example_MP4_1920_18MG.mp4 (18 MB MP4)\n5. https://examplefile.com/file-download/203 (500 MB TXT)\n6. https://filesamples.com/samples/video/mp4/sample_3840x2160.mp4 (126 MB MP4)\n7. https://getsamplefiles.com/download/gif/sample-1.gif (625 KB GIF)\n8. Custom\n\033[0;37m>>> ",
                termcolor,
            )
        )
        if server.isdigit() and 0 < int(server) < 9:
            if server != "8":
                server = serverlist[int(server) - 1]
            else:
                server = input(
                    colored("Type your server URL\n\033[0;37m>>> ", termcolor)
                )
        else:
            print(colored("Please type a number between 1-8\n", "red"))
            speedtest()
            return
        print(colored("Running speedtest...", termcolor))
        response = urllib.request.urlopen(server)
        total_bytes = 0
        chunk_size = 1024
        first_chunk = response.read(chunk_size)
        if not first_chunk:
            print(colored("No data received", "red"))
            return

        start_time = time.time()
        total_bytes += len(first_chunk)

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
        end_time = time.time()

        file_size_mb = total_bytes / 1000000
        duration = end_time - start_time
        download_speed = file_size_mb / duration

        print("\n===== Speed Test Results =====")
        print(f"Downloaded: {file_size_mb:.3f} MB in {duration:.3f} seconds")
        print(f"Download Speed: {download_speed:.3f} Mbps\n")
    except Exception as e:
        print(colored("Error: " + str(e), "red"))
    getinput()


def start_20_20_20_rule():
    global running202020
    while running202020:
        seconds = 0
        while running202020 and seconds < 1201:
            time.sleep(1)
            seconds += 1
        if operatingsys == "win32" and running202020:
            os.system(
                'start cmd /k "@echo off && title 20-20-20 Rule Reminder &&echo You have been staring at this screen for twenty minutes, rest your eyes for 20 seconds staring 20 feet away"'
            )
        elif operatingsys == "linux" and running202020:
            for term in ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"]:
                try:
                    subprocess.Popen(
                        [
                            term,
                            "-e",
                            "bash -c 'echo You have been staring at this screen for twenty minutes, rest your eyes for 20 seconds staring 20 feet away;echo -ne '\\033]0;20-20-20 Rule Reminder\\007'; exec bash'",
                        ]
                    )
                    break
                except FileNotFoundError:
                    continue
        elif operatingsys == "darwin" and running202020:
            try:
                subprocess.Popen(
                    [
                        "osascript",
                        "-e",
                        'display notification "You have been staring at this screen for twenty minutes. Rest your eyes for 20 seconds staring 20 feet away." with title "20-20-20 Rule Reminder"',
                    ]
                )
            except FileNotFoundError:
                print(
                    colored(
                        "AppleScript execution failed. Ensure 'osascript' is available.",
                        "red",
                    )
                )


def shortcut_list():
    if "Shortcuts" not in config or not config["Shortcuts"]:
        print(colored("No shortcuts found.", termcolor))
    else:
        for shortcut in config["Shortcuts"]:
            print(colored(f"{shortcut} -> {config['Shortcuts'][shortcut]}", termcolor))


def shortcut_create():
    try:
        shortname = input(
            colored(
                "What would you like the shortcut to be called by? (Naming to an existing shortcut will overwrite it, use shortcut list for a list of all shortcuts)\n\033[0;37m>>> ",
                termcolor,
            )
        )
        if (
            shortname.replace(" ", "_").replace("-", "_").lower() in globals()
            and callable(
                globals()[shortname.replace(" ", "_").replace("-", "_").lower()]
            )
            or shortname.lower() == "color"
        ):
            print(
                colored(
                    shortname
                    + "' is the name of a command, please choose a different name\n",
                    termcolor,
                )
            )
            shortcut_create()
        print(
            colored(
                "What is the path of the shortcut?\nUse the file selection dialog.",
                termcolor,
            )
        )
        Tk().withdraw()
        shortpath = askopenfilename()
        config["Shortcuts"][shortname] = shortpath
        with open("settings.ini", "w") as f:
            config.write(f)
        print(colored("Succesfully created shortcut.", termcolor))
    except Exception as e:
        print(colored("Error: " + str(e), "red"))
    getinput()


def shortcut_delete():
    try:
        if "Shortcuts" not in config or not config["Shortcuts"]:
            print(colored("No shortcuts found.", termcolor))
        else:
            print("\n")
            for shortcut in config["Shortcuts"]:
                print(
                    colored(f"{shortcut} -> {config['Shortcuts'][shortcut]}", termcolor)
                )
        shortdel = input(
            colored(
                "\nWhich shortcut would you like to remove? (Type shortcut name)\n\033[0;37m>>> ",
                termcolor,
            )
        )
        if config["Shortcuts"][shortdel]:
            config.remove_option("Shortcuts", shortdel)
        with open("settings.ini", "w") as f:
            config.write(f)
        print(colored("Succesfully deleted shortcut.", termcolor))
    except Exception as e:
        print(colored("Error: " + str(e), "red"))
    getinput()


def exit():
    with open("settings.ini", "w") as f:
        config.write(f)
    sys.exit()


def generatepassword():
    passlength = input(
        colored(
            "How many characters should the password be?\n\033[0;37m>>> ", termcolor
        )
    )
    if passlength.isdigit() and 0 < int(passlength) < 129:
        length = int(passlength)
        charset = list(string.ascii_letters + string.digits + string.punctuation)
        random.shuffle(charset)
        password = "".join(random.choice(charset) for _ in range(length))
        print(colored("The generated password is: " + password, termcolor))
    else:
        print(colored("Please type a number between 1-128\n", "red"))
        generatepassword()
        return
    getinput()


def termname():
    print(colored("Type a name for this terminal", termcolor))
    termnameinput = input("\033[0;37m>>> ")
    if operatingsys == "win32":
        os.system(f"title {termnameinput}")
    elif operatingsys == "linux":
        os.system(f'echo -ne "\\033]0;{termnameinput}\\007"')
    elif operatingsys == "darwin":
        os.system(
            f'osascript -e \'tell application "Terminal" to set custom title of window 1 to "{termnameinput}"\''
        )
    config["General"]["termname"] = termnameinput
    with open(configfile, "w") as file:
        config.write(file)
    getinput()


def cleanup():
    if operatingsys == "win32":
        os.system('del /s /q "%temp%\\*.*"')
        os.system('for /d %G in ("%temp%\\*") do rd /s /q "%G"')
    elif operatingsys == "linux":
        os.system("rm -rf /tmp/*")
    elif operatingsys == "darwin":
        os.system("rm -rf /private/tmp/* /var/tmp/*")
    getinput()


def hackermode():
    try:
        if operatingsys != "win32":
            print(
                colored(
                    f"Press {'cmd' if operatingsys == 'darwin' else 'ctrl'}+c to stop at anytime"
                )
            )
            time.sleep(5)
            os.system("ls -R /")
        else:
            os.system(
                f'echo {colored("Press ctrl+c to stop at anytime", termcolor)} && pause && color a && for /L %i in (1,1,10) do tree C:/'
            )
    except KeyboardInterrupt:
        print("\n\n")
    getinput()


def titlethread():
    global runninganimation
    termname = config["General"]["termname"]
    while runninganimation:
        title = ""
        for x in termname:
            title += x
            if operatingsys == "win32" and runninganimation:
                os.system(f"title {title}")
            elif operatingsys == "linux" and runninganimation:
                os.system(f'echo -ne "\\033]0;{title}\\007"')
            elif operatingsys == "darwin" and runninganimation:
                os.system(
                    f'osascript -e \'tell application "Terminal" to set custom title of window 1 to "{title}"\''
                )
            time.sleep(0.05)

        for i in range(len(termname), 0, -1):
            title = termname[: i - 1]
            if operatingsys == "win32" and runninganimation:
                os.system(f"title {title}")
            elif operatingsys == "linux" and runninganimation:
                os.system(f'echo -ne "\\033]0;{title}\\007"')
            elif operatingsys == "darwin" and runninganimation:
                os.system(
                    f'osascript -e \'tell application "Terminal" to set custom title of window 1 to "{title}"\''
                )
            time.sleep(0.05)


def animatetermname():
    global runninganimation
    global tt
    runninganimation = not runninganimation
    if runninganimation:
        tt = threading.Thread(target=titlethread)
        tt.start()
    else:
        tt.join()
        termname = config["General"]["termname"]
        if operatingsys == "win32":
            os.system(f"title {termname}")
        elif operatingsys == "linux":
            os.system(f'echo -ne "\\033]0;{termname}\\007"')
        elif operatingsys == "darwin":
            os.system(
                f'osascript -e \'tell application "Terminal" to set custom title of window 1 to "{termname}"\''
            )
    getinput()


def clear():
    os.system("cls" if operatingsys == "win32" else "clear")
    getinput()


def getinput():
    try:
        global running202020, t, autoclear
        if autoclear:
            os.system("cls" if operatingsys == "win32" else "clear")
        input1 = input("\033[0;37m>>> ").replace(" ", "_").replace("-", "_").lower()
        if input1 in globals() and callable(globals()[input1]):
            if input1 == "bughunt":
                bughunt().start()
            else:
                globals()[input1]()
        elif input1 == "color":
            termcolorchange()
        elif input1 == "start_20_20_20":
            if not running202020:
                running202020 = True
                t = threading.Thread(target=start_20_20_20_rule)
                t.start()
                print(
                    colored(
                        "20-20-20 rule timer started, use stop 20-20-20 to stop timer",
                        termcolor,
                    )
                )
            else:
                print(colored("The 20-20-20 rule timer is already running", "yellow"))
        elif input1 == "stop_20_20_20":
            if running202020:
                running202020 = False
                t.join()
                print(colored("The 20-20-20 rule timer has stopped", termcolor))
            else:
                print(colored("The 20-20-20 rule timer is not running", "yellow"))
        elif input1 == "autoclear":
            autoclear = not autoclear
            os.system("cls" if operatingsys == "win32" else "clear")
            print(
                colored(
                    f"Auto clear is turned {'on' if autoclear else 'off'}", termcolor
                )
            )
            if autoclear:
                print(colored("Autoclear is VERY buggy!", "yellow"))
            time.sleep(3)
            getinput()
        elif config["Shortcuts"][input1]:
            if operatingsys == "win32":
                os.startfile(config["Shortcuts"][input1])
            elif operatingsys == "linux":
                subprocess.Popen(["xdg-open", config["Shortcuts"][input1]])
            elif operatingsys == "darwin":
                subprocess.Popen(["open", config["Shortcuts"][input1]])
        else:
            print(
                colored(
                    f"'{input1}' is not a valid command, use help for a list of commands",
                    "red",
                    attrs=["bold", "underline"],
                )
            )
            getinput()
    except Exception as e:
        print(colored("Error: " + str(e), "red"))
    getinput()


if __name__ == "__main__":
    getinput()

