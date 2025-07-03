import math
import os
import time
import argparse
yVals = [[20,10,50,40,100]]
xVals = []
yMax = max(yVals[0])
xMax = 1
XDIST = 50 #available space for graph
YCHAR = 5/3 #height:width for characters
YDIST = 36
FULLCHAR = "#"
horizontalSeparator = "="
renderTable = []
elementGap = 5
gapPlace = []
xLabels = []
yLabels = []
yLabelPos = []
yLabelLength = 0
fileSeparator = ","
debugLevel = 0 #set to 7 when long_write errors
customXLabels = False
xLabelShift = 0
args = ()
def load_csv(filename):
    global yVals
    with open(filename) as file:
        loadCheck = 0
        for line in file:
            iLoad = 0
            yVals.append([])
            for item in line.split(fileSeparator):
                yVals[-1].append(float(item.strip())) #append to last dataset array
                iLoad += 1
            if debugLevel > 3: #debug
                if loadCheck < 1:
                    loadCheck = iLoad
                elif loadCheck == iLoad:
                    iLoad = 0 #reset loading counter
                else:
                    print(f"expected {loadCheck} got {iLoad} at line {line}")
                    raise ValueError(f"err when loading csv lines, last {yVals[-2]} now {yVals[-1]}")
def c(s):
    pass
def newSubroutine(inputLine,lineNum):
    global yVals
    if len(yVals) == 0:
        yVals.append([])
    iItem = 0
    for item in inputLine:
        if len(yVals) > iItem:
            yVals[iItem].append(float(item))
            c("iItem is the set of values-position, item is the current item")
        else:
            yVals.append([])
            for retrieve in yVals[0]:
                yVals[-1].append(float(retrieve))
            yVals[-1][-1] = float(item)

            c("all X columns have to be at least depth 0, so they are in yVals[0]")
        iItem += 1 
def newLoad(path,doCustomX=False):
    global yVals, xVals
    with open(path) as file:
        iLine =0
        for line in file:
            splitLine=line.strip().split(",")
            if doCustomX:
                xVals.append(float(splitLine[0]))
                newSubroutine(splitLine[1:],iLine)
            else:
                newSubroutine(splitLine,iLine)
def y_check(valArray):
    countArray = []
    for dataArray in valArray:
        countArray.append(len(dataArray))
    sortedCountArray = sorted(countArray)
    if sortedCountArray[0] == sortedCountArray[-1]:
        return True
    else:
        return False
def operation_2D(array2D,op=max):
    opArray = []
    for array1D in array2D:
        opArray.append(op(array1D))
    return (op(opArray),max(opArray),len(opArray))
def reverseNorm(value,mode=0,base=10,anyMax=yMax):
    if mode == 1:
        return math.sqrt(value*anyMax**2)
    elif mode == 2:
        return (value*math.sqrt(anyMax))**2
    elif mode == 3:
        return math.log(value*(base**anyMax),base=base)
    elif mode == 4:
        return base**(value*math.log(anyMax,base=base))
    else:
        return value*anyMax
def n_y(value, mode=0, base=10, anyMax=yMax):
    if mode == 1:
        return (value**2)/(anyMax**2) #square norming
    elif mode == 2:
        return (math.sqrt(value))/(math.sqrt(anyMax))
    elif mode == 3:
        return (base**value)/(base**yMax)
    elif mode == 4:
        return(math.log(value,base=base))/(math.log(anyMax,base=base))
    else:
        return value/anyMax

def count_gap_place(pointsEnabled=False):
    global gapPlace, elementGap
    elementGap = math.floor((XDIST/2)/(len(yVals[0])))
    if not pointsEnabled:
        for i in range(len(yVals[0])):
            gapPlace.append(elementGap+elementGap*i*2)
            #comment out if using custom labels:
            if False == customXLabels:
                xLabels.append(i)
    else:
        for item in xVals:
            gapPlace.append(round(n_y(item,anyMax=xMax)*XDIST)-1)
            if False == customXLabels:
                xLabels.append("^") #random char
            if debugLevel > 4:
                print(f"label gap pos from {item} into {n_y(item,anyMax=xMax)*XDIST} xMax {xMax}")
    if gapPlace[-1] > XDIST-2:
        gapPlace[-1] = XDIST-2
    if debugLevel > 2:
        print(f"leeks {gapPlace} yVals {yVals}")
        time.sleep(2)
