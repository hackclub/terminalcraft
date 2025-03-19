import requests
import json
import sys
import time
import threading
from termcolor import colored
from rich.console import Console
from rich.progress import Progress
from rich.spinner import Spinner
from rich.text import Text

# Initialize the console for beautiful output
console = Console()

# Super cute loading animation ✨💖
def super_cute_loading_animation():
    symbols = [
        "🌟 (✿◕‿◕) 🌟",  
        "💖 (｡♥‿♥｡) 💖",  
        "✨ ~(˘▾˘~) ✨",  
        "💫 (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ 💫",  
        "🐱 (=ↀωↀ=) 🐱"
    ]
    for _ in range(5):  # Loop the symbols 5 times for better animation flow
        for symbol in symbols:
            sys.stdout.write(f'\r{colored("Thinking...", "cyan")} {colored(symbol, "magenta", attrs=["bold"])}')
            sys.stdout.flush()
            time.sleep(0.3)

# Function to send the question to the AI API
def ask_question(question):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {"messages": [{"role": "user", "content": question}]}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        answer = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No answer')
        return answer
    else:
        return "Error: Unable to get a response."

# Main function to interact with user
def main():
    console.print("\n💖✨ [bold cyan]Welcome to the Cutest AI Chat Terminal![/bold cyan] ✨💖")
    console.print(colored("Ready to answer all your magical questions. Type 'exit' to quit. ✨", "magenta"))

    while True:
        question = console.input("\n🌸 [bold magenta]Ask anything (or type 'exit' to quit): [/bold magenta] ")

        if question.lower() in ["exit", "quit"]:
            console.print("\n💫 [bold yellow]Goodbye, stay magical! 💖✨[/bold yellow]\n")
            break

        # Show a progress bar for a smooth waiting experience
        with Progress() as progress:
            # task = progress.add_task("[cyan]Loading your answer...", total=100)
            while not progress.finished:
                time.sleep(0.1)
                progress.update(task, advance=1)

        # Run the super cute loading animation in the background
        loading_thread = threading.Thread(target=super_cute_loading_animation)
        loading_thread.daemon = True  # Allow the animation to stop when the main program finishes
        loading_thread.start()

        # Start spinner manually for smoother feedback
        spinner = Spinner("dots", text="Please wait, we're getting your answer... 💖✨", style="cyan")
        console.print(spinner, end="\r")

        # Run the question-fetching in another thread so we don't block the main thread
        answer_thread = threading.Thread(target=fetch_answer, args=(question,))
        answer_thread.start()

        # Wait for the answer to be fetched
        answer_thread.join()

        # Stop the loading animation once we have the answer
        loading_thread.join(0.1)  # Allow animation to end quickly

def fetch_answer(question):
    # Get the answer to the question
    answer = ask_question(question)

    # Print the final answer in the console
    console.print(f"\r{colored('Answer is ready!', 'green')} [bold magenta]{answer}[/bold magenta]\n")
    # Display the answer in a magical style! ✨
    console.print(f"\n🌸💖✨ [bold magenta]Your Magical Answer:[/bold magenta] [bold yellow]{answer}[/bold yellow] ✨💖🌸\n")

if __name__ == "__main__":
    main()
