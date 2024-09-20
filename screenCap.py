import ctypes
import gc
import os
import sys
from configparser import ConfigParser
from os import getenv, mkdir, path, remove
from tkinter import Button, Checkbutton, Entry, Frame, IntVar, Label, StringVar, Tk, messagebox
from tkinter.constants import BOTH, END, LEFT, RIGHT, TOP, X

import infi.systray.win32_adapter as win32
import pythoncom
from infi.systray import SysTrayIcon
from pynput import keyboard
from win32com.client import Dispatch

from recycle import RecycleBin
from snapshot import Snapshot
from values import conversionTable, modifiers, resource_path

"""
datas=[('icon.ico', '.'), ('bread.cur', '.')],
             hiddenimports=['pkg_resources.markers','pkg_resources.py2_warn','pynput.keyboard._win32', 'pynput.mouse._win32', 'pkg_resources', 'setuptools.py33compat','setuptools.py27compat'],
"""

# lock files dont work, use mutex instead
mutexName = "screenCapLock"
mutex = ctypes.windll.kernel32.CreateMutexA(None,False,mutexName)

if ctypes.windll.kernel32.GetLastError() == 183:  # 183 means "ERROR_ALREADY_EXISTS"
    messagebox.showerror(title="error", message="An instance of screenCap is already running!")
    os._exit(0)


seperator = "(*)"
# replace with screenCap.exe if compiling to exe!
executable = "screenCap.exe"
iconName = "icon.ico"
configDir = path.join(getenv("appdata", ""), "screenCap")
configFile = path.join(configDir, "config.ini")

