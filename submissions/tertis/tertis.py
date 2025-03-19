import os, sys

import ctypes, ctypes.wintypes
import subprocess, time, struct
import msvcrt
from sys import stdout
from random import sample
from math import ceil
from string import ascii_lowercase

VERSIONS = [(3, 6), (3, 7), (3, 8)]


SAVESCORES = True
SCOREFILE = "scores"

FONTSIZE = 3
WIDTH = 27
HEIGHT = 24


# 1 2 3 4 5 6 7
# I O T L J S Z
COLORS = ["0;255;255", "255;255;0", "128;0;128", "256;128;0", "0;0;255", "0;255;0", "255;0;0"]

MINOS = [
	[["    ","████","    ","    "], ["  █ ","  █ ","  █ ","  █ "], ["    ","    ","████","    "], [" █  "," █  "," █  "," █  "]],
	[[" ██"," ██","   "], [" ██"," ██","   "], [" ██"," ██","   "], [" ██"," ██","   "]],
	[[" █ ","███","   "], [" █ "," ██"," █ "], ["   ","███"," █ "], [" █ ","██ "," █ "]],
	[["  █","███","   "], [" █ "," █ "," ██"], ["   ","███","█  "], ["██ "," █ "," █ "]],
	[["█  ","███","   "], [" ██"," █ "," █ "], ["   ","███","  █"], [" █ "," █ ","██ "]],
	[[" ██","██ ","   "], [" █ "," ██","  █"], ["   "," ██","██ "], ["█  ","██ "," █ "]],
	[["██ "," ██","   "], ["  █"," ██"," █ "], ["   ","██ "," ██"], [" █ ","██ ","█  "]],
]

# Rotations
#   0
# 3   1
#   2

WALLKICK_JLSTZ = {
	"01" : [(0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)],
	"10" : [(0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)],
	"12" : [(0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)],
	"21" : [(0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)],
	"23" : [(0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)],
	"32" : [(0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)],
	"30" : [(0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)],
	"03" : [(0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)],
}

WALLKICK_I = {
	"01" : [(0, 0), (-2, 0), (+1, 0), (-2, -1), (+1, +2)],
	"10" : [(0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)],
	"12" : [(0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)],
	"21" : [(0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)],
	"23" : [(0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)],
	"32" : [(0, 0), (-2, 0), (+1, 0), (-1, -1), (+1, +2)],
	"30" : [(0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)],
	"03" : [(0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)],
}

INPUTS = {
	"RIGHT" : b"d",
	"LEFT" : b"a",
	"SOFT" : b"s",
	"HARD" : b"w",
	"RRIGHT" : b"\xe0M",
	"RLEFT" : b"\xe0K",
	"HOLD" : b" ",
	"ENTER" : b"\r",
}

lines = 0
goal = 5
top = 0
score = 0
level = -1

b2b = False

grid = [[0 for x in range(10)] for y in range(24)]
next = sample([i+1 for i in range(7)], 7)
hold = 0
holdblock = 0

bag = []

mino = 0
minoX = 0
minoY = 0
minoR = 0

keycooldown = 0


scores = []



def fetchScores():
	global scores, top
	if not os.path.exists(SCOREFILE):
		with open(SCOREFILE,"wb") as fc:
			fc.write(struct.pack("<I", 0))
	
	f = open(SCOREFILE,"rb")
	l = struct.unpack("<I", f.read(4))[0]
	scores = sorted([(f.read(3).decode("ascii"), struct.unpack("<I", f.read(4))[0]) for i in range(l)], key=lambda x: -x[1])
	top = 0 if len(scores) == 0 else scores[0][1]
	f.close()


def init():

	if SAVESCORES:
		fetchScores()
	
	initScreen()
	
	drawTitle()
	
	show = True
	enter = False
	while not enter:
		enter = msvcrt.kbhit() and msvcrt.getch() == INPUTS["ENTER"]
		stdout.write("\033[0;97;40m" if show else "\033[0;30;40m")
		stdout.write("\033[20;12HPRESS\033[21;13HENTER")
		stdout.flush()
		show = not show
		time.sleep(0.5)
	
	global level
	level = 1
	
	drawLayout()
	drawScores()
	drawGame()
	
	time.sleep(2)
	
	lost = False
	while not lost:
		lost = doRound()
	
	drawLayout()
	drawScores()
	drawGame()
	
	gameover()
	
	time.sleep(2)
	
	if SAVESCORES:
		scoreboard()
	time.sleep(180)


