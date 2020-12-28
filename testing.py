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


root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", root.withdraw)
root.mainloop()
