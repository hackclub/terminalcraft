import configparser
import os
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from pyperclip import PyperclipException
from pyperclip import copy as clipboard_copy


class FetchProblemDetailsError(Exception):
    pass


def colorstr(text, color):
    return color + text + Style.RESET_ALL


def validate_url(url):
    try:
        result = urlparse(url)
        return result.hostname == "usaco.org" and result.path.startswith("/index.php")
    except ValueError:
        return False


def fetch_problem_details(url):
    # Fetch the page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        stdin_input = False

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Step 1: Find the div with class "panel" and extract the h2 tags (problem name)
        panel_div = soup.find("div", class_="panel")
        if panel_div:
            h2_tags = panel_div.find_all("h2")
            if len(h2_tags) >= 2:
                h2_text_1 = h2_tags[0].get_text(strip=True)
                h2_text_2 = h2_tags[1].get_text(strip=True)
                problem_name = f"{h2_text_1} {h2_text_2}"
            else:
                raise FetchProblemDetailsError("Error: Less than 2 h2 tags found inside the panel.")
        else:
            raise FetchProblemDetailsError("Error: No div with class 'panel' found.")

        # Step 2A: Find the div with class "prob-in-spec" and extract the first h4 (filename)
        problem_input_format_div = soup.find("div", class_="prob-in-spec")
        if problem_input_format_div:
            problem_input_filename_tag = problem_input_format_div.find("h4")
            if problem_input_filename_tag:
                problem_filename = problem_input_filename_tag.get_text(strip=True)

                # Step 2B: Use a regular expression to extract the FILENAME from the format "INPUT FORMAT (file FILENAME.in):"
                filename_match = re.search(r"file ([\w\d]+)\.in", problem_filename)
                if filename_match:
                    # Get the captured filename
                    filename = filename_match.group(1)
                else:
                    stdin_input = True
                    filename = problem_name.split(".")[-1].replace(" ", "").lower()
            else:
                raise FetchProblemDetailsError("Error: No h4 tag found inside 'prob-in-spec'.")
        else:
            raise FetchProblemDetailsError("Error: No div with class 'prob-in-spec' found.")

        # Step 3: Find the pre tag with class "in" and extract all the text (problem input)
        problem_input_tag = soup.find("pre", class_="in")
        if problem_input_tag:
            problem_input = problem_input_tag.get_text(strip=True)
        else:
            raise FetchProblemDetailsError("Error: No pre tag with class 'in' found.")

        # Return all gathered data
        return problem_name, filename, problem_input, stdin_input
    else:
        raise requests.HTTPError(f"Unable to fetch the page. Status code: {response.status_code}")


def ask_yes_no(prompt):
    while True:
        answer = input(f"{prompt} ({colorstr('y', Fore.GREEN)}/{colorstr('n', Fore.RED)}): ").strip().lower()
        if answer in ["y", "n"]:
            return answer == "y"


def clear_screen():
    if config.getboolean("Input", "clear_screen"):
        print("\033c\033[3J", end="")


def create_boilerplate_file(contest_name, contest_input, contest_link, filename, stdin_input):
    if config.getboolean("File Generator", "create_folder"):
        new_folder_path = os.path.join(script_directory, config["File Generator"]["problem_folder"], filename)
        os.makedirs(new_folder_path, exist_ok=True)
    else:
        new_folder_path = os.path.join(script_directory, config["File Generator"]["problem_folder"])

    # Define the full path to the boilerplate file
    boilerplate_file_path = os.path.join(new_folder_path, filename + ".py")
    input_file_path = os.path.join(new_folder_path, filename + ".in")

    # Define the boilerplate template
    boilerplate_name = (
        config["File Generator"]["stdin_boilerplate"] if stdin_input else config["File Generator"]["file_boilerplate"]
    )
    with open(os.path.join(script_directory, boilerplate_name), "r") as f:
        boilerplate = f.read()
    boilerplate = "\n".join(boilerplate.split("\n"))

    # Replace placeholders with actual inputs
    boilerplate = boilerplate.format(
        contest_name=contest_name,
        contest_link=contest_link,
        filename=filename,
    )

    # Write the modified boilerplate to the file in the new folder
    with open(boilerplate_file_path, "w") as f:
        f.write(boilerplate)
        print(colorstr(f"Boilerplate written to {boilerplate_file_path} successfully.", Fore.GREEN))

    # Write the problem input to the file in the new folder
    with open(input_file_path, "w") as f:
        f.write(contest_input)
        print(colorstr(f"Input written to {input_file_path} successfully.", Fore.GREEN))