def make_y_label(fraction=4):
    global yLabels, yLabelLength, yLabelPos
    yLabels.append(round(yMax))
    yLabelPos.append(0)
    i = 1
    unitFrac = 1/fraction
    while i < fraction:
        reverse = reverseNorm(unitFrac*i,anyMax=yMax)
        yLabels.append(round(reverse))
        yLabelPos.append(round(YDIST*(1-unitFrac*i)))
        if debugLevel > 5:
            print(reverse)
        i += 1
    lengthDecider = []
    for i in yLabels:
        lengthDecider.append(len(str(i)))
    yLabelLength = sorted(lengthDecider)[-1]
    if debugLevel > 5:
        print(f"length {yLabelLength} labels {yLabels} label pos {yLabelPos}")
def halving(array,mult=0.5):
    i = 0
    while i < len(array):
        array[i] = float(array[i])*mult
        i += 1
def termgraph_prepare():
    global yVals,xLabelShift,yMax,XDIST,YDIST,customXLabels,xLabels,xVals,xMax,args
    parser = argparse.ArgumentParser(description="CLI graph rendering")
    parser.add_argument("file", type=str, help="comma-separated values to plot, one set per each line")
    parser.add_argument("--y-label-fraction",type=int,default=4,help="Number of labels on the y axis")
    parser.add_argument("--y-space",default=36,help="Character count for graph height")
    parser.add_argument("--x-space",default=126,help="Character count for graph width")
    parser.add_argument("--x-labels",default=False,help="Comma-separated labels")
    parser.add_argument("--old-parse",action="store_true",default=False,help="Use new parsing function, each csv line is an entry")
    parser.add_argument("--csv-points",action="store_true",default=False,help="first column is X positions, render as points")
    args = parser.parse_args()
    if args.old_parse:
        args.csv_points = False
    if args.file != "" and args.file != None :
        yVals = []
        if args.old_parse:
            load_csv(args.file)
        else:
            newLoad(args.file,args.csv_points)
        if debugLevel > 5:
            print(yVals)
    #if debugLevel > 2:
    #    for dataset in yVals:
    #        halving(dataset,1)
    xLabelShift = math.floor(len(yVals)/2)
    yMax = operation_2D(yVals,max)[0]
    if args.csv_points:
        xMax = max(xVals)
    XDIST = round(int(args.x_space))
    YDIST = round(int(args.y_space))
    if not args.x_labels == False:
        customXLabels = True
        print("using custom label")
    else:
        customXLabels = False
        print("nevermind")
    count_gap_place(args.csv_points)
    if customXLabels:
        xLabels = args.x_labels.split(",")
    if len(xLabels) != len(gapPlace):
        raise ValueError(f"xlabels {xLabels} of len {len(xLabels)} not the same as {len(gapPlace)}")
    if debugLevel > 5:
        print(f"ymax {yMax}")
        time.sleep(1)
    make_y_label(args.y_label_fraction)
if __name__ == "__main__":
    termgraph_prepare()
def long_write(input, xLastPos, yPos=len(renderTable)-1):
    strInput = str(input)
    if debugLevel > 6:
        print(f"input {strInput} y {yPos}")
    firstX = xLastPos-len(strInput)+1
    if firstX >= 0:
        for i in range(len(strInput)):
            if debugLevel > 6:
                print(f"y {yPos} firstX {firstX} i {i} last len {len(renderTable[firstX+i-1])} len {len(renderTable[firstX+i])}")
            if renderTable[firstX+i][yPos] == " ": #erroring with more lines to plot
                
                
                renderTable[firstX+i][yPos] = strInput[i]
            else:
                print(f"x {firstX+i} letter {strInput[i]} would replace {renderTable[firstX+i][yPos]}")
    else:
        print(f"{input} ending at {xLastPos} with y {yPos} too long")
        time.sleep(2)
        renderTable[xLastPos][yPos] = strInput[-1]
