import pyfiglet
import time
from colorama import init
from termcolor import colored
from rich.console import Console
from rich.table import Table

console = Console()

class InterviewSimulator:

    def __init__(self):
        self.questions = [
            ('What is the time complexity of binary search?', 'O(log n)'),
            ('Which data structure uses FIFO?', 'Queue'),
            ('What does HTML stand for?', 'HyperText Markup Language'),
            ('What command is used to initialize a Git repository?', 'git init'),
            ('Which language is used for styling web pages?', 'CSS'),
            ('What is the purpose of a constructor in OOP?', 'To initialize objects'),
            ('Which method is used to add an element to the end of a list in Python?', 'append()'),
            ('What is the result of 3 * 1 ** 3?', '3'),
            ('What is a Python dictionary?', 'A key-value pair collection'),
            ('What does HTTP stand for?', 'HyperText Transfer Protocol'),
        ]
        self.score = 0

    def display_title(self):
        title = pyfiglet.figlet_format('Interview\n Simulator')
        console.print(f'[bold cyan]{title}[/bold cyan]')

    def run(self):
        self.display_title()
        console.print('Welcome To The [bold yellow]Interview Simulator[/bold yellow]!\n', style='bold green')
        time.sleep(1)

        for i, (question, correct_answer) in enumerate(self.questions, start=1):
            console.rule(f'[bold blue]Question {i}[/bold blue]')
            print(colored(f'{question}', 'cyan'))
            answer = input(colored('Your answer: ', 'yellow')).strip()

            if answer.lower() == correct_answer.lower():
                console.print('✅ [green]Correct![/green]\n')
                self.score += 1
            else:
                console.print(f'❌ [red]Incorrect[/red]. The correct answer is: [bold white]{correct_answer}[/bold white]\n')

            time.sleep(0.5)

        console.rule('[bold magenta]Results[/bold magenta]')
        table = Table(title='Interview Summary')
        table.add_column('Total Questions', justify='center')
        table.add_column('Correct Answers', justify='center')
        table.add_column('Score (%)', justify='center')

        percentage = (self.score / len(self.questions)) * 100
        table.add_row(str(len(self.questions)), str(self.score), f'{percentage:.1f}%')
        console.print(table)

        if self.score == len(self.questions):
            console.print('🎉 [bold green]Perfect Score! You nailed it![/bold green]')
        elif self.score >= 7:
            console.print('👏 [bold yellow]Good job! Keep it up![/bold yellow]')
        else:
            console.print('💡 [bold red]Keep practicing. You\'ll improve![/bold red]')



if __name__ == '__main__':
    sim = InterviewSimulator()
    sim.run()
