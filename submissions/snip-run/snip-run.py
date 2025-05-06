from prompt_toolkit import shortcuts
import os
import time
import filecmp
SUBDIR = "snip-files"
#SUBDIR = "test-snip-files"
# intended file structure:
# ./SUBDIR has everything (do not clutter own dir)
# ./SUBDIR/_data intended for input and output data
# ./SUBDIR/_output has logs, dumps etc
if not os.path.isdir(f"{SUBDIR}/_output"):
    os.makedirs(f"{SUBDIR}/_output")
if not os.path.isdir(f"{SUBDIR}/_data"):
    os.makedirs(f"{SUBDIR}/_data") # preemptively add these dirs for recognition reasons
filesFound = [f"{f}" for f in os.listdir(SUBDIR) if os.path.isfile(f"{SUBDIR}/{f}") and f.endswith(".py")] # go away regex
folders = [f"{f}" for f in os.listdir(SUBDIR) if os.path.isdir(f"{SUBDIR}/{f}")]

#for fol in folders:
#    nestedFiles.append([f"{fol}/{f}" for f in os.listdir(fol) if os.path.isfile(f"{fol}/{f}") and f.endswith("py")])
for fol in folders:
    currentfiles = [f"{fol}/{f}" for f in os.listdir(f"{SUBDIR}/{fol}") if os.path.isfile(f"{SUBDIR}/{fol}/{f}") and f.endswith("py")]
    for snek in currentfiles:
        filesFound.append(snek)
# allows 1-deep folders for easy organisation. if folders is ["aa", "bb"]
# then it (for example) outputs nestedFiles as
# X [["SUBDIR/aa/uno.py", "SUBDIR/aa/dos.py"],["SUBDIR/bb/tres.py", "SUBDIR/bb/cuatro.py"]]
# ["SUBDIR/aa/uno.py", "SUBDIR/aa/dos.py", "SUBDIR/bb/tres.py", "SUBDIR/bb/cuatro.py"]
# now i dont have to loop a 2D array!
listButtons = [(f"{a}", a) for a in filesFound]
#print(listButtons)
cFile = shortcuts.radiolist_dialog(title="choose snippet",
                                     text="what snippet do you want to run?",
                                     values=listButtons).run()
#print(cFile)
runFile = f"{SUBDIR}/{cFile}" #keeps the real file name as cFile i guess
modifiers = shortcuts.checkboxlist_dialog(title="Modifiers",
                                          values=[("timeit", "Measure time?"),
                                                  ("args", "Change arguments?"),
                                                  ("stdin", "choose stdin?"),
                                                  ("stdout", "Choose stdout?"),
                                                  ("stderr", "Choose stderr?")]).run()
arguments = ""
if "args" in modifiers:
    arguments = shortcuts.input_dialog(title="Argument selection").run()
maybeIn = ""
if "stdin" in modifiers:
    chooseIn = shortcuts.input_dialog(title="stdin", text="Select input file in {SUBDIR}/_data").run()
    maybeIn = f"< {SUBDIR}/_data/{chooseIn}"
maybeOut = ""
pathToLogs = f"{SUBDIR}/_output/{cFile}/"
if "stdout" in modifiers:
    realOuts = []
    modTimes = []
    
    for slot in range(10):
        slotName = f"{pathToLogs}out{slot}.txt" #ptl ends with a /
        if os.path.isfile(slotName):
            realOuts.append(slotName)
            modTimes.append(os.path.getmtime(slotName))
            #print(f"{slotName} exists, made at {time.ctime(os.path.getmtime(slotName))}, stamp {os.path.getmtime(slotName)}") #wonky array workaround in case the files do not exist
        # print(f"{slotName}")
    #print(f"slots {realOuts} with modTimes {modTimes}")
    if len(realOuts) < 1 or len(modTimes) < 1:
        if not os.path.isdir(pathToLogs):
            print(f"creating dir {os.makedirs(pathToLogs)}")
        with open(f"{pathToLogs}out0.txt", "x") as o:
            o.write("") #establish new log file
            o.close
        targetSlot = f"{pathToLogs}out0.txt"
        print(f"made new file for log at {pathToLogs}")
    else:
        targetSlot = realOuts[modTimes.index(min(modTimes))] #finds the oldest output slot to overwrite
        #print(targetSlot)
    maybeOut = f"> {targetSlot}"            
maybeErr = ""
if "stderr" in modifiers:
    errSlots = [f"{pathToLogs}/err.txt",f"{pathToLogs}/lasterr.txt"]
    for eS in errSlots:
        if not os.path.isfile(eS):
            with open(eS, "x") as o:
                o.write("")
                o.close()
    if filecmp.cmp(errSlots[0], errSlots[1], shallow=False):
        pass
    else:
        errR = open(errSlots[0], "r")
        lastErrW = open(errSlots[1],"w")
        lastErrW.write(errR.read()) #shift newer error to file for later error
        errR.close()
        lastErrW.close()
    maybeErr = f"2> {errSlots[0]}"

finalCmd = f"{runFile} {arguments} {maybeIn} {maybeOut} {maybeErr}"
print(finalCmd)
if "timeit" in modifiers:
    if os.name == "posix":
        maybeTime = "time "
        print("posix time")
    else:
        maybeTime = "timecmd "
else:
    maybeTime = ""
os.system(f"{maybeTime}python {finalCmd}") # "waaa exec() bad!!!" here, have shell access