if __name__ == "__main__":
    init()  # Initialize colorama

    script_directory = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_directory, "config.txt")
    if not os.path.isfile(config_path):
        print(
            colorstr(
                "Error: config.txt file not found in the current directory. Please create a config.txt file with the required settings.\nLearn more here: https://github.com/22yeets22/USACO-Boilerplate-Generator",
                Fore.RED,
            )
        )
        sys.exit()

    config = configparser.ConfigParser()
    config.read(config_path)

    # Get the problem link from the user
    url = input(colorstr("Enter the USACO problem URL: ", Fore.BLUE)).strip()

    if not validate_url(url):
        print(
            colorstr(
                "Invalid URL. Please enter a valid USACO problem URL.\nIt should be in the format: https://usaco.org/index.php?...",
                Fore.RED,
            )
        )
        sys.exit()

    print(colorstr("Now fetching details...", Fore.YELLOW))

    # Fetch and display the problem stuff
    try:
        problem_name, filename, problem_input, stdin_input = fetch_problem_details(url)
    except FetchProblemDetailsError as e:
        print(colorstr(f"An error occurred while fetching problem details:\n{e}", Fore.RED))
        sys.exit()

    clear_screen()

    print(colorstr("Problem name:", Fore.WHITE), problem_name)
    print(colorstr("URL:", Fore.WHITE), url)
    print(colorstr("Extracted filename:", Fore.WHITE), filename)
    print(
        colorstr(f"(Sample) Problem input coming from {'terminal' if stdin_input else 'file'}:\n", Fore.WHITE)
        + problem_input
    )

    if config.getboolean("Input", "confirm_details") and not ask_yes_no("Does this look correct?"):
        if not ask_yes_no("Is the problem name correct?"):
            if ask_yes_no("Do you want to enter the problem name manually?"):
                problem_name = input("Enter the problem name: ").strip()
            else:
                problem_name = "DEFAULT"
        if not ask_yes_no("Is the filename correct?"):
            if ask_yes_no("Do you want to enter the filename manually?"):
                filename = input("Enter the filename: ").strip()
            else:
                filename = "DEFAULT"
        if not ask_yes_no("Is the problem input correct?"):
            if ask_yes_no("Do you want to enter the problem input manually?"):
                problem_input = input("Enter the problem input: ").strip()
            else:
                problem_input = "DEFAULT"
        if not ask_yes_no("Is the terminal input section correct?"):
            stdin_input = ask_yes_no("Does the input come from terminal?")

    clear_screen()
    print(colorstr("Now creating boilerplate files...", Fore.YELLOW))

    # Automatically generate boilerplate files from reading the config
    try:
        create_boilerplate_file(problem_name, problem_input, url, filename, stdin_input)
    except Exception as e:
        print(colorstr(f"An error occurred while generating the boilerplate file:\n{e}", Fore.RED))
        sys.exit()

    print(colorstr("Successfully completed all operations!", Fore.GREEN))

    if config.getboolean("Input", "copy_commands"):
        cmds = config["File Generator"]["copy_command"].format(filename=filename)
        if ask_yes_no("Do you want to copy VSCode commands?"):
            try:
                clipboard_copy(cmds)
                print(colorstr(f"Successfully copied! Commands:\n{cmds}!", Fore.GREEN))
            except PyperclipException:
                print(
                    colorstr(
                        f"Clipboard copy failed. Ensure xclip/xsel is installed on Linux. Commands:\n{cmds}",
                        Fore.RED,
                    )
                )
        else:
            print(f"Commands:\n{cmds}")
