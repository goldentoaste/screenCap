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

from tkinter import messagebox
from PIL import Image

import tkinter
import os
import sys
import ctypes
import tkinter as tk

import psutil


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


# main = tkinter.Tk()


# def newTop():
#     t = tkinter.Toplevel(main)
#     tkinter.Button(t, text="stuff", command=lambda: print("stuff")).pack()
#     iconImage = Image.open("icon.ico")
#     # menu = pystray.Menu(item("Quit", self.quit), item(
#     #     "Capture!", self.capture), item("show", self.show, default=True, visible=False))

#     main.withdraw()


# tkinter.Button(main, text="new window", command=newTop).pack()


# def stop(tray):
#     tray.shutdown()
#     main.quit()


# def show(tray):
#     tray.shutdown()
#     main.deiconify()


# programs = [program.name() for program in psutil.process_iter()]


# messagebox.showerror(title="program already running!",
#                      message=str(programs.count("testing.exe")))

# tkinter.Button(main, text="hide").pack()
# main.mainloop()
# input("hold up")

import tkinter as tk

def populate(frame):
    '''Put in some fake data'''
    for row in range(100):
        tk.Label(frame, text="%s" % row, width=3, borderwidth="1", 
                 relief="solid").grid(row=row, column=0)
        t="this is the second column for row %s" %row
        tk.Label(frame, text=t).grid(row=row, column=1)

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

root = tk.Tk()
canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
frame = tk.Frame(canvas, background="#ffffff")
vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)

vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4,4), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

populate(frame)

root.mainloop()