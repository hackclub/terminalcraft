from subsystems.camera import *
from subsystems.debug import *
from subsystems.display import *
from subsystems.inputs import *
from subsystems.mathutil import *
from subsystems.render import *
from subsystems.world import *
import time

debug = Debug()
camera = Camera(debug, 7,7,10)
world = WorldState(25)
renderer = Renderer(debug, camera, world)
display = Display(debug)

lastUpdate = 0
while True:
    if abs(time.time() - lastUpdate) > 0.03:
        lastUpdate = time.time()
        temp = renderer.render()
        display.render(temp)
        debug.detail()

    # position controls
    if keyPressed("w"):     camera.applyMovement( 0,-1, 0)
    if keyPressed("a"):     camera.applyMovement(-1, 0, 0)
    if keyPressed("s"):     camera.applyMovement( 0, 1, 0)
    if keyPressed("d"):     camera.applyMovement( 1, 0, 0)
    if keyPressed("shift"): camera.applyMovement( 0, 0,-1)
    if keyPressed("space"): camera.applyMovement( 0, 0, 1)

    # rotation controls
    if keyPressed("Up"):    camera.applyRotation(   0, 0.1)
    if keyPressed("Down"):  camera.applyRotation(   0,-0.1)
    if keyPressed("Left"):  camera.applyRotation(-0.1,   0)
    if keyPressed("Right"): camera.applyRotation( 0.1,   0)