def initScreen():
	# This function will take control of the windows console and initialize to my liking
	# using the windows api through ctypes
	
	subprocess.call("", shell=True)
	
	class COORD(ctypes.Structure):
		_fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
	
	class CONSOLE_FONT_INFOEX(ctypes.Structure):
		_fields_ = [("cbSize", ctypes.c_ulong),
					("nFont", ctypes.c_ulong),
					("dwFontSize", COORD),
					("FontFamily", ctypes.c_uint),
					("FontWeight", ctypes.c_uint),
					("FaceName", ctypes.c_wchar * 32)]
	
	font = CONSOLE_FONT_INFOEX()
	font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
	font.dwFontSize.X = 8 * FONTSIZE
	font.dwFontSize.Y = 8 * FONTSIZE
	font.FaceName = "Terminal"
	
	rect = ctypes.wintypes.SMALL_RECT(0, 0, WIDTH-1, HEIGHT-1)
	
	handle = ctypes.windll.kernel32.GetStdHandle(-11)
	ctypes.windll.kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.pointer(font))
	ctypes.windll.kernel32.SetConsoleWindowInfo(handle, True, ctypes.pointer(rect))
	ctypes.windll.kernel32.SetConsoleTitleW("Tertis")
	
	stdout.write("\033[2J")
	stdout.write("\033[3J")
	stdout.write("\033[?1049h")
	stdout.write("\033[?25l")
	
	stdout.flush()


def drawGame():
	
	global grid
	
	stdout.write("\033[23;10H")
	for y in range(20):
		for x in range(10):
			if grid[y][x] == 0:
				stdout.write("\033[0;40;30m█")
			else:
				stdout.write(f"\033[0;38;2;{COLORS[grid[y][x]-1]}m█")
		stdout.write("\033[1A\033[10D")
	
	stdout.write("\033[?25l")
	stdout.flush()


def drawScores():
	
	global lines, top, score, level
	
	stdout.write("\033[0;97;100m")
	stdout.write(f"\033[2;10HLines: {min(lines, 999):03}")
	stdout.write(f"\033[11;2HHigh\033[12;3H{min(top, 999999):06}")
	stdout.write(f"\033[14;2HScore\033[15;3H{min(score, 999999):06}")
	stdout.write("\033[21;2HLevel\033[22;3H" + (f"{min(level, 99):02}" if level > 0 else "--"))
	
	stdout.flush()


def drawLayout():

	#─│┌┐└┘┴├┼┤┬█░
	
	stdout.write("\033[1;1H\033[0;97;100m" + " " * (WIDTH * HEIGHT))
	stdout.write("\033[0;37;100m")
	stdout.write("\033[2;3H┌HOLD┐\033[1B\033[6D" + "│    │\033[1B\033[6D" * 4 + "└────┘")
	stdout.write("\033[2;21H┌NEXT┐\033[1B\033[6D" + "│    │\033[1B\033[6D" * 4 + "├────┤\033[1B\033[6D" + "│    │\033[1B\033[6D" * 15 + "└────┘")
	
	drawMino(next[0], 0, 4, 22)
	for i in range(5):
		drawMino(next[i+1], 0, 9 + i*3 , 22)
	
	drawMino(hold, 0, 4, 4)
	
	stdout.flush()


def drawTitle():
	
	drawLayout()
	drawScores()
	
	stdout.write("\033[0;40m")
	for i in range(20):
		stdout.write("\033[" + str(4+i) + ";10H" + " "*10)
	
	stdout.write("\033[0;97;40m\033[5;10H╔════════╗\033[6;10H║ TERTIS ║\033[7;10H╚════════╝")
	
	stdout.flush()


def gameover():
	# Fades away the game screen and draws GAME OVER
	
	stdout.write("\033[0;40;38;2;255;255;255m\033[6;13HGAME\033[7;13HOVER")
	
	for i in range(20):
		stdout.write("\033[" + str(23-i) + ";10H")
		for j in range(10):
			stdout.write("\033[48;2;80;80;80m" if (j + i) % 2 == 0 else "\033[48;2;100;100;100m")
			stdout.write("   GAME   "[j] if i == 17 else ("   OVER   "[j] if i == 16 else " "))
		stdout.flush()
		time.sleep(0.05)