shortCutDest = path.join(getenv("appdata", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
shortCutFile = path.join(shortCutDest, "screenCap.lnk")


class MainWindow:
    def __init__(self):

        self.main = Tk()
        self.main.title("screenCap")
        self.initialize()
        self.main.mainloop()

    def initialize(self):
        # initialize variables
        self.config = ConfigParser()

        self.currentKeys = set()
        self.detect = False
        self.capturing = False
        self.combo = []
        self.vkCombo = set()

        self.startup = IntVar()
        self.minimize = IntVar()
        self.startMin = IntVar()
        self.admin = IntVar()
        self.recycleSize = StringVar()
        self.lastPath = StringVar()
        self.lastColor = StringVar()
        self.custColors = StringVar()
        self.hoverOpacity = StringVar()
        self.ihoverOpacity = 0
        # list of opended snapshot
        self.snaps = []
        self.bin: RecycleBin = None
        self.isOnTop = False

        # initialize icon
        self.main.iconbitmap(path.join(resource_path(iconName)))

        # reading config file
        self.main.resizable(False, False)
        self.makeUI()
        self.config.read(configFile, encoding="utf-8-sig")

        if not self.config.has_section("screenCap"):
            self.config.add_section("screenCap")

        def getIntConfig(section, default=0, low=0, high=9999999):
            # return min(high, max(low, int(self.config.getint("screenCap", section))))
            try:
                return min(high, max(low, int(self.config.getint("screenCap", section))))
            except Exception:
                return default

        def getStrConfig(section, default=""):
            try:
                return self.config.get("screenCap", section)
            except Exception:
                return default

        # init vals only if config exist
        # if path.isfile(configFile):
        self.startup.set(getIntConfig("startup"))
        self.minimize.set(getIntConfig("minimize"))
        self.startMin.set(getIntConfig("startMin"))
        self.admin.set(getIntConfig("admin"))
        self.lastPath.set(getStrConfig("lastPath", default=configDir))
        self.lastColor.set(getStrConfig("lastColor", default="#ffffff"))
        self.custColors.set(getStrConfig("custColors", default="#ffffff"))

        self.hoverOpacity.set(str(getIntConfig("hoverCopacity", default=100, low=1, high=100)))
        self.opacityEntry.delete(0, END)
        self.opacityEntry.insert(0, str(self.hoverOpacity.get()))
        self.opacityEntry.configure(state="disabled")

        # load recycle size into variable and entry field
        self.recycleSize.set(str(getIntConfig("recycleSize", default=20)))
        self.recycleEntry.delete(0, END)
        self.recycleEntry.insert(0, str(self.recycleSize.get()))
        self.recycleEntry.configure(state="disabled")

        # key combo
        self.combo = getStrConfig("combo").split(seperator)
        vkList = getStrConfig("vkCombo", default="0").split(seperator)
        self.vkCombo = {int(key) for key in (vkList if vkList[0] != "" else [])}

        self.hotkeyButton["text"] = getStrConfig("key_string")

        # updating things to reflect settings
        self.update("all")


        # init system tray
        menu = (
            ("Capture!", None, lambda tray: self.capture()),
            ("Recycle Bin", None, lambda tray: self.bin.show()),  # type: ignore
            ("Show Window", None, lambda tray: self.show()),
        )
        self.tray = SysTrayIcon(
            resource_path(iconName), "screenCap", menu, default_menu_index=2, on_quit=lambda tray: self.quit()
        )
        self.tray.start()

        # withdraw if the program is to minimalize on startup
        if self.startMin.get() == 1:
            self.withdraw()

        # starting keyboard event listener
        self.listrener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,  # type: ignore
            win32_event_filter=self.event_filter,
            suppress=False,
        )
        self.listrener.start()

    def event_filter(self, msg, data):
        # not key up event
        if msg != 257 and data.vkCode in self.vkCombo:
            if {self.getVk(key) for key in self.currentKeys}.union({data.vkCode}) == self.vkCombo:
                self.listrener._suppress = True
        else:
            self.listrener._suppress = False
        return True

    def update(self, item):
        def lastColor():
            self.config.set("screenCap", "lastColor", str(self.lastColor.get()))

        def custColor():
            self.config.set("screenCap", "custColors", str(self.custColors.get()))

        def startUp():
            self.config.set("screenCap", "startup", str(self.startup.get()))
            if self.startup.get() == 1:
                pythoncom.CoInitialize()
                target = sys.argv[0]
                # target = path.join(resource_path(path.dirname(path.abspath(__file__))), executable)
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortCutFile)
                shortcut.Targetpath = target
                shortcut.save()
            else:
                if path.isfile(shortCutFile):
                    remove(shortCutFile)

        def minimize():
            self.config.set("screenCap", "minimize", str(self.minimize.get()))
            # setup on close action
            if self.minimize.get() == 1:
                self.main.protocol("WM_DELETE_WINDOW", self.withdraw)
            else:
                self.main.protocol("WM_DELETE_WINDOW", self.main.destroy)

        def startMin():
            self.config.set("screenCap", "startMin", str(self.startMin.get()))

        def combo():
            self.config.set("screenCap", "combo", "(*)".join([key for key in self.combo]))
            self.config.set("screenCap", "vkCombo", "(*)".join([str(key) for key in self.vkCombo]))
            self.config.set("screenCap", "key_string", self.hotkeyButton["text"])

        def admin():
            self.config.set("screenCap", "admin", str(self.admin.get()))
            saveConfig()
            # admin handle
            if self.admin.get() == 1:
                if not is_admin():
                    # for nuitka
                    # ctypes.windll.shell32.ShellExecuteW(
                    #     None,
                    #     "runas",
                    #     # execute with console since, in editor, console would not be captured otherwise
                    #     "".join(sys.argv),
                    #     "",  # leave empty for deployment
                    #     None,
                    #     None,
                    # )

                    # # for pyinstaller
                    selfPath = (
                        ""
                        if hasattr(sys, "_MEIPASS")
                        else '"' + os.getcwd() + "\\screenCap.py" + '"'
                    )
                    ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "runas",
                        # execute with console since, in editor, console would not be captured otherwise
                        '"' + sys.executable + '"',
                        selfPath,  # leave empty for deployment
                        None,
                        1,
                    )
                    self.main.destroy()

                    os._exit(0)

        def lastPath():
            self.config.set("screenCap", "lastPath", self.lastPath.get())

        def recycle():
            try:
                size = int(self.recycleEntry.get())
            except Exception:
                size = 0

            size = str(min(999, max(0, size)))
            self.recycleSize.set(size)
            self.recycleEntry.delete(0, END)
            self.recycleEntry.insert(0, size)

            self.config.set("screenCap", "recyclesize", str(size))
            if self.bin is None:
                self.bin = RecycleBin(int(self.recycleSize.get()), self)  # TODO change size instead of making a new one
            else:
                self.bin.size = int(self.recycleSize.get())
            self.recycleButton.configure(command=self.bin.show)

        def saveConfig():
            if not path.isdir(configDir):
                mkdir(configDir)
            with open(configFile, "w") as file:
                self.config.write(file)

        def hoverOpacity():
            try:
                size = int(self.opacityEntry.get())
            except Exception:
                size = 1

            self.ihoverOpacity = min(100, max(1, size))
            size = str(self.ihoverOpacity)
            self.hoverOpacity.set(size)
            self.opacityEntry.delete(0, END)
            self.opacityEntry.insert(0, size)

            self.config.set("screenCap", "hoverCopacity", size)

        mapping = {
            "startup": startUp,
            "minimize": minimize,
            "startmin": startMin,
            "combo": combo,
            "admin": admin,
            "lastpath": lastPath,
            "recycle": recycle,
            "lastColor": lastColor,
            "custColors": custColor,
            "hoverOpacity": hoverOpacity,
        }
        # execute all update methods
        if item == "all":
            for func in mapping.values():
                func()
            saveConfig()
            return None

        mapping.get(item, lambda: print)()
        saveConfig()

    def addSnap(self, snap: Snapshot):
        self.bin.addImage(snap.pilImage, snap.name)  # type: ignore

    def on_press(self, key):
        self.currentKeys.add(key)
        # print(self.getVk(key), "on_press")
        if self.detect:
            self.hotkeyButton.configure(text=self.getKeyString())
        elif (
            all(c in [str(key) for key in self.currentKeys] for c in self.combo)
            and len(self.combo) > 0
            and not self.capturing
        ):
            self.capture()
            self.capturing = True

    def on_release(self, key):
        # and self.getVk(key) not in modifiers , so that modifier keys cant be used alone
        if self.detect:
            self.combo = [str(key) for key in self.getSortedKeys()]
            self.vkCombo = {self.getVk(key) for key in self.currentKeys}
            self.main.title(f"hotkey set to '{self.getKeyString()}'")
            self.detect = False

            #!!! update must be called before currentKeys is cleared
            self.update("combo")
            self.currentKeys.clear()
            return True
        if str(key) in self.combo:
            self.capturing = False
        self.currentKeys.clear()

    def getKeyString(self):
        s = ""
        for k in self.getSortedKeys():
            s += conversionTable.get(self.getVk(k), "Unknown") + "+"
        return s[:-1]

    def capture(self):
        gc.collect()
        Snapshot(mainWindow=self).fromFullScreen()

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

    # quit, show, and withdraw is meant for handling system tray
    def quit(self):
        win32.DestroyWindow(self.tray._hwnd)
        os._exit(0)

    def show(self):
        self.main.title("screenCap")
        self.main.deiconify()

    def withdraw(self):
        self.detect = False
        self.main.withdraw()

    def reset(self):
        self.combo.clear()
        self.hotkeyButton["text"] = ""
        self.update("combo")

    def record(self):
        self.detect = True
        self.combo.clear()

    

    def makeUI(self):
        self.frame0 = Frame(self.main)
        self.startUpCheck = Checkbutton(
            self.frame0,
            variable=self.startup,
            command=lambda: self.update("startup"),
            text="Run on startup",
        ).pack(side=TOP, anchor="w", padx=10)

        self.minToTrayCheck = Checkbutton(
            self.frame0,
            variable=self.minimize,
            command=lambda: self.update("minimize"),
            text="Minimize to tray when 'X' is pressed?",
        ).pack(side=TOP, anchor="w", padx=10)

        self.startMinCheck = Checkbutton(
            self.frame0,
            command=lambda: self.update("startmin"),
            variable=self.startMin,
            text="Start minimized",
        ).pack(side=TOP, anchor="w", padx=10)

        Checkbutton(
            self.frame0,
            text="Start as Admin",
            variable=self.admin,
            command=lambda: self.update("admin"),
        ).pack(side=TOP, anchor="w", padx=10)

        self.frame0.pack(side=TOP, anchor="w", expand=True, fill=BOTH)

        recycleFrame = Frame(self.main)
        Label(recycleFrame, text="Recycling bin capacity : ").pack(side=LEFT)
        self.recycleEntry = Entry(recycleFrame, width=10, justify="center")
        self.recycleEntry.pack(side=LEFT)

        self.recycleEntry.bind(
            "<Return>",
            lambda event: (
                self.update("recycle"),
                self.recycleEntry.configure(state="disabled"),
            ),
        )
        self.recycleEntry.bind("<Button-1>", lambda event: self.recycleEntry.configure(state="normal"))
        recycleFrame.pack(side=TOP, padx=10, pady=(0, 5), fill=X)

        opacityFrame = Frame(self.main)
        Label(opacityFrame, text="Opacity on Hover(%) : ").pack(side=LEFT)
        self.opacityEntry = Entry(opacityFrame, width=10, justify="center")
        self.opacityEntry.pack(side=LEFT)
        self.opacityEntry.bind(
            "<Return>",
            lambda event: (
                self.update("hoverOpacity"),
                self.opacityEntry.configure(state="disabled"),
            ),
        )
        self.opacityEntry.bind("<Button-1>", lambda event: self.opacityEntry.configure(state="normal"))
        opacityFrame.pack(side=TOP, padx=10, pady=(0, 5), fill=X)

        self.frame1 = Frame(self.main)
        self.hotKeyLabel = Label(self.frame1, text="Hotkey for screen capture:").pack(side=LEFT)
        self.hotkeyButton = Button(self.frame1, command=self.record, width=20)
        self.hotkeyButton.pack(side=LEFT, fill=BOTH, expand=True)
        self.hotkeyResetButton = Button(self.frame1, text="Clear", command=self.reset, width=5).pack(side=LEFT)
        self.frame1.pack(side=TOP, fill=X, padx=10)

        self.frame3 = Frame(self.main)

        self.captureButton = Button(self.frame3, command=self.capture, text="Capture").pack(side=LEFT, anchor="w")
        self.recycleButton = Button(self.frame3, text="Recycling bin")
        self.recycleButton.pack(side=LEFT, anchor="w", padx=5)

        self.pinButton = Button(
            self.frame3,
            text="Pin",
        )
        self.pinButton.pack(side=LEFT, anchor="w", padx=5)

        def pin():
            self.isOnTop = not self.isOnTop
            self.main.attributes("-topmost", self.isOnTop)
            self.pinButton.config(text="Pin: " + ("✓" if self.isOnTop else "✗"))

        self.pinButton.config(command=pin)

        self.exitButton = Button(self.frame3, text="Exit", command=self.quit).pack(side=RIGHT, anchor="e")

        self.aboutButton = Button(
            self.frame3,
            text="About",
            command=lambda: messagebox.showinfo(
                title="About/Help",
                message="Program by Ray Gong, 2024\nContact: rayg2375@gmail.com\n\nFor info and usage see:\ngithub.com/goldentoaste/screenCap\n\nVersion 1.2",
            ),
        ).pack(side=RIGHT, anchor="e")

        self.frame3.pack(side=TOP, padx=10, pady=(10, 5), expand=True, fill=BOTH)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    try:
        main = MainWindow()
    except Exception as e:
        print(e)
        input("press any to continue")
