import pyfiglet
import time
import random
import json
import sys
import itertools
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TimeRemainingColumn

console = Console()

def typing_effect(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def loading_animation(message='Loading', duration=3):
    for _ in range(duration):
        for dots in ['.  ', '.. ', '...']:
            print(f'\r{message}{dots}', end='', flush=True)
            time.sleep(0.5)
    print('\r' + ' ' * 20, end='\r')

def winner_animation():
    art = pyfiglet.figlet_format('YOU WIN!')
    console.print(f'[bold green]{art}[/bold green]')
    typing_effect('🏆 Congratulations, you passed the simulator! 🧠💪')

def loser_animation():
    art = pyfiglet.figlet_format('Try Again!')
    console.print(f'[bold red]{art}[/bold red]')
    typing_effect('😢Do not give up! Practice makes perfect!')

class InterviewSimulator:

    def __init__(self):
        self.easy_questions = [
            {
                'question': 'What does HTML stand for?',
                'options': ['HyperText Markup Language', 'Home Tool Markup Language', 'Hyperlink Machine Language', 'HighText Machine Language'],
                'answer': 'a'
            },
            {
                'question': 'Which data structure uses FIFO?',
                'options': ['Stack', 'Queue', 'Tree', 'Array'],
                'answer': 'b'
            },
            {
                'question': 'Which language is used for styling web pages?',
                'options': ['HTML', 'CSS', 'JavaScript', 'Python'],
                'answer': 'b'
            },
            {
                'question': 'What is 2 + 2 * 2?',
                'options': ['6', '8', '4', '10'],
                'answer': 'a'
            },
            {
                'question': 'What symbol is used for comments in Python?',
                'options': ['//', '#', '/* */', '<!-- -->'],
                'answer': 'b'
            },
            {
                'question': 'Which keyword is used to define a function in Python?',
                'options': ['def', 'function', 'define', 'fun'],
                'answer': 'a'
            },
            {
                'question': 'Which one is a valid variable name in Python?',
                'options': ['1name', 'my-var', '_temp', 'import'],
                'answer': 'c'
            },
            {
                'question': 'What is the output of: print("5" + "6")?',
                'options': ['11', '56', 'Error', 'None'],
                'answer': 'b'
            },
            {
                'question': 'Which command initializes a Git repository?',
                'options': ['git init', 'git start', 'git begin', 'git push'],
                'answer': 'a'
            },
            {
                'question': 'Which extension is used for Python files?',
                'options': ['.py', '.js', '.html', '.exe'],
                'answer': 'a'
            }
        ]  
        self.medium_questions = [
            {
                'question': 'What is the output of this code?\n\nx = [1, 2, 3]\nprint(x[-1])',
                'options': ['1', '2', '3', 'Error'],
                'answer': 'c'
            },
            {
                'question': 'Which operator is used for exponentiation in Python?',
                'options': ['^', '**', '//', 'exp()'],
                'answer': 'b'
            },
            {
                'question': 'What is the output of:\nprint(type([]))?',
                'options': ['<class "list">', '<list>', 'list', 'array'],
                'answer': 'a'
            },
            {
                'question': 'Which statement is true about Python sets?',
                'options': ['They allow duplicates', 'They are unordered', 'They are indexed', 'They are mutable and ordered'],
                'answer': 'b'
            },
            {
                'question': 'What is the scope of a variable declared inside a function?',
                'options': ['Global', 'Local', 'Module', 'Static'],
                'answer': 'b'
            },
            {
                'question': 'Which of the following is used to handle exceptions in Python?',
                'options': ['try-catch', 'try-except', 'throw-catch', 'error-handler'],
                'answer': 'b'
            },
            {
                'question': 'What is the output of:\nprint(10 // 3)?',
                'options': ['3', '3.33', '4', 'Error'],
                'answer': 'a'
            },
            {
                'question': 'Which is NOT a valid Python data type?',
                'options': ['dict', 'set', 'array', 'tuple'],
                'answer': 'c'
            },
            {
                'question': 'What does the strip() method do?',
                'options': ['Removes spaces', 'Replaces characters', 'Splits a string', 'Capitalizes text'],
                'answer': 'a'
            },
            {
                'question': 'What will be the output?\nprint("Python" * 2)',
                'options': ['PythonPython', 'Error', 'Python 2', '2Python'],
                'answer': 'a'
            }
        ]
        self.hard_questions = [
            {
                'question': 'What is the output of:\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)',
                'options': ['[1, 2, 3]', '[1, 2, 3, 4]', '[4]', 'Error'],
                'answer': 'b'
            },
            {
                'question': 'Which of the following is used to define a class in Python?',
                'options': ['function', 'define', 'class', 'struct'],
                'answer': 'c'
            },
            {
                'question': 'What is a decorator in Python?',
                'options': ['A data type', 'A way to loop', 'A function that modifies another function', 'A class method'],
                'answer': 'c'
            },
            {
                'question': 'Which of the following sorts a list in-place?',
                'options': ['sorted()', 'sort()', 'order()', 'arrange()'],
                'answer': 'b'
            },
            {
                'question': 'Which one is a mutable type in Python?',
                'options': ['tuple', 'int', 'list', 'str'],
                'answer': 'c'
            }
        ]  

        self.score = 0
        self.total = 0
        self.streak = 0
        self.history_file = 'history.json'

    def display_title(self):
        title = pyfiglet.figlet_format('Interview\nSimulator')
        console.print(f'[bold cyan]{title}[/bold cyan]')

    def countdown_timer(self, seconds=20):
        with Progress(
            '[progress.description]{task.description}',
            BarColumn(bar_width=None),
            '[progress.percentage]{task.percentage:>3.0f}%',
            TimeRemainingColumn(),
            transient=True
        ) as progress:
            task = progress.add_task('⏳ Time Left', total=seconds)
            for _ in range(seconds):
                progress.update(task, advance=1)
                time.sleep(1)

    def random_feedback(self, correct=True):
        correct_msgs = ['Nice job!', 'You nailed it!', '🔥 Keep going!', '✅ That’s right!']
        wrong_msgs = ['Oops! Not quite.', '❌ Try again next time.', 'Incorrect, but keep it up!']
        return random.choice(correct_msgs if correct else wrong_msgs)

    def ask_question(self, q_obj, index):
        console.rule(f'[bold blue]Question {index}[/bold blue]')
        print(colored(q_obj['question'], 'cyan'))
        for i, option in enumerate(q_obj['options']):
            letter = chr(97 + i)
            print(colored(f'{letter}) {option}', 'white'))

        self.countdown_timer(20)
        answer = input(colored('Your answer (a/b/c/d): ', 'yellow')).lower().strip()
        if answer == q_obj['answer']:
            console.print(f'✅ [green]{self.random_feedback(True)}[/green]\n')
            self.score += 1
            self.streak += 1
        else:
            correct_letter = q_obj['answer']
            correct_text = q_obj['options'][ord(correct_letter) - 97]
            console.print(f'❌ [red]{self.random_feedback(False)}[/red] The correct answer was: [white]{correct_letter}) {correct_text}[/white]\n')
            self.streak = 0

    def run(self):
        self.display_title()
        console.print('Welcome to the [bold yellow]Interview Simulator[/bold yellow]!\n', style='bold green')
        console.print('💀 [bold red]Keep your eyes on the keyboard, the answer you type won’t be visible![/bold red]\n')
        time.sleep(1)

        input('Press [Enter] to start the Easy section...')
        loading_animation('Preparing Easy Questions')
        easy_qs = random.sample(self.easy_questions, 10)
        for i, q in enumerate(easy_qs, 1):
            self.ask_question(q, i)

        input('Press [Enter] to unlock the Medium section...')
        loading_animation('Loading Medium Round')
        medium_qs = random.sample(self.medium_questions, 10)
        for i, q in enumerate(medium_qs, 1):
            self.ask_question(q, i)

        input('Press [Enter] to unlock the Hard section...')
        loading_animation('Unlocking Hard Mode')
        hard_qs = random.sample(self.hard_questions, 5)
        for i, q in enumerate(hard_qs, 1):
            self.ask_question(q, i)

        self.total = 25

        console.rule('[bold magenta]Results[/bold magenta]')
        table = Table(title='Interview Summary')
        table.add_column('Total Questions', justify='center')
        table.add_column('Correct Answers', justify='center')
        table.add_column('Score (%)', justify='center')

        percentage = (self.score / self.total) * 100
        table.add_row(str(self.total), str(self.score), f'{percentage:.1f}%')
        console.print(table)

        if self.score == self.total:
            console.print('🎉 [bold green]Perfect Score! You nailed it![/bold green]')
        elif self.score >= self.total * 0.7:
            winner_animation()
        else:
            loser_animation()

        self.save_history(percentage)
        self.show_history_table()

    def save_history(self, percent):
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        history.append({'score': percent, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

        console.print('\n📊 [cyan]History saved to history.json[/cyan]')

    def show_history_table(self):
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            console.print('[red]No history found.[/red]')
            return

        if not history:
            console.print('[yellow]No attempts recorded yet.[/yellow]')
            return

        console.rule('[bold cyan]History[/bold cyan]')
        history_table = Table(title='Previous Attempts')
        history_table.add_column('Timestamp', justify='center')
        history_table.add_column('Score (%)', justify='center')

        for attempt in history[-10:]:
            history_table.add_row(attempt['timestamp'], f"{attempt['score']:.1f}%")

        console.print(history_table)

if __name__ == '__main__':
    sim = InterviewSimulator()
    sim.run()