def scoreboard():
	# Transition into the scoreboard screen, draw the scoreboard, take the player's name, save their score and wait forever
	
	global scores, score
	
	while msvcrt.kbhit():
		msvcrt.getch()
	
	for i in range(24):
		stdout.write(f"\033[{i+1};1H\033[0;40m" + " "*27)
		stdout.flush()
		time.sleep(0.05)
	
	stdout.write("\033[0;95;40m\033[2;9HHigh  Scores")
	stdout.write("\033[0;97;40m\033[4;4HEnter name:")
	stdout.write("\033[0;38;2;255;130;0m\033[8;4HRANK   NAME       SCORE")
	
	pos = 0
	for i, s in enumerate(scores):
		if s[1] >= score:
			pos += 1
		else:
			break
	
	scores.insert(pos, (" - ", score))
	
	c = ["230;50;255", "0;200;255", "0;200;255", "90;220;100", "90;220;100", "255;255;255"]
	for i in range(10):
		stdout.write(f"\033[{i + 10};3H\033[38;2;{c[min(5, i)]}m")
		stdout.write(f"{i+1:3}" + ["ST", "ND", "RD", "TH"][min(3, int(str(i)[-1]))])
		if len(scores) > i:
			stdout.write(f"\033[0;97;40m   {scores[i][0]}   " + " "*(10-len(str(scores[i][1]))) + str(scores[i][1]))
	
	stdout.flush()
	
	show = True
	name = ""
	while True:
		stdout.write("\033[0;97;40m" if show else "\033[0;30;40m")
		stdout.write("\033[4;2H>")
		stdout.write(f"\033[0;36;40m\033[4;16H{(name + '___')[:3]}")
		stdout.flush()
		show = not show
		if msvcrt.kbhit():
			u = msvcrt.getch()
			if u.lower() in bytes(ascii_lowercase, "ascii"):
				name = (name + u.decode("ascii").upper())[:3]
			elif u == b'\x08':
				name = name[:-1]
			elif u == INPUTS["ENTER"] and len(name) == 3:
				break
		time.sleep(0.1)
	
	stdout.write("\033[0;37;40m\033[4;2H" + " "*17)
	stdout.flush()
	
	f = open(SCOREFILE,"wb")
	f.write(struct.pack("<I", len(scores)))
	for s in scores:
		if s[0] == " - ":
			s = (name, score)
		f.write(bytes(s[0], "ascii"))
		f.write(struct.pack("<I", s[1]))
	f.close()
	
	# Flash the player's score forever to satisfy their ego of a good tetris player 
	show = True
	while True:
		stdout.write(f"\033[{min(9, pos) + 10};2H")
		stdout.write("\033[0;38;2;255;200;0m>" if show else " ")
		stdout.write("\033[0;38;2;255;200;0m" if show else f"\033[38;2;{c[min(5, pos)]}m")
		stdout.write(f"{pos+1:3}" + ["ST", "ND", "RD", "TH"][min(3, int(str(pos)[-1]))])
		stdout.write(("\033[0;97;40m   " if not show else "   ") + name + "   " + " "*(10-len(str(score))) + str(score))
		stdout.flush()
		show = not show
		time.sleep(0.1)


def drawMino(id, rot, y, x, boundsY=0, alt=0):
	
	if id == 0:
		return
	stdout.write(f"\033[{y};{x}H")
	stdout.write(f"\033[0;38;2;{COLORS[id-1]}m")
	
	for i, r in enumerate(MINOS[id-1][rot]):
		for c in r:
			if c == " " or i + y < boundsY:
				stdout.write("\033[1C")
			elif alt == 1:
				stdout.write("░")
			elif alt == 2:
				stdout.write("X")
			else:
				stdout.write(c)
		stdout.write(f"\033[1B\033[{len(r)}D")
	stdout.flush()


