import time

# config pynput
import pynput
from pynput.keyboard import Key
keys={
    "esc": Key.esc,
    "f1": Key.f1,
    "ctrl_l": Key.ctrl_l,
    "backspace": Key.backspace
}

# records everything
def listener(key, keyList:list):
    # check if exits
    try:
        if key == keys["esc"]:
            print("esc detacted")
            return False
    except AttributeError:
        return
    
    # records 
    print("key detected:", key)
    keyList.append((str(key), time.time()))



def listen():
    # init listens
    keyList = []
    keyListener = pynput.keyboard.Listener(on_press = lambda key : listener(key, keyList))
    keyListener.start()

     # actaully listens
    while keyListener.running:
        pass
    else:
        keyListener.stop()
        del keyListener
    
    return keyList