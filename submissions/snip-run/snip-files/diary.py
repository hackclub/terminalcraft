
from datetime import datetime
import os
import argparse
import re
import subprocess
def find_top_dir(f):
    dirlog = []
    dirlog.append(os.path.dirname(f))
    dirlog.append(os.path.dirname(dirlog[0]))
    if os.path.isfile(f"{dirlog[1]}/snip-run.py"):
        nested = False
    else:
        dirlog.append(os.path.dirname(dirlog[1]))
        if not os.path.isfile(f"{dirlog[2]}/snip-run.py"):
            raise FileNotFoundError(f"where tf am i? currently {dirlog[2]}, files {os.listdir(dirlog[2])}, d1 {dirlog[1]}")
        nested = True
    #print(f"{dirlog[-1]}, files {os.listdir(dirlog[-1])}, {nested}")
    dirlog[-1] = os.path.normpath(dirlog[-1]) #dont let print() gaslight you, normpath will
    dirlog[-2] = os.path.normpath(dirlog[-2]) #reduce it to single slashes
    l = len(dirlog[-1])+1 #+1 accounts for slash
    if len(dirlog[-1]) < len(dirlog[-2]):
        subdir = dirlog[-2][l:] #cut off the parent directories with l - second character inclusive for l=1
    else:
        subdir = "" #this should not ever happen
    return [dirlog[-1], dirlog[-2], subdir, nested] #second item is the SUBDIR
dirInfo = find_top_dir(__file__)
if dirInfo[-1]: #nested=true
    orgFolder = os.path.dirname(__file__)
    orgBase = os.path.basename(orgFolder)
    Spezifisch = f"{orgBase}/{os.path.basename(__file__)}"
    #print(f"nested, {Spezifisch}")
else:
    Spezifisch = os.path.basename(__file__)
    #print(f"not nested")
pathData = f"{dirInfo[1]}/_data/{Spezifisch}"
#print(pathData)
#boring parser things
parser = argparse.ArgumentParser(description="quickly write down entries in a diary",
                                 usage="diary [-n name] [-e editor_command] [-uf] entry")
parser.add_argument("entry",type=str, help="Diary entry")
parser.add_argument("--name", "-n", type=str, default="main",help="diary you are writing to")
parser.add_argument("--editor", "-e", type=str, help="command to invoke editor of your choice")
parser.add_argument("--unstructured", "-u", action="store_true", help="do not mark time or day, temporary diary")
parser.add_argument("--feel", "-f", type=int,
                    help="HWF emotion square, 2 digit number up to 22 for positive-energetic")
args = parser.parse_args()
# no more parser
diaryPath = f"{pathData}/{args.name}.txt"
editorCmd = f"{args.editor} {diaryPath}"
# time trickery
d = datetime.today()
t = datetime.now()
assembleDate = f"{d.day}-{d.month}-{d.year}"
dateMarkerPattern = r"^== \d.+"
compiledPattern = re.compile(dateMarkerPattern)
try:
    os.makedirs(pathData, exist_ok=True)
    with open(diaryPath, "x") as o:
        o.write("")
    with open(f"{pathData}/u0.txt", "x") as u:
        u.write("")
except FileExistsError:
    print(f"err, {diaryPath} is real, or maybe just u0")
openDiary = open(diaryPath, "a+")
def scan_rotat(file, assembled):
    rotat = reversed(file.readlines()) #reading from the end to encounter a date header
    for line in rotat:
        if compiledPattern.search(line):
            cut = line[3:-3]
            print(f"found line {line}, {cut} vs {assembled}")
            if cut == assembled:
                return False #controls "insert another date marker"
            else:
                return True #needs another date marker
    return True

if args.feel:
    if args.feel > 22 or args.feel < 0:
        feelTuple = (2,2) #"happy by default"
    else:
        feelStr = str(args.feel)
        if args.feel < 10:
            feelStr = "0"+feelStr
        feelTuple = (feelStr[0],feelStr[1])
    feelEnd = f"[{feelTuple[0]}-{feelTuple[1]}] "
    #print(feelEnd)
prepend = f"{feelEnd}{t.hour}:{t.minute} > "
if args.editor:
    tempName = f"{args.name}diaryentry_temp.txt"
    subprocess.run([args.editor, tempName])
    with open(tempName, "r") as tempHandle:
        finalEntry = tempHandle.read()
    os.remove(tempName)
else:
    finalEntry = args.entry
#data gathered
if args.unstructured: #no date headers, no info prepend
    with open(f"{pathData}/u0.txt", "a") as uFile:
        uFile.write(f"{finalEntry}\n\n")
else:
    prependEntry = prepend+finalEntry
    testScanRotat = scan_rotat(openDiary, assembleDate)
    if testScanRotat: # true = needs new date marker
        openDiary.write(f"== {assembleDate} ==\n")
    openDiary.write(prependEntry)
    print(f"wrote {prependEntry} to {diaryPath}, {testScanRotat}")
    