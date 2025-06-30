def divideData(keyList):
    # initializing database
    aafa = ["switchTab", "copy", "paste", "type"] # stands for "action avalible for analysis"
    actions = {
        i : [] for i in aafa
    }

    # below is encountering for actions that is not performed by just two keys
    longTerm = {"type" : None, "startIndex" : -1} 
    skipNext = True

    # ok lets list through all of my keys! 
    for i in range(len(keyList)):
        # manages if a loop should be skiped: 
        # if the last key is involved in some other event then it is not gonna get involved in this event, therefore skip
        if skipNext:
            skipNext = False
            continue

        # determin what action just got performed by checking the key behind of it, or if there even is any
        indexData = (i - 1, i)
        if (keyList[i][0] == "ctrl" and keyList[i - 1][0] == "alt") or \
            (keyList[i][0] == "alt" and keyList[i - 1][0] == "ctrl") or \
            (keyList[i][0] == "tab" and keyList[i - 1][0] == "alt") or \
            (keyList[i][0] == "alt" and keyList[i - 1][0] == "tab"):
            actions["switchTab"].append(indexData)
            skipNext = True
        elif keyList[i][0] == "c" and keyList[i - 1][0] == "ctrl":
            actions["copy"].append(indexData)
            skipNext = True
        elif keyList[i][0] == "v" and keyList[i - 1][0] == "ctrl":
            actions["paste"].append(indexData)
            skipNext = True
        elif len(keyList[i][0]) == 1 or keyList[i][0] in ['space', 'enter', 'tab', 'backspace', "delete"]:
            if longTerm["startIndex"] == -1 or not longTerm["type"]:
                longTerm["startIndex"] = i
                longTerm["type"] = "typing"
            continue
        else:
            if longTerm["type"] == "typing":
                actions["type"].append((longTerm["startIndex"], i))
                longTerm["startIndex"] = -1
                longTerm["type"] = None
                skipNext = True # if typing continues, still checking the next one. howeven if typing stoped that means skiping next one
                continue

    return actions, aafa # return divided action lists!


def analysisHabit(keyList, dividedActionList, aafa):
    # now we divid all the habits and listed them, , its time for us to actually analysis it
    staticFormate = {"num" : 0, "timeSpent" : 0, "timePercentage" : 0, "onceInAWhile": 0}
    actionStatistics = {
        i : staticFormate.copy() for i in aafa
    }
    totleTime = keyList[-1][1] - keyList[0][1]
    for i in aafa:
        for start, end in dividedActionList[i]:
            actionStatistics[i]["num"] += 1
            actionStatistics[i]["timeSpent"] += keyList[end][1] - keyList[start][1]
        if actionStatistics[i]["num"] == 0: continue # needs further encountering code for empty events, especially in explaination
        actionStatistics[i]["onceInAWhile"] = totleTime / actionStatistics[i]["num"]
        actionStatistics[i]["timePercentage"] = actionStatistics[i]["timeSpent"] / totleTime

    return actionStatistics # returning the staticstics of actions

def analysisStops(keyList, dividedActionList, aafa):
    # perpare returning data and analysis data
    shortestStop = 15
    active = []
    stops = []
    lastEnd = keyList[0][1]
    lastStart = keyList[0][1]

    # actionsConsideredActive = ["switchTab", "copy", "paste", "type"]
    # dividedActionList = [action for i in actionsConsideredActive for action in dividedActionList[i]]
    # dividedActionList.sort(key = lambda x : x[0])
    
    for _, unixTime in keyList:
        # if your stoped for too long
        if unixTime - lastEnd > shortestStop:
            stops.append((lastEnd, unixTime, unixTime - lastEnd))
            active.append((lastStart, lastEnd, lastEnd - lastStart))
            lastStart = unixTime # start the next active timeline from here
        lastEnd = unixTime # eitherway, this is the last time you been active

    # now we have all list of stop interval and active interval
    activeTotle = 0
    for i in active:
        activeTotle += i[2]
    stopTotle = 0
    for i in stops:
        stopTotle += i[2]

    return active, stops, activeTotle, stopTotle
    
def analysisHours(keyList, dividedActionList, aafa):
    return list(zip(*keyList))[0]

