import datetime
import os
import termios
import sys

# project src
import listener
import analysis
import explain

# load settings with json
import json
settings = {}
file = open("settings.json")
settings = json.load(file)
file.close()

# the main logic
print("\nThis application listens to your keyboard pattern, records it, and analys it. \nSo you know how you work and you can improve on it!")
while True:
    termios.tcflush(sys.stdin, termios.TCIFLUSH) # sometimes pynput messes up input buffer
    # headers + options: 
    userOption = input("""
Options: 
 - q: quit
 - aa: analysis with all avalible data
 - a <json file name> analysis with data from one session
 - enter: record new

> """).strip().lower()
    inputList = userOption.split(" ")
    
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

    #analysis all
    elif (userOption == "aa"):
        #perpare data
        actives = []
        stops = []
        activeTotle = 0
        stopTotle = 0
        actionStatistics = []
        fileNum = 0

        # loop through files
        for fileName in os.listdir(settings["path"]):
            try:
                keyList = json.load(open(settings["path"]+"/"+fileName))
            except Exception as s:
                print(s)
                continue
            fileNum += 1
            
            # perpare divided data 
            dividedActionList, aafa = analysis.divideData(keyList)

            # analysis habit
            actionStatistics_ = analysis.analysisHabit(keyList, dividedActionList, aafa)
            staticFormate = {"num" : 0, "timeSpent" : 0, "timePercentage" : 0, "onceInAWhile": 0} # copied from analysis.py, update in future if needed

            # merge analysised habits
            if (not actionStatistics): actionStatistics = actionStatistics_
            else:# adds everything together!!! normalize to average later
                for actionKey in actionStatistics:
                    for dataKey in staticFormate:
                        actionStatistics[actionKey][dataKey] += actionStatistics_[actionKey][dataKey]
            
            # analysis then merged stops
            actives_, stops_, activeTotle_, stopTotle_ = analysis.analysisStops(keyList, dividedActionList, aafa)
            actives.extend(actives_)
            stops.extend(stops_)
            activeTotle += activeTotle_
            stopTotle += stopTotle_

        # normalize staticstics to average
        for actionKey in actionStatistics:
            actionStatistics[actionKey]["timePercentage"] /= fileNum
            actionStatistics[actionKey]["onceInAWhile"] /= fileNum
        # then display all data
        explain.explainAnalysis(actionStatistics, actives, stops, activeTotle, stopTotle)

    # analysis a certain one
    elif (inputList[0] == "a" and len(inputList) == 2):
        #open file
        fileName = inputList[1].strip(" \n\"'<>")
        if fileName in os.listdir(settings["path"]):
            try:
                keyList = json.load(open(settings["path"]+"/"+fileName))
            except Exception as s:
                print(s)

        # analysis
        dividedActionList, aafa = analysis.divideData(keyList)
        actionStatistics = analysis.analysisHabit(keyList, dividedActionList, aafa)
        actives, stops, activeTotle, stopTotle = analysis.analysisStops(keyList, dividedActionList, aafa)
        explain.explainAnalysis(actionStatistics, actives, stops, activeTotle, stopTotle, timeline=list(zip(*keyList))[1])

    #nothing happens
    else:
        print("Invalid command")

