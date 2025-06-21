import time
import sys
import datetime
import random

import listener

# load settings with json
import json
settings = {}
try:
    file = open("settings.json")
    settings = json.load(file)
    file.close()
except FileNotFoundError:
    pass
    # i'll do the setting encounter later
    # # file doesn't exist or settings incomplete
    # settings = {"path": "./recordings", "exitKey": "esc"}
    # with open("settings.json", "w"):

# header
print("This application listens to your keyboard pattern, records it, and analys it. \nSo you know how you code and you can improve on it!\n")

running = True
while running:
    # headers
    input("enter to start")
    
    startTime = datetime.datetime.now().strftime("%y%d%m%H%M%S")
    keyList = listener.listen()

    # anylize listened keys
    # first save everything
    endTime = datetime.datetime.now().strftime("%y%d%m%H%M%S")
    with open(settings["path"]+"/"+startTime+"-"+endTime+".json", "w") as file:
        json.dump(keyList, file)
