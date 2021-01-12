import gc
from tkinter.constants import END, TOP, LEFT, BOTH, X, RIGHT
from snapshot import Snapshot
from win32com.client import Dispatch
from configparser import ConfigParser
from values import conversionTable, modifiers
from pynput import keyboard
from tkinter import (
    Entry,
    IntVar,
    StringVar,
    Tk,
    Frame,
    Checkbutton,
    Button,
    Label,
    messagebox,
)
import sys
import pythoncom
import ctypes
import os
from os import path, getenv, mkdir, remove
from infi.systray import SysTrayIcon
import infi.systray.win32_adapter as win32
from recycle import RecycleBin

# fmt : off
# this is important for tendo to load
os.environ["PBR_VERSION"] = "4.0.2"
from tendo import singleton

# fmt : on
seperator = "(*)"
# replace with screenCap.exe if compiling to exe!
executable = "screenCap.exe"
iconName = "icon.ico"
configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")

shortCutDest = path.join(
    getenv("appdata"), "Microsoft\Windows\Start Menu\Programs\Startup"
)
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

        self.startup = IntVar()
        self.minimize = IntVar()
        self.startMin = IntVar()
        self.admin = IntVar()
        self.recycleSize = StringVar()
        self.lastPath = StringVar()
        # list of opended snapshot
        self.snaps = []
        # initialize icon
        self.main.iconbitmap(path.join(self.resource_path(iconName)))

        # reading config file
        self.main.resizable(0, 0)
        self.makeUI()
        self.config.read(configFile)
        if not self.config.has_section("screenCap"):
            self.config.add_section("screenCap")

        def getIntConfig(section, default=0):
            try:
                return self.config.getint("screenCap", section)
            except Exception:
                return default

        def getStrConfig(section, default=""):
            try:
                return self.config.get("screenCap", section)
            except Exception:
                return default

        # init vals only if config exist
        if path.isfile(configFile):
            self.startup.set(getIntConfig("startup"))
            self.minimize.set(getIntConfig("minimize"))
            self.startMin.set(getIntConfig("startMin"))
            self.admin.set(getIntConfig("admin"))
            self.lastPath.set(getStrConfig("lastPath", default=configDir))
            # load recycle size into variable and entry field

            self.recycleSize.set(getIntConfig("recycleSize"))
            self.recycleEntry.delete(0, END)
            self.recycleEntry.insert(0, str(self.recycleSize.get()))
            self.recycleEntry.configure(state="disabled")
            self.combo = getStrConfig("combo").split(seperator)
            self.hotkeyButton["text"] = getStrConfig("key_string")

        # updating things to reflect settings
        self.update("all")

        # singleton should be established after update, in  initialize, so that if the code aborts in update(restart as admin), it will not
        # be labeled as singleton. Works for both IDE and compiled exe.

        try:
            self.me = singleton.SingleInstance()
        except singleton.SingleInstanceException:
            messagebox.showerror(
                title="error", message="An instance of screenCap is already running!"
            )
            os._exit(0)

        # withdraw if the program is to minimalize on startup
        if self.startMin.get() == 1:
            self.withdraw()
        # starting keyboard event listener
        listrener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        listrener.start()

    def update(self, item):
        def startUp():
            self.config.set("screenCap", "startup", str(self.startup.get()))
            if self.startup.get() == 1:
                pythoncom.CoInitialize()
                target = path.join(
                    self.resource_path(path.dirname(path.abspath(__file__))), executable
                )
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
            # write config to ini file
            if not path.isdir(configDir):
                mkdir(configDir)
            with open(configFile, "w") as file:
                self.config.write(file)

        def combo():
            self.config.set(
                "screenCap", "combo", "(*)".join([key for key in self.combo])
            )
            self.config.set("screenCap", "key_string", self.hotkeyButton["text"])

        def admin():
            self.config.set("screenCap", "admin", str(self.admin.get()))
            saveConfig()
            # admin handle
            if self.admin.get() == 1:
                if not is_admin():
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
            badEntry = False
            try:
                self.recycleSize.set(int(self.recycleEntry.get()))
                self.config.set("screenCap", "recyclesize", self.recycleEntry.get())
            except Exception:
                badEntry = True

            # ignore input/no update if input is not number/has issues
            if not badEntry and int(self.recycleEntry.get()) >= 0:
                self.bin = RecycleBin(int(self.recycleSize.get()), self)
                self.recycleButton.configure(command=self.bin.show)

        def saveConfig():
            with open(configFile, "w") as file:
                self.config.write(file)

        mapping = {
            "startup": startUp,
            "minimize": minimize,
            "startmin": startMin,
            "combo": combo,
            "admin": admin,
            "lastpath": lastPath,
            "recycle": recycle,
        }
        # execute all update methods
        if item == "all":
            for func in mapping.values():
                func()
            saveConfig()
            return None

        mapping.get(item, lambda: print())()
        saveConfig()

    def addSnap(self, snap: Snapshot):
        if snap is not None:
            self.snaps.append(snap)

    def removeSnap(self, snap: Snapshot):
        if snap in self.snaps:
            self.snaps.remove(snap)
            self.bin.addImage(snap.pilImage)

    def on_press(self, key):
        self.currentKeys.add(key)
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
        self.addSnap(Snapshot(mainWindow=self).fromFullScreen())

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

        for snap in self.snaps:
            self.removeSnap(snap)
        ## allow 2 second for sys to save images to recycling
        self.main.after(2000, os._exit(0))

    def show(self):
        self.main.title("screenCap")
        self.main.deiconify()
        win32.DestroyWindow(self.tray._hwnd)

    def withdraw(self):
        menu = (
            ("Capture!", None, lambda tray: self.capture()),
            ("Recycle Bin", None, lambda tray: self.bin.show()),
            ("Show Window", None, lambda tray: self.show()),
            ("Quit", None, lambda tray: self.quit()),
        )
        self.tray = SysTrayIcon(
            self.resource_path(iconName), "screenCap", menu, default_menu_index=2
        )
        self.detect = False
        self.tray.start()
        self.main.withdraw()

    def reset(self):
        self.combo.clear()
        self.hotkeyButton["text"] = ""
        self.update("combo")

    def record(self):
        self.detect = True
        self.combo.clear()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)

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
            command=lambda: self.update("starmin"),
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
        Label(recycleFrame, text="Recycling bin capacity :").pack(side=LEFT)
        self.recycleEntry = Entry(recycleFrame, width=10, justify="center")
        self.recycleEntry.pack(side=LEFT)

        self.recycleEntry.bind(
            "<Return>",
            lambda event: (
                self.update("recycle"),
                self.recycleEntry.configure(state="disabled"),
            ),
        )
        self.recycleEntry.bind(
            "<Button-1>", lambda event: self.recycleEntry.configure(state="normal")
        )
        # Button(recycleFrame, text="Set", command=self.update).pack(side=LEFT)
        recycleFrame.pack(side=TOP, padx=10, pady=(0, 5), fill=X)

        self.frame1 = Frame(self.main)
        self.hotKeyLabel = Label(self.frame1, text="Hotkey for screen capture:").pack(
            side=LEFT
        )
        self.hotkeyButton = Button(self.frame1, command=self.record, width=20)
        self.hotkeyButton.pack(side=LEFT, fill=BOTH, expand=True)
        self.hotkeyResetButton = Button(
            self.frame1, text="Clear", command=self.reset, width=5
        ).pack(side=LEFT)
        self.frame1.pack(side=TOP, fill=X, padx=10)

        self.frame3 = Frame(self.main)

        self.captureButton = Button(
            self.frame3, command=self.capture, text="Capture"
        ).pack(side=LEFT, anchor="w")
        self.recycleButton = Button(self.frame3, text="Recycling bin")
        self.recycleButton.pack(side=LEFT, anchor="w", padx=5)

        self.exitButton = Button(self.frame3, text="Exit", command=self.quit).pack(
            side=RIGHT, anchor="e"
        )

        self.aboutButton = Button(
            self.frame3,
            text="About",
            command=lambda: messagebox.showinfo(
                title="About/Help",
                message="Program by Ray Gong, 2021\nFor info and usage see:\ngithub.com/goldentoaste/screenCap",
            ),
        ).pack(side=RIGHT, anchor="e")

        self.frame3.pack(side=TOP, padx=10, pady=(10, 5), expand=True, fill=BOTH)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


MainWindow()