def redrawGameMino(alt=False):
	
	global mino, minoX, minoY, minoR
	
	drawScores()
	drawGame()
	
	ytest = minoY
	while not checkCollision(mino, minoR, ytest-1, minoX):
		ytest -= 1
	drawMino(mino, minoR, 23 - ytest, minoX + 10, 4, alt=1)
	drawMino(mino, minoR, 23 - minoY, minoX + 10, 4, alt=2 if alt else 0)


def addscore(s, lvl=False, b2b=False):
	
	global score, top, level
	s *= level if lvl else 1
	s += s // 2 if b2b else 0
	score += s
	top = max(score, top)


def msgscore(s, alt=False):
	
	if alt:
		stdout.write("\033[18;2H\033[0;97;100;38;2;255;20;0m " + s)
	else:
		stdout.write("\033[17;2H\033[0;97;100;38;2;69;180;255m" + s)


def checkCollision(id, rot, y, x):
	# collisiion shit
	
	global grid
	
	if id == 0:
		return False
	for i, r in enumerate(MINOS[id-1][rot]):
		for j, c in enumerate(r):
			if c != " ":
				if x + j < 0 or x + j >= 10 or y - i < 0 or y - i >= 24:
					return True
				if grid[y-i][x+j] != 0:
					return True
	return False


def checkOOB(id, rot, y, x):
	# Check if the tetrimino is out of bounds (specifically for game over condition)
	
	if id == 0:
		return False
	for i, r in enumerate(MINOS[id-1][rot]):
		for j, c in enumerate(r):
			if y - i >= 20:
				return True
	return False


def pasteGrid():
	
	global mino, minoX, minoY, minoR
	global grid
	
	if mino == 0:
		return
	for i, r in enumerate(MINOS[mino-1][minoR]):
		for j, c in enumerate(r):
			if c != " ":
				grid[minoY-i][minoX+j] = mino


def waitInput(t):
	# Main VERY IMPORTANT function
	# Waits for input for a specific amount of time and executes every action taken by the player
	
	global mino, minoX, minoY, minoR
	global keycooldown
	global autorep, autorepcooldown, autorepcount
	global hold, holdblock
	
	s = int(ceil(120 * t))
	
	for i in range(s):
		while msvcrt.kbhit():
			k = msvcrt.getch()
			
			if k == b"\xe0" or k == b"000":
				k += msvcrt.getch()
			
			if k == INPUTS["LEFT"] and not checkCollision(mino, minoR, minoY, minoX-1):
				minoX -= 1
				keycooldown = 0
				redrawGameMino()
			elif k == INPUTS["RIGHT"] and not checkCollision(mino, minoR, minoY, minoX+1):
				minoX += 1
				keycooldown = 0
				redrawGameMino()
			elif k == INPUTS["RRIGHT"]:
				tempX = minoX
				tempY = minoY
				i = 0
				while checkCollision(mino, (minoR+1)%4, tempY, tempX) and i < 5:
					tempX = minoX
					tempY = minoY
					if mino == 1:
						tempX += WALLKICK_I[str(minoR) + str((minoR + 1) % 4)][i][0]
						tempY += WALLKICK_I[str(minoR) + str((minoR + 1) % 4)][i][1]
					else:
						tempX += WALLKICK_JLSTZ[str(minoR) + str((minoR + 1) % 4)][i][0]
						tempY += WALLKICK_JLSTZ[str(minoR) + str((minoR + 1) % 4)][i][1]
					i += 1
				if not checkCollision(mino, (minoR+1)%4, tempY, tempX):
					minoX = tempX
					minoY = tempY
					minoR = (minoR + 1) % 4
					keycooldown = 0
					redrawGameMino()
			elif k == INPUTS["RLEFT"]:
				tempX = minoX
				tempY = minoY
				i = 0
				while checkCollision(mino, (minoR-1)%4, tempY, tempX) and i < 5:
					tempX = minoX
					tempY = minoY
					if mino == 1:
						tempX += WALLKICK_I[str(minoR) + str((minoR + 1) % 4)][i][0]
						tempY += WALLKICK_I[str(minoR) + str((minoR + 1) % 4)][i][1]
					else:
						tempX += WALLKICK_JLSTZ[str(minoR) + str((minoR - 1) % 4)][i][0]
						tempY += WALLKICK_JLSTZ[str(minoR) + str((minoR - 1) % 4)][i][1]
					i += 1
				if not checkCollision(mino, (minoR-1)%4, tempY, tempX):
					minoX = tempX
					minoY = tempY
					minoR = (minoR - 1) % 4
					keycooldown = 0
					redrawGameMino()
			elif k == INPUTS["HARD"]:
				upperY = minoY
				while not checkCollision(mino, minoR, minoY-1, minoX):
					minoY -= 1
				addscore(2 * (upperY - minoY))
				keycooldown = float("inf")
				return
			elif k == INPUTS["SOFT"]:
				upperY = minoY
				while not checkCollision(mino, minoR, minoY-1, minoX):
					minoY -= 1
				addscore(upperY - minoY)
				minoY = min(minoY + 2, upperY)
				return
			elif k == INPUTS["HOLD"] and holdblock <= 0:
				if hold == 0:
					hold = mino
				else:
					next.insert(0, hold)
					hold = mino
				holdblock = 2
				return "SKIP"
		
		time.sleep(1 / 120)
		keycooldown += 1 / 120


