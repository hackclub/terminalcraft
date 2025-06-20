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

    def run(self):
        print('Welcome to the Interview Simulator!\n')
        for i, (question, correct_answer) in enumerate(self.questions, start=1):
            print(f'Q{i}: {question}')
            answer = input('Your answer: ').strip()
            if answer.lower() == correct_answer.lower():
                print('Correct! ✅\n')
                self.score += 1
            else:
                print(f'Incorrect. The correct answer is: {correct_answer}\n')
        print(f'Interview Completed! Your score: {self.score}/{len(self.questions)}')

if __name__ == '__main__':
    sim = InterviewSimulator()
    sim.run()
