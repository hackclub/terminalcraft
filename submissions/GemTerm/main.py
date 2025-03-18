import json

from chat import chat
from clear import clear
from generate import generate
from getname import getname
from help import help
from info import info
from setname import setname

f = open(".data", "r")
data = json.load(f)

has_name: bool = False

info()

while True:
  if "name" in data and data["name"] != "":
    has_name = True
  else:
    print(
      "\033[0;31mWARNING: Looks like you don't have a name set. Please set one now using the 'setname' command, followed by your name.\033[0m"
    )
    has_name = False

  if has_name:
    prefix: str = data["name"] + "@GemTerm > "
  else:
    prefix: str = "GemTerm > "
  x = input("\33[1;49;32m" + prefix + "\033[0m")
  if x == "generate":
    prompt = input("Enter a clear description of the image you want: ")
    generate(prompt)
  elif x == "chat":
    chat()
  elif x == "help":
    help()
  elif x.partition(" ")[0] == "setname":
    name = x.partition(" ")[2]
    data["name"] = setname(name)
  elif x == "getname":
    getname()
  elif x == "clear":
    clear()
  elif x == "":
    continue
  elif x == "info":
    info()
  elif x == "exit":
    break
  else:
    print("Command not found. Type 'help' for a list of available commands.")

f.close()
