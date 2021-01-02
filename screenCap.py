import gc
from tkinter.constants import END
from snapshot import Snapshot
from PIL import Image, ImageGrab, ImageTk
from win32com.client import Dispatch
from configparser import ConfigParser
from values import conversionTable, modifiers
from pynput import keyboard
from tkinter import Entry, IntVar, StringVar, Tk, Frame, Checkbutton, Button, TOP, LEFT, Label, BOTH, RIGHT, messagebox, X
import sys
import pythoncom
import ctypes
import os
from os import path, getenv, mkdir, remove
from infi.systray import SysTrayIcon
import infi.systray.win32_adapter as win32
import psutil

seperator = "(*)"
# replace with screenCap.exe if compiling to exe!
executable = "screenCap.exe"
iconName = "icon.ico"
configDir = path.join(getenv("appdata"),
                      "screenCap")
configFile = path.join(configDir, "config.ini")

shortCutDest = path.join(
    getenv("appdata"), "Microsoft\Windows\Start Menu\Programs\Startup")
shortCutFile = path.join(shortCutDest, "screenCap.lnk")


class MainWindow:

    def __init__(self):

        self.main = Tk()
        self.main.title("screenCap")
        self.initialize()
        self.main.mainloop()

    def initialize(self):
        programs = [program.name() for program in psutil.process_iter()]

        if programs.count('screenCap.exe') > 2:
            messagebox.showerror(title="program already running!",
                                 message="An instance of screenCap is already running, the program will not exit.")
            self.quit()

        # initialize variables
        self.config = ConfigParser()

        self.currentKeys = set()
        self.detect = False
        self.combo = []

        self.startup = IntVar()
        self.minimize = IntVar()
        self.startMin = IntVar()
        self.admin = IntVar()
        self.recycleSize = StringVar()

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
            # load recycle size into variable and entry field

            self.recycleSize.set(getIntConfig("recycleSize"))
            self.recycleEntry.delete(0, END)
            self.recycleEntry.insert(0, str(self.recycleSize.get()))

            self.combo = (getStrConfig("combo").split(seperator))
            self.hotkeyButton["text"] = getStrConfig("key_string")

        # updating things to reflect settings
        self.update()
        # withdraw if the program is to minimalize on startup
        if self.startMin.get() == 1:
            self.withdraw()
        # starting keyboard event listener
        listrener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release)
        listrener.start()

    def update(self):
        # updating ini file
        self.config.set("screenCap", "startup", str(self.startup.get()))
        self.config.set("screenCap", "minimize", str(self.minimize.get()))
        self.config.set("screenCap", "startMin", str(self.startMin.get()))
        self.config.set("screenCap", "combo",
                        "(*)".join([key for key in self.combo]))
        self.config.set("screenCap", "key_string", self.hotkeyButton['text'])
        self.config.set("screenCap", "admin", str(self.admin.get()))
        self.config.set("screenCap", "recycleSize",
                        str(self.recycleSize.get()))

        # write config to ini file
        if not path.isdir(configDir):
            mkdir(configDir)
        with open(configFile, 'w') as file:
            self.config.write(file)

        # setup startup shortcut
        if self.startup.get() == 1:
            pythoncom.CoInitialize()
            target = path.join(self.resource_path(
                path.dirname(path.abspath(__file__))), executable)
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortCutFile)
            shortcut.Targetpath = target
            shortcut.WindowStyle = 7
            shortcut.save()
        else:
            if path.isfile(shortCutFile):
                remove(shortCutFile)

        # setup on close action
        if self.minimize.get() == 1:
            self.main.protocol("WM_DELETE_WINDOW", self.withdraw)
        else:
            self.main.protocol("WM_DELETE_WINDOW", self.main.quit)

        # admin handle
        if self.admin.get() == 1:
            if not is_admin():
                selfPath = "" if hasattr(
                    sys, '_MEIPASS') else '"' + os.getcwd() + '\\screenCap.py' + '"'
                ctypes.windll.shell32.ShellExecuteW(
                    None, 'runas',
                    # execute with console since, in editor, console would not be captured otherwise
                    '"' + sys.executable + '"',
                    selfPath,  # leave empty for deployment
                    None, 1)
                self.main.destroy()

        # recycleSize handling
        badEntry = False
        try:
            self.recycleSize.set(int(self.recycleEntry.get()))
        except Exception:
            badEntry = True
        # ignore input/no update if input is not number/has issues
        if not badEntry and int(self.recycleEntry.get()) >= 0:
            pass

    def on_press(self, key):
        self.currentKeys.add(key)
        if self.detect:
            self.hotkeyButton.configure(text=self.getKeyString())
        elif all(c in [str(key) for key in self.currentKeys] for c in self.combo) and len(self.combo) > 0:
            self.capture()

    def on_release(self, key):
        if key in self.currentKeys:
            # and self.getVk(key) not in modifiers , so that modifier keys cant be used alone
            if self.detect:
                self.combo = [str(key) for key in self.getSortedKeys()]
                self.main.title(f"hotkey set to '{self.getKeyString()}'")
                self.detect = False

                #!!! update must be called before currentKeys is cleared
                self.update()
                self.currentKeys.clear()
                return True

            self.currentKeys.remove(key)

    def getKeyString(self):
        s = ""
        for k in self.getSortedKeys():
            s += conversionTable.get(self.getVk(k), "Unknown") + "+"
        return s[:-1]

    def capture(self):
        gc.collect()
        Snapshot(master=self).fromFullScreen()
        # self.test = Toplevel(self.main)
        # Button(self.test, text="stuff", command=lambda: print(
        #     "stuff happended")).pack()
        # self.test.attributes("-topmost", True)

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
        self.main.destroy()
        os._exit(0)

    def show(self):
        self.main.title("screenCap")
        self.main.deiconify()
        win32.DestroyWindow(self.tray._hwnd)

    def withdraw(self):
        menu = (("Capture!", None, lambda tray: self.capture()),
                ("show", None, lambda tray: self.show()), ("Quit", None, lambda tray: self.quit()))
        self.tray = SysTrayIcon(self.resource_path(
            iconName), "screenCap", menu, default_menu_index=1)
        self.detect = False
        self.tray.start()
        self.main.withdraw()

    def reset(self):
        self.combo.clear()
        self.hotkeyButton["text"] = ""
        self.update()
        self.main.title("hotkey cleared")

    def record(self):
        self.detect = True
        self.combo.clear()
        self.main.title("input new hotkey (do not exit!)")

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)

    def makeUI(self):
        self.frame0 = Frame(self.main)
        self.startUpCheck = Checkbutton(self.frame0, variable=self.startup, command=self.update,  text="run when computer starts?").pack(
            side=TOP, anchor="w", padx=10)

        self.minToTrayCheck = Checkbutton(
            self.frame0, variable=self.minimize,  command=self.update, text="minimize to tray when 'X' is pressed?").pack(side=TOP, anchor="w", padx=10)

        self.startMinCheck = Checkbutton(self.frame0, command=self.update, variable=self.startMin,
                                         text="start minimalized?").pack(side=TOP, anchor="w", padx=10)

        Checkbutton(self.frame0, text="Start as Admin?", variable=self.admin,
                    command=self.update).pack(side=TOP, anchor="w", padx=10)

        self.frame0.pack(side=TOP, anchor="w", expand=True, fill=BOTH)

        recycleFrame = Frame(self.main)
        Label(recycleFrame, text="Recycler capcity :").pack(side=LEFT)
        self.recycleEntry = Entry(recycleFrame, width=10, justify='center')
        self.recycleEntry.pack(side=LEFT)
        self.recycleEntry.bind('<Return>', lambda event: (
            self.recycleEntry.configure(state='disabled'), self.update()))
        self.recycleEntry.bind(
            "<Button-1>", lambda event: self.recycleEntry.configure(state='normal'))
        #Button(recycleFrame, text="Set", command=self.update).pack(side=LEFT)
        recycleFrame.pack(side=TOP, padx=10, pady=(0, 5), fill=X)

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
        self.exitButton = Button(self.frame3, text="Exit", command=self.quit).pack(
            side=RIGHT, anchor="e")
        self.aboutButton = Button(self.frame3, text="About").pack(
            side=RIGHT, anchor="e")

        self.frame3.pack(side=TOP, padx=10, pady=(
            10, 5), expand=True, fill=BOTH)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


MainWindow()