def doRound():
	# Main VERY IMPORTANT function
	# Does a round (--> Spawn tetrimino, --> play with tetrimino, --> place tetrimino, --> rinse and repeat)
	
	global grid
	global next, bag
	global b2b, goal
	global lines, top, score, level
	global mino, minoX, minoY, minoR
	global keycooldown
	global hold, holdblock
	
	holdblock -= 1
	
	if len(bag) < 1:
		bag = sample([i+1 for i in range(7)], 7)
	
	mino = next[0]
	
	next.append(bag[0])
	del next[0]
	del bag[0]
	
	minoX = 3
	minoY = 21
	minoR = 0
	
	drawLayout()
	drawScores()
	drawGame()
	
	while True:
		redrawGameMino()
		
		## stdout.write("\033[1;1HX " + str(minoX) + "\033[2;1HY " + str(minoY))
		## stdout.write("\033[1;1H" + str(goal))
		## stdout.flush()
		
		msg = waitInput((0.8 - 0.007*(level-1))**(level-1))
		
		if msg == "SKIP":
			return False
		
		if not checkCollision(mino, minoR, minoY-1, minoX):
			minoY -= 1
			keycooldown = 0
		
		if keycooldown >= 0.5:
			keycooldown = 0
			redrawGameMino(True)
			
			time.sleep(0.1)
			
			pasteGrid()
			drawScores()
			drawGame()
			
			time.sleep(0.1)
			
			if checkOOB(mino, minoR, minoY, minoX):
				return True
			
			clines = []
			for y in range(24):
				line = 0
				for x in range(10):
					line += 0 if grid[y][x] == 0 else 1
				if line == 10:
					clines.append(y)
			
			if len(clines) > 0:
				if len(clines) == 1:
					msgscore("Single")
					if b2b:
						msgscore("B2B", True)
					addscore(100, True, b2b)
					goal -= 1 + lines/2
				elif len(clines) == 2:
					msgscore("Double")
					if b2b:
						msgscore("B2B", True)
					addscore(300, True, b2b)
					goal -= 2 + lines/2
				elif len(clines) == 3:
					msgscore("Triple")
					if b2b:
						msgscore("B2B", True)
					addscore(500, True, b2b)
					goal -= 3 + lines/2
				elif len(clines) == 4:
					msgscore("Tetris")
					if b2b:
						msgscore("B2B", True)
					addscore(800, True, b2b)
					goal -= 4 + lines/2
				
				while goal <= 0:
					level += 1
					goal += level * 5
				
				drawScores()
				
				for i in range(10):
					for j in clines:
						stdout.write(f"\033[0;38;2;255;255;255m\033[{23 - j};{10 + i}H/")
						stdout.flush()
					time.sleep(0.035)
				
				for i in range(10):
					for j in clines:
						stdout.write(f"\033[0;38;2;0;0;0m\033[{23 - j};{10 + i}H█")
						stdout.flush()
					time.sleep(0.035)
				for j in range(len(clines)):
					del grid[clines[j]-j]
					grid.append([0 for i in range(10)])
				b2b = True
			else:
				b2b = False
			
			lines += len(clines)
			
			break;
	
	drawScores()
	drawGame()
	
	return False

if __name__ == "__main__":
	try:
		init()
	except (KeyboardInterrupt, SystemExit):
		raise
