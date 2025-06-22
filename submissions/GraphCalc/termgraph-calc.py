USE_ARGPARSE = True
USE_OS = True
if USE_ARGPARSE:
    import argparse
    parser = argparse.ArgumentParser()
else:
    parser = ()
STARTBRACKET = "("
ENDBRACKET = ")"
def find_bracket(string, beginBracket="(", endBracket=")", skip=0, stringID=0):
    posStack = []
    foundBrackets = []
    bracketContent = []
    i = 0
    depth = 0
    for l in string:
        if l == beginBracket:
            if len(posStack) <= skip:
                posStack.append(i)
            else:
                depth += 1
        elif l == endBracket:
            if depth < 1:
                b = posStack.pop()
                foundBrackets.append((string[b+1:i],b,i,stringID))
                bracketContent.append(foundBrackets[-1][0])
            else:
                depth -= 1
        i += 1
    return((bracketContent,foundBrackets))
def substitute(tar,newContent,start,end):
    target = []
    for l in tar:
        target.append(l)
    print(target)
    for i in range(start,end):
        target.pop(i)
    i = start
    for l in newContent:
        target.insert(i,l)
        i += 1
    stringTar = ""
    for l in target:
        stringTar += l
    return stringTar
layers = []
def executive_breakdown(fullstring):
    global layers
    layers.append([find_bracket(fullstring)[1]])
    i = 0
    layers.append([])
    layers.append([])
    for rec in layers[0]: #individual output of find_bracket
        for s in rec:
            i += 1
            tup = s
            layers[-2].append(tup)
            if (STARTBRACKET in tup[0]) or (ENDBRACKET in tup[0]):
                tempBracket = find_bracket(tup[0],stringID=1)
                for tup2 in tempBracket[1]:
                    print(tup2)
                    tup2n = (tup2[0], tup2[1], tup2[2])
                    layers[-1].append(tup2n)
    return layers

def multisplit(string,splitters=["+","-"]):
    res = []
    current = splitters[0]
    currentPos = 0
    i = 0
    for l in string:
        if l in splitters:
            res.append((current,string[currentPos:i]))
            current = l
            currentPos = i+1 #avoids including the splitter
        i += 1
    res.append((current,string[currentPos:]))
    return res
def sign(x):
    if x == "+":
        return 1
    elif x == "-":
        return -1
    elif x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
def multisum(multiInput):
    output = 0
    secondInput = []
    for i in multiInput:
        asteriskRes = 1
        asterisk = multisplit(i[1], ["*","/"])
        if True:
            print(asterisk)
        for a in asterisk:
            if a[1] == 0:
                a[1] == 1 #avoid division by zero
                print("attempted div by zero")
            a[1] == float(a[1])
            if a[0] == "/":
                asteriskRes /= float(a[1])
            else:
                asteriskRes *= float(a[1])
        if True:
            print(f"from {i[1]} to {asteriskRes}")
        secondInput.append((i[0],asteriskRes)) #multiply before summing
    print(secondInput)
    for i in secondInput:
        if i[0] == "-":
            output -= float(i[1])
        else:
            output += float(i[1])
    return output
def math_solve(math, x, xChar="x"):
    xPositions = []
    i = 0
    changeMath = math
    while xChar in changeMath:
        while i < len(changeMath):
            if changeMath[i] == xChar:
                toChange = substitute(changeMath,str(x),i,i+1)
                break
            i += 1
        if True:
            print(toChange)
        changeMath = toChange
    print(changeMath)
    nextInput = changeMath
    parsedNextInput = multisplit(nextInput,["+","-"])
    print(parsedNextInput)
    return multisum(parsedNextInput)
def tests():
    #print(executive_breakdown("(balls (are goofy) lol (or ((likely )and (perhaps))) not) but (maybe y)es"))
    m = multisplit("2*3+2*5-6/3")
    r = multisum(m)
    print(r)
    mathRes = math_solve("2*x+2*5-6/x","3")
    mathRes2 = math_solve("2*x+2*5-6/x","2")
    print((mathRes,mathRes2))
def getArg(argname,arguments=()): #do not use, it doesn't work :(
    if USE_ARGPARSE:
        res = 0
        exec(f"res = arguments.{argname}")
        return res
    else:
        return input(f"Choose {argname}:\n")
def termgraph_calc_begin():
    if USE_ARGPARSE:
        parser.add_argument("--function",type=str,default="x*x/4")
        parser.add_argument("--x-offset",default=0,type=float)
        parser.add_argument("--x-range",default=6,type=float)
        if USE_OS:
            parser.add_argument("--run", default=False,type=bool)
        parser.add_argument("--file",default="function.csv",type=str)
        arguments = parser.parse_args()
    else:
        arguments = ()
    sampleSize = 9
    rangeStep = arguments.x_range/sampleSize
    samplePlaces = []
    sampleY = []
    csvText = ""
    for i in range(sampleSize-1):
        samplePlaces.append(round(i*rangeStep+getArg("x_offset",arguments),3))
    print(samplePlaces)
    functionArg = arguments.function
    print(functionArg)
    for i in samplePlaces:
        sampleY.append(math_solve(functionArg,i))
    print(sampleY)
    for i in sampleY[:-1]:
        csvText += str(i)
        csvText += ","
    csvText += str(sampleY[-1])
    with open(getArg("file",arguments), "w") as file:
        file.write(csvText)
    if USE_OS and arguments.run:
        import os
        os.system(f"python termgraph.py {arguments.file}")
if __name__ == "__main__":
    termgraph_calc_begin()
