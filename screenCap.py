
import os
from tkinter import IntVar, Tk, Frame, Checkbutton, Button, TOP, LEFT, Label, BOTH, RIGHT, X
from pynput import keyboard
from values import conversionTable, modifiers
from configparser import ConfigParser
from win32com.client import Dispatch


seperator = "(*)"
# replace with screenCap.exe if compiling to exe!
executable = "screenCap.exe"
configDir = os.path.join(os.getenv("appdata"),
                         "screenCap")
configFile = os.path.join(configDir, "config.ini")

shortCutDest = os.path.join(
    os.getenv("appdata"), "Microsoft\Windows\Start Menu\Programs\Startup")
shortCutFile = os.path.join(shortCutDest, "screenCap.lnk")


class MainWindow:

    def __init__(self):

        self.main = Tk()

        self.config = ConfigParser()

        self.currentKeys = set()
        self.detect = False
        self.combo = []

        self.startup = IntVar()
        self.minimize = IntVar()
        self.startMin = IntVar()

        self.initialize()
        self.main.mainloop()

    def initialize(self):

        # reading config file
        self.makeUI()
        self.config.read(configFile)
        if not self.config.has_section("screenCap"):
            self.config.add_section("screenCap")
        # init vals only if config exist
        if os.path.isfile(configFile):
            self.startup.set(self.config.getint("screenCap", "startup"))
            self.minimize.set(self.config.getint("screenCap", "minimize"))
            self.startMin.set(self.config.getint("screenCap", "startMin"))
            self.combo = (self.config.get(
                "screenCap", "combo").split(seperator))
            self.hotkeyButton["text"] = self.config.get(
                "screenCap", "key_string")
        # starting keyboard event listener
        listrener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release)
        listrener.start()

    def updateConfig(self):
        # updating ini file
        self.config.set("screenCap", "startup", str(self.startup.get()))
        self.config.set("screenCap", "minimize", str(self.minimize.get()))
        self.config.set("screenCap", "startMin", str(self.startMin.get()))
        self.config.set("screenCap", "combo",
                        "(*)".join([key for key in self.combo]))
        self.config.set("screenCap", "key_string", self.getKeyString())

        # setup startup shortcut
        target = os.path.join(os.getcwd(), executable)
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortCutFile)
        shortcut.Targetpath = target
        shortcut.WindowStyle = 7
        shortcut.save()

        if not os.path.isdir(configDir):
            os.mkdir(configDir)
        with open(configFile, 'w') as file:
            self.config.write(file)

    def on_press(self, key):
        print(key)

        self.currentKeys.add(key)
        if self.detect:
            self.hotkeyButton.configure(text=self.getKeyString())
        elif all(c in [str(key) for key in self.currentKeys] for c in self.combo) and len(self.combo) > 0:
            self.capture()

    def on_release(self, key):
        if key in self.currentKeys:
            if self.detect and self.getVk(key) not in modifiers:
                self.combo = [str(key) for key in self.getSortedKeys()]
                self.main.title(f"hotkey set to '{self.getKeyString()}'")
                self.detect = False

                #!!! update must be called before currentKeys is cleared
                self.updateConfig()
                self.currentKeys.clear()
                return True

            self.currentKeys.remove(key)

    def getKeyString(self):
        s = ""
        for k in self.getSortedKeys():
            s += conversionTable.get(self.getVk(k), "Unknown") + "+"
        return s[:-1]

    def capture(self):
        print("combo detected")

    def getVk(self, key):
        if "vk" in dir(key):
            return key.vk
        return key.value.vk

    def getSortedKeys(self):
        def modKey(key):
            if self.getVk(key) in modifiers:
                return 0
            return 1
        return sorted(list(self.currentKeys), key=modKey)

    def reset(self):
        self.combo.clear()
        self.hotkeyButton["text"] = ""
        self.main.title("hotkey cleared")

    def record(self):
        self.detect = True
        self.combo.clear()
        self.main.title("input new hotkey (do not exit!)")

    def makeUI(self):
        self.frame0 = Frame(self.main)
        self.startUpCheck = Checkbutton(self.frame0, variable=self.startup, command=self.updateConfig,  text="run when computer starts?").pack(
            side=TOP, anchor="w", padx=10)

        self.minToTrayCheck = Checkbutton(
            self.frame0, variable=self.minimize,  command=self.updateConfig, text="minimize to tray when 'X' is pressed?").pack(side=TOP, anchor="w", padx=10)

        self.startMinCheck = Checkbutton(self.frame0, command=self.updateConfig, variable=self.startMin,
                                         text="start minimalized?").pack(side=TOP, anchor="w", padx=10)

        self.frame0.pack(side=TOP, anchor="w", expand=True, fill=BOTH)

        self.frame1 = Frame(self.main)
        self.hotKeyLabel = Label(
            self.frame1, text="Hotkey for screen capture:").pack(side=LEFT)
        self.hotkeyButton = Button(self.frame1, command=self.record, width=20)
        self.hotkeyButton.pack(side=LEFT, fill=BOTH, expand=True)
        self.hotkeyResetButton = Button(
            self.frame1, text="Reset", command=self.reset, width=5).pack(side=LEFT)
        self.frame1.pack(side=TOP, fill=X, padx=10)

        self.frame3 = Frame(self.main)
        self.captureButton = Button(self.frame3, command=self.capture, text="Capture!").pack(
            side=LEFT, anchor="w")
        self.exitButton = Button(self.frame3, text="Exit", command=self.main.quit).pack(
            side=RIGHT, anchor="e")
        self.aboutButton = Button(self.frame3, text="About").pack(
            side=RIGHT, anchor="e")

        self.frame3.pack(side=TOP, padx=10, pady=(
            10, 5), expand=True, fill=BOTH)


if __name__ == "__main__":
    main = MainWindow()
