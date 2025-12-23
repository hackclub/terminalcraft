from rich import print
from rich.panel import Panel
from rich.console import Console
import json
import sys
import questionary
import os
import time
import webbrowser
console = Console()
with open("ascii-text-art.txt", "r") as file:  
            ascii_art = file.read()
            print(ascii_art)

def return_back():
                                return_answer = questionary.text("would u like to return to main menu?? (y/n)").ask()
                                if return_answer == "y":
                                        options()
                                elif return_answer == "n":
                                        exit()
                                else:
                                        print("Wrong input...please try again!")
                                        return_answer = questionary.text("would u like to return to main menu?? (y/n)").ask()


def exit():
        print("[bold red]Closing the program in progress![/bold red]")
        time.sleep(1)
        sys.exit()
def login():
        print("Please enter you data to login")
        answer1 = questionary.text("Choose a username, please!!").ask()
        answer2 = questionary.password("Choose a Password, please!!").ask()
        
        user_data = {
                "username": answer1,
                "password": answer2,
        }
        with open("data.json", "r") as file:
                stored_data = json.load(file)
                if stored_data["username"] == user_data["username"] and stored_data["password"] == user_data["password"]:
                        console.print(Panel(f"[italic magenta]Welcome back, {user_data['username']}![/italic magenta]"))
                        options()
                elif stored_data["username"] != user_data["username"] and stored_data["password"] != user_data["password"]:
                        print("[bold red]Wrong username or password!![/bold red]")
                        enter()


def options():
        program_options = questionary.select(
    "Choose an option to start the program",
    choices=["Create directory", "access my files", "create new file", "store a code snippet", "execute a code", "reach some documentations"],
        ).ask()

        
        if program_options == "Create directory":
                folder_name = input("write the directory name")
                if os.path.exists(folder_name):
                        print("folder name exists...choose another one")
                        folder_name = input("write the directory name")
                else:
                        os.mkdir(folder_name)
                        print("[italic green]Horaayyyy, Folder created successfully![/italic green]")                        
                        return_back()
        elif program_options == "access my files":
                dir_list = os.listdir()
                print(dir_list)
                time.sleep(1)
                return_back()

        elif program_options == "create new file":
                file_name = input("write the file name")
                if os.path.exists(file_name):
                        print("file name exists...choose another one")
                        file
                        _name = input("write the directory name")
                else:
                        file_type = questionary.select(
    "Choose the file type",
    choices=["json", "txt"],
        ).ask()
                        if file_type == "json":
                                open(f"{file_name}.json", "w")
                        elif file_type == "txt":
                                open(f"{file_name}.txt", "w")

        elif program_options == "store a code snippet":
                code_snippet_text = []
                def code_snippet():
                        code_input = input("input your code")
                        code_snippet_text.append(code_input)
                        console.print(Panel("[bold green]code snippet created successfully! [/bold green]"))
                        with open("code.json", "w") as file:
                                json.dump(code_snippet_text, file)
                        if isinstance(file, list) and file:
                                last_item = file[-1].remove(",")
                code_snippet()
                restart_function = questionary.select("Would you like to save another code snippet??",
                                                                        choices = ["yes", "no"]).ask()
                if restart_function == "yes":
                        code_snippet()
                elif restart_function == "no":
                        options()
        elif program_options == "execute a code":
                console.print(Panel("[bold green]Welcome to the code execution section![/bold green]"))
                execution_options = questionary.select("Choose option 1 to access and choose code to execute from the file or choose option 2 to write a code snippet to execute!!!"
                                                , choices = ["option 1", "option 2"]).ask()
                if execution_options == "option 1":
                        with open("code.json", "r") as file:
                                stored_code = json.load(file)
                        selected_code = questionary.select("Choose a code snippet to execute!", 
                                                        choices = stored_code).ask()
                        exec(selected_code)
                        console.print(Panel("[bold green]Code executed successfully![/bold green]"))
                elif execution_options == "option 2":
                        code_snippet_text = input("please write your code here!")
                        exec(code_snippet_text)
                        console.print(Panel("[bold green]Code executed successfully![/bold green]"))
                time.sleep(1)
                return_back()
        elif program_options == "reach some documentations":
                doc_select = questionary.select("[bold green]choose a documentation to be forwarded to[/bold green]", 
                                                choices = ["git", "github"]).ask()
                if doc_select == "git":
                        url = "https://git-scm.com/"
                        webbrowser.open(url)
                        time.sleep(1)
                        return_back()
                elif doc_select == "github":
                        url = "https://github.com/"
                        webbrowser.open(url)
                        time.sleep(1)
                        return_back()


def enter():
        choice = questionary.select(
    "Choose an option to start",
    choices=["log in", "Sign up", "Exit"],
        ).ask()
                
        if choice == "log in":
                login()
        elif choice == "Sign up":
                answer1 = questionary.text("Choose a username, please!!").ask()
                answer2 = questionary.password("Choose a Password, please!!").ask()
        
                user_data = {
                        "username": answer1,
                        "password": answer2,
                }
                with open("data.json", "w") as file:
                        json.dump(user_data, file)
                login()
        elif choice == "Exit":
                exit()
enter()