import datetime
import os
import termios
import sys

# project src
import listener
import analysis

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

# prints a bar garph in terminal
def barGraph(numbers, max_bars=8):
    min_val = min(numbers)
    max_val = max(numbers)
    range_size = (max_val - min_val + 1) // max_bars + 1
    # Initialize ranges
    ranges = [(min_val + i * range_size, min_val + (i + 1) * range_size - 1) for i in range(max_bars)]
    ranges[-1] = (ranges[-1][0], max_val)  # Ensure the last range includes the max value
    # Count occurrences in each range
    range_counts = [0] * max_bars
    for num in numbers:
        for i, (start, end) in enumerate(ranges):
            if start <= num <= end:
                range_counts[i] += 1
                break
    # Display the bar graph
    for (start, end), count in zip(ranges, range_counts):
        label = f"{round(start)}s-{round(end)}s"
        print(f"{label:10}: {('=' * count * 2):20}({count})")

# explain XD
def explainAnalysis(actionStatistics, active, stops, activeTotle, stopTotle):
    print("\n\nHere is the analysis of all your working habit through your keyboard activities we ever recorded.")
    print("You:")
    print(f"Switches Tab once every {actionStatistics["switchTab"]["onceInAWhile"]} seconds in average")
    print(f"Copies stuff once every {actionStatistics["copy"]["onceInAWhile"]} seconds in average")
    print(f"Pastes stuff once every {actionStatistics["paste"]["onceInAWhile"]} seconds in average")
    print(f"Spends {int(actionStatistics["type"]["timePercentage"] * 100)}% of the time actaully typing stuff")
    print(f"How long do you actually stay active on your work:")
    barGraph(sorted(list(zip(*active))[-1]))
    print(f"How long do you stay unactive everytime you stop:")
    barGraph(sorted(list(zip(*stops))[-1]))
    print(f"You stay active for {int(activeTotle / (activeTotle + stopTotle) * 100)}% of the time")
    print(f"And you stay unactive for {int(stopTotle / (activeTotle + stopTotle) * 100)}% of the time.")
    input("Enter to continue: ")

# header
print("\nThis application listens to your keyboard pattern, records it, and analys it. \nSo you know how you work and you can improve on it!")

# the main logic
while True:
    termios.tcflush(sys.stdin, termios.TCIFLUSH) # sometimes pynput messes up input buffer
    # headers + options: 
    userOption = input("""
Options: 
 - q: quit
 - a: analysis with all avalible data
 - enter: record new

> """).strip().lower()
    
    # deal with inputs
    if (not userOption):
        # start listening
        startTime = datetime.datetime.now().strftime("%y%d%m%H%M%S")
        print("we started recording your keyboard activities! good luck on your work and press esc to exit!")
        keyList = listener.listen()
        # save everything
        endTime = datetime.datetime.now().strftime("%y%d%m%H%M%S")
        if (not os.path.exists(settings["path"])):
            os.makedirs(settings["path"])
        fileName = startTime+"-"+endTime+".json"
        with open(settings["path"]+"/"+fileName, "w") as file:
            json.dump(keyList, file)
        print(f"Data of this session is saved to file \"{fileName}\", and its avalible for anlysis!")
    #quit
    elif (userOption == "q"):
        print("Thank you for using this application, good luck on your improvement!")
        break
    #analysis
    elif (userOption == "a"):

        #perpare data
        actives = []
        stops = []
        activeTotle = 0
        stopTotle = 0
        actionStatistics = []
        fileNum = 0
        # take each data in average
        for fileName in os.listdir(settings["path"]):
            try:
                keyList = json.load(open(settings["path"]+"/"+fileName))
            except Exception as s:
                print(s)
                continue
            fileNum += 1
            # print(fileNum, fileName, os.listdir(settings["path"])) # debug
            # first perpare data
            dividedActionList, aafa = analysis.divideData(keyList)
            # again take average
            actionStatistics_ = analysis.analysisHabit(keyList, dividedActionList, aafa)
            staticFormate = {"num" : 0, "timeSpent" : 0, "timePercentage" : 0, "onceInAWhile": 0} # copied from analysis.py, update in future if needed
            if (not actionStatistics): actionStatistics = actionStatistics_
            else:# adds everything together!!! normalize to average later
                for actionKey in actionStatistics:
                    for dataKey in staticFormate:
                        actionStatistics[actionKey][dataKey] += actionStatistics_[actionKey][dataKey]
            # merge sotps and actives together
            actives_, stops_, activeTotle_, stopTotle_ = analysis.analysisStops(keyList, dividedActionList, aafa)
            actives.extend(actives_)
            stops.extend(stops_)
            activeTotle += activeTotle_
            stopTotle += stopTotle_
        # normalize part of staticstics to average
        for actionKey in actionStatistics:
            actionStatistics[actionKey]["timePercentage"] /= fileNum
            actionStatistics[actionKey]["onceInAWhile"] /= fileNum
        # then display all at once
        explainAnalysis(actionStatistics, actives, stops, activeTotle, stopTotle)
    #nothing happens
    else:
        print("Invalid command")

