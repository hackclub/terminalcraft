from subsystems.debug import *
from subsystems.display import *
from subsystems.media import *
import time, os

debug = Debug()
displayData = MediaDisplayData(debug)
display = Display(debug)
media = Media(os.path.join("subsystems", "1155-crescendo.gif"))


i = 0
while True:
    # if abs(time.time() - lastUpdate) > 0.03:
    #     lastUpdate = time.time()
    #     debug.detail()
    displayData.setData(media.get(i % media.gifLength))
    display.render(displayData)
    i += 1