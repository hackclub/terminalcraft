import time

# config pynput
import pynput
from pynput.keyboard import Key
from pynput.keyboard import KeyCode
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
        if key == Key.esc:
            print(f"Detacted ESC, exiting.")
            print("#" * 20)
            return False
    except AttributeError:
        return
    
    # records 
    print("key detected:", key)
    stringName = ""
    if isinstance(key, Key):
        # Special keys have a .name attribute
        stringName = key.name
    elif isinstance(key, KeyCode):
        # Character keys have a .char attribute
        stringName = key.char
    if stringName:keyList.append((stringName, time.time()))



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