import json
import os

FILE = 'config.json'

def load():
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        print("Lets start creating your little me ")
        user = {}
        user['name'] = input("What is your name?: ")
        user['vibe'] = input("What is your vibe in 2-3 words ( chill, chaos)?: ")
        user['goal'] = input("What is your goal in 2-3 words ( be happy, be rich)?: ")
        user['worsthabit'] = input("What is your worst habit in 2-3 words ( procrastination, laziness)?: ")
        user['fear'] = input("What is your biggest fear in 2-3 words ( failure, loneliness)?: ")
        user['favthing'] = input("What is your favorite thing in 2-3 words ( music, food)?: ")
        user['api_key'] = input("Enter your Google Generative AI API key: ")

        with open(FILE, "w") as f:
            json.dump(user, f, indent=2)
        print("Your PC is succesfully infiltrated with virus!! lol jk, you are ready to go!")
    with open(FILE, 'r') as f:
        return json.load(f)