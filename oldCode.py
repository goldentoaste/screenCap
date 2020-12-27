from tkinter import *
from tkinter import messagebox
from pynput import keyboard
from values import conversionTable, modifiers


main = Tk()

currentKeys = set()
detect = False
combo = []


main.title("ScreenCap")


def initialize():
    listrener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listrener.start()

def capture():
    print("hotkey detected!!!")

def getSortedKeys():

    def modKey(key):
        if getVk(key) in modifiers:
            return 0
        return 1
    return sorted(list(currentKeys), key= modKey)




def getVk(key):
    if "vk" in dir(key):
        return key.vk
    return key.value.vk


def getKeyString():
    s = ""
    for k in getSortedKeys():
        s += conversionTable[getVk(k)] + "+"
    return s[:-1]


def getComboString():
    s = ""
    for c in combo:
        s += conversionTable[getVk(c)] + "+"
    return s[:-1]


def on_press(key):

    currentKeys.add(key)
    if detect:
        hotkeyButton.configure(text=getKeyString())
    elif all(ckey in currentKeys for ckey in combo):
        capture()
            



def on_release(key):
    global detect, combo
    

    if key in currentKeys:
        if detect and getVk(key) not in modifiers:
            combo = getSortedKeys()
            main.title(f"hotkey set to '{getComboString()}'")
            detect = False
            currentKeys.clear()

            return True

        currentKeys.remove(key)


def reset():
    combo.clear()
    hotkeyButton["text"] = ""
    main.title("hotkey cleared")


def record():
    global detect, combo
    detect = True
    combo.clear()
    main.title("input new hotkey (do not exit!)")
    


frame0 = Frame(main)
startUpCheck = Checkbutton(frame0, text="run when computer starts?").pack(
    side=TOP, anchor="w", padx=10)
minToTrayCheck = Checkbutton(
    frame0, text="minimize to tray when 'X' is pressed?").pack(side=TOP, anchor="w", padx=10)

frame0.pack(side=TOP, anchor="w")

frame1 = Frame(main)
hotKeyLabel = Label(frame1, text="Hotkey for screen capture:").pack(side=LEFT)
hotkeyButton = Button(frame1, command=record, width=20)
hotkeyButton.pack(side=LEFT, fill=BOTH, expand=True)
hotkeyResetButton = Button(
    frame1, text="Reset", command=reset, width=5).pack(side=LEFT)
frame1.pack(side=TOP, fill=X, padx=10)


frame3 = Frame(main)
captureButton = Button(frame3, text="Capture!").pack(side=LEFT, anchor="w")
exitButton = Button(frame3, text="Exit", command=main.quit).pack(
    side=RIGHT, anchor="e")
aboutButton = Button(frame3, text="About").pack(side=RIGHT, anchor="e")

frame3.pack(side=TOP, padx=10, pady=(10, 5), expand=True, fill=X)
initialize()
main.mainloop()
