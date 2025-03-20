# import random, time
# import os, platform

# def minmax(lower, value, upper):
#     return max(lower, min(value, upper))

# def color(fr,fg,fb,br,bg,bb):
#     return "\033[38;2;{};{};{};48;2;{};{};{}m".format(minmax(0, round(fr), 255), minmax(0, round(fg), 255), minmax(0, round(fb), 255), minmax(0, round(br), 255), minmax(0, round(bg), 255), minmax(0, round(bb), 255))

# tick = 0
# while True:
#     os.system("cls" if platform.system() == "Windows" else "clear")
#     print("\033[0m")
#     pixel = "▀"
#     for i in range(10):
#         print("".join([color(((i+ie+tick)%20)*255/20, ((i-ie+tick)%20)*255/20, ((i+ie-tick)%20)*255/20, ((i+ie+tick+1)%20)*255/20, ((i-ie+tick-1)%20)*255/20, ((i+ie-tick+1)%20)*255/20) + pixel for ie in range(20)]))
#     print("\033[0m")
#     print("tick {}".format(tick))
#     tick += 1
#     time.sleep(0.025)


from subsystems.render import *
from subsystems.debug import *

debug = Debug()
displayData = DisplayData(debug)

displayData.drawLine(0,0,20,20.2,Block.GRASS,5)
debug.detail()