def init_render_table(xdist, ydist,nullchar=" ", yLabelOffset=0):
    global renderTable
    yLabelOffset += 1 #space for separator lines and label
    yLabeli = 0
    while yLabeli < yLabelOffset:
        renderTable.append([])
        for yLabelj in range(ydist):
            if yLabeli+1 == yLabelOffset:
                renderTable[yLabeli].append("|")
            elif yLabeli+2 == yLabelOffset:
                if yLabelj in yLabelPos:
                    labelPlace = yLabelPos.index(yLabelj)
                    renderTable[yLabeli].append(nullchar)
                    long_write(yLabels[labelPlace],yLabeli,yLabelj)
                else:
                    renderTable[yLabeli].append(nullchar)
            else:
                renderTable[yLabeli].append(nullchar)
        yLabeli += 1
    for unoffset in range(xdist-yLabelOffset):
        i = unoffset+yLabelOffset
        renderTable.append([])
        for j in range(ydist):
            if j == ydist-2:
                renderTable[i].append(horizontalSeparator)
            elif j == ydist-1:
                if (i-xLabelShift in gapPlace):
                    renderTable[i].append(nullchar) #long_write can not append
                    print(f"x label at i {i} j {j} xLabelOffset {xLabelShift}")
                    long_write(xLabels[gapPlace.index(i-xLabelShift)],xLastPos=i,yPos=j) #removed -xLabelShift from xLastPos
                else:
                    renderTable[i].append(nullchar)
            else:
                renderTable[i].append(nullchar)
    print((len(renderTable),len(renderTable[0])))

def write_render_table():
    global renderTable
    os.system("clear")
    tempRow = ""
    for i in range(len(renderTable[0])): #number of rows in first (all) columns
        for j in range(len(renderTable)):
            tempRow += str(renderTable[j][i])
        if tempRow != "":
            print(tempRow)
            tempRow = ""

def d_slope(height):
    targetTan = height/(XDIST/len(yVals[0]))
    print(targetTan)
    return 180*math.atan(targetTan)/math.pi #return value in degrees
def bar_graph(vals=yVals[0],offset=0,xdist=XDIST,ydist=YDIST, gap=elementGap,onlyPoint=False):
    gapPos = gap+offset #unused
    for iVal in range(len(vals)):
        iterVal = vals[iVal]
        relative = n_y(iterVal,anyMax=yMax)
        fracNormY = ydist*(1-relative)
        normY = round(fracNormY) #lowest y has highest index
        if normY >= len(renderTable[0]):
            print(f"clipping {normY} to {len(renderTable[0])}")
            normY = len(renderTable[0])-1
        normY -= 2 #termgraph_render decreases yMax too
        if normY < 0:
            print(f"clipping {normY} up")
            normY = 0
        i = len(renderTable[0])-2 #space for separator+numbers
        if debugLevel > 5:
            print(f"bar {iVal} value {iterVal} norm {normY} frac {fracNormY} rel {relative}") 
        if onlyPoint == False:
            while i > normY:
                i -= 1
                renderTable[gapPlace[iVal]+offset][i] = FULLCHAR
        else:
            renderTable[gapPlace[iVal]+offset][normY] = FULLCHAR

        #gapPos += 2*gap
def termgraph_render():
    init_render_table(XDIST,YDIST,yLabelOffset=yLabelLength)
    if y_check(yVals):
        iOffset = 0
        for dataArray in yVals:
            bar_graph(dataArray, offset=iOffset, onlyPoint=args.csv_points)
            iOffset += 1
    else:
        print("y check failed")
        time.sleep(1)
        bar_graph(yVals[0], offset=0,onlyPoint=args.csv_points)
    if debugLevel > 4:
        time.sleep(2)
    if debugLevel > 7:
        time.sleep(4)
    write_render_table()
if __name__ == "__main__":
    termgraph_render()
