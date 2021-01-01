# from configparser import ConfigParser
# config = ConfigParser()

# config.read('config.ini')
# config.add_section('main')
# config.set('main', 'key1', 'value1')
# config.set('main', 'key2', 'value2')
# config.set('main', 'key3', 'value3')

# with open('config.ini', 'w') as f:
#     config.write(f)
#     f.close()


# #testing sorting
# from functools import cmp_to_key
# def moreItems(l1, l2):
#     return len(l1) - len(l2)

# def keyFunc(l):
#     return len(l)

# stuff = [[1,3], [1,2,3,4,5],[1],[2],[3,3,3,3]]
# print(sorted(stuff, key=keyFunc)
# print(stuff)


# sort number before letters

# def numLetterKey(item):
#     if item in [1,2,3,4,5,6]:
#         return 0
#     return 1

# stuff = [1,3,"b","x",2,"x","a","f",3]
# print(sorted(stuff, key=numLetterKey))

import pystray
from PIL import Image
import infi.systray
from infi.systray.traybar import SysTrayIcon
from pynput import keyboard
import tkinter
from elevate import elevate
import os
import sys
import ctypes
import tkinter as tk


class testing:

    def __init__(self):
        self.var1 = 0
        self.text = "a"


# from enum import Enum


# class testEnum(Enum):
#     a = 0
#     b = 1
#     c = 2


# print(testEnum.a, type(testEnum.a))
# print(testEnum["a"])
# print(str(testEnum["a"]) + " this is a string!")
# input("press enter to exit")


# import tkinter
# from pynput import keyboard

# main = tkinter.Tk()

# tkinter.Button(main, text="text").pack()
# print(keyboard.Key.ctrl)
# main.mainloop()


# root = tk.Tk()
# root.protocol("WM_DELETE_WINDOW", root.withdraw)
# root.mainloop()


# print(__file__)
# input(">")
# ctypes.windll.shell32.ShellExecuteW(
#     None, 'runas', sys.executable, sys.argv[0], None, 1)

# print("check2")
# ???????????//


# def is_root():
#     return ctypes.windll.shell32.IsUserAnAdmin()


# print("before ", is_root())
# if not is_root():
#     ctypes.windll.shell32.ShellExecuteW(
#         None, 'runas',
#         '"' + sys.executable + '"',
#         '"' + os.getcwd() + '\\testing.py' + '"',  # leave empty for deployment
#         None, 1)

# main = tkinter.Tk()
# main.title(str(is_root()))
# tkinter.Button(main, text="text").pack()
# print(keyboard.Key.ctrl)
# main.mainloop()

# print("after ", is_root())
# input("press enter to exit")


main = tkinter.Tk()


def newTop():
    t = tkinter.Toplevel(main)
    tkinter.Button(t, text="stuff", command=lambda: print("stuff")).pack()
    iconImage = Image.open("icon.ico")
    # menu = pystray.Menu(item("Quit", self.quit), item(
    #     "Capture!", self.capture), item("show", self.show, default=True, visible=False))
    menu = pystray.Menu()
    icon = pystray.Icon(
        "screenCap", iconImage, "screenCap", menu)
    icon.run()
    main.withdraw()


tkinter.Button(main, text="new window", command=newTop).pack()


def stop(tray):
    tray.shutdown()
    main.quit()


def show(tray):
    tray.shutdown()
    main.deiconify()


def withDraw():
    tray = SysTrayIcon('icon.ico', "screenCap", (("show", None, show),), default_menu_index=0, on_quit=stop)
    tray.start()
    main.withdraw()


tkinter.Button(main, text="hide", command=withDraw).pack()
main.mainloop()
