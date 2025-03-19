import requests
import json
import sys
import time
import threading
import argparse
import subprocess
import os
import concurrent.futures
from multiprocessing import Process
from datetime import datetime, timedelta

from termcolor import colored
from rich.console import Console
from rich.spinner import Spinner
import pyttsx3

# Initialize the console for beautiful output
console = Console()

# Attempt to initialize text-to-speech engine
try:
    engine = pyttsx3.init()
except Exception as e:
    engine = None
    console.print(f"[red]Failed to initialize TTS engine:[/red] {e}")

# Fallback speak function: if TTS fails, use macOS 'say' command.
def speak(text):
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    elif sys.platform == "darwin":
        subprocess.run(["say", text])
    else:
        console.print(f"TTS (fallback): {text}", style="italic")

# Super cute loading animation
def super_cute_loading_animation():
    symbols = [
        "🌟 (✿◕‿◕) 🌟",
        "💖 (｡♥‿♥｡) 💖",
        "✨ ~(˘▾˘~) ✨",
        "💫 (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ 💫",
        "🐱 (=ↀωↀ=) 🐱"
    ]
    for _ in range(5):  # Repeat the sequence 5 times
        for symbol in symbols:
            sys.stdout.write(f'\r{colored("Thinking...", "cyan")} {colored(symbol, "magenta", attrs=["bold"])}')
            sys.stdout.flush()
            time.sleep(0.3)

# Function to send the question to the AI API
def ask_question(question):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {"messages": [{"role": "user", "content": question}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        if response.status_code == 200:
            answer = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No answer')
            return answer
        else:
            return "Error: Unable to get a response."
    except requests.RequestException as e:
        return f"Error: {str(e)}"

# Function to open a software application
def open_software(software_name):
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "-a", software_name])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", software_name])
        elif sys.platform == "win32":
            os.startfile(software_name)
        else:
            console.print(f"Unsupported platform: {sys.platform}", style="red")
    except Exception as e:
        console.print(f"Error opening software: {e}", style="red")

# Function to set a device alarm on macOS by adding a reminder via AppleScript.
def set_device_alarm(alarm_time_str):
    try:
        # Expect alarm_time_str in "HH:MM" (24-hour format)
        now = datetime.now()
        alarm_time = datetime.strptime(alarm_time_str, "%H:%M").time()
        alarm_datetime = datetime.combine(now.date(), alarm_time)
        # If the alarm time has already passed today, schedule it for tomorrow.
        if alarm_datetime <= now:
            alarm_datetime += timedelta(days=1)
        # Format the date in MM/DD/YYYY hh:mm:ss AM/PM format (without 'at')
        alarm_date_str = alarm_datetime.strftime("%m/%d/%Y %I:%M:%S %p")
        applescript = f'''
        tell application "Reminders"
            set newReminder to make new reminder with properties {{name:"Alarm: It's time to wake up!", remind me date:(date "{alarm_date_str}")}}
        end tell
        '''
        subprocess.run(["osascript", "-e", applescript])
        console.print(f"Alarm set for {alarm_time_str} (at {alarm_date_str}).", style="green")
        speak(f"Alarm set for {alarm_time_str}.")
    except Exception as e:
        console.print(f"Error setting device alarm: {e}", style="red")

# Function to run an interactive AI session
def run_ai():
    console.print("\n💖✨ [bold cyan]Welcome to the Cutest AI Chat Terminal![/bold cyan] ✨💖")
    console.print(colored("Ready to answer your magical questions. Type 'exit' to quit.", "magenta"))
    question = input("\n✨💖 What's your magical question? 💖✨: ")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_anim = executor.submit(super_cute_loading_animation)
        answer = ask_question(question)
        try:
            future_anim.result(timeout=1)
        except concurrent.futures.TimeoutError:
            pass
    console.print(f"\r{colored('Answer is ready!', 'green')} [bold magenta]{answer}[/bold magenta]\n")
    console.print(f"\n🌸💖✨ [bold magenta]Your Magical Answer:[/bold magenta] [bold yellow]{answer}[/bold yellow] ✨💖🌸\n")
    speak(answer)

# Main function: handles command-line options for alarms, opening software, or immediate AI query.
def main():
    parser = argparse.ArgumentParser(
        description="Ask questions to the AI Terminal with device alarms and software opening."
    )
    parser.add_argument("question", type=str, nargs="?", help="The question you want to ask the AI.")
    parser.add_argument("--alarm", type=str, help="Set an alarm (in HH:MM 24-hour format).")
    parser.add_argument("--open", type=str, help="Open a specific software (by name).")
    args = parser.parse_args()

    if args.open:
        open_software(args.open)

    if args.alarm:
        # Set the alarm on the device (via Reminders) and exit immediately.
        set_device_alarm(args.alarm)
        console.print("Terminal released.", style="green")
        return

    if args.question:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_anim = executor.submit(super_cute_loading_animation)
            answer = ask_question(args.question)
            try:
                future_anim.result(timeout=1)
            except concurrent.futures.TimeoutError:
                pass
        console.print(f"\r{colored('Answer is ready!', 'green')} [bold magenta]{answer}[/bold magenta]\n")
        console.print(f"\n🌸💖✨ [bold magenta]Your Magical Answer:[/bold magenta] [bold yellow]{answer}[/bold yellow] ✨💖🌸\n")
        speak(answer)
    else:
        run_ai()

if __name__ == "__main__":
    main()
