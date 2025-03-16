class Player:
    def __init__(self, username):
        self.username = username
        self.score = 0
        self.answer = None
    
    def getAnswer(self):
        self.answer = input(f"{self.username}, what is your answer? ")