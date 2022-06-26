modifiers = [16, 17, 18, 91]

modCode = {16: 0x0004, 17: 0x0002, 18: 0x0001, 91: 0x0008}

NOREPEAT = 0x4000

import os
from PyQt5 import QtCore

from PyQt5.QtCore import QObject

defaultConfigPath = os.path.join(os.getenv("appdata"), "screenCap")


conversionTable = {
    8: "backspace",
    9: "tab",
    12: "clear",
    13: "enter",
    16: "shift",
    17: "ctrl",
    18: "alt",
    19: "pause",
    20: "caplock",
    27: "esc",
    32: "space",
    33: "page_up",
    34: "page_down",
    35: "end",
    36: "home",
    37: "left",
    38: "up",
    39: "right",
    40: "down",
    41: "select",
    42: "print",
    44: "prtscr",
    45: "insert",
    46: "del",
    48: "0",
    49: "1",
    50: "2",
    51: "3",
    52: "4",
    53: "5",
    54: "6",
    55: "7",
    56: "8",
    57: "9",
    65: "a",
    66: "b",
    67: "c",
    68: "d",
    69: "e",
    70: "f",
    71: "g",
    72: "h",
    73: "i",
    74: "j",
    75: "k",
    76: "l",
    77: "m",
    78: "n",
    79: "o",
    80: "p",
    81: "q",
    82: "r",
    83: "s",
    84: "t",
    85: "u",
    86: "v",
    87: "w",
    88: "x",
    89: "y",
    90: "z",
    91: "windows",
    92: "right windows",
    93: "menu key",
    96: "num_0",
    97: "num_1",
    98: "num_2",
    99: "num_3",
    100: "num_4",
    101: "num_5",
    102: "num_6",
    103: "num_7",
    104: "num_8",
    105: "num_9",
    106: "num_*",
    107: "num_+",
    108: "seperator",
    109: "num_-",
    110: "num_decimal",
    111: "num_/",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    124: "F13",
    125: "F14",
    126: "F15",
    127: "F16",
    128: "F17",
    129: "F18",
    130: "F19",
    131: "F20",
    132: "F21",
    133: "F22",
    134: "F23",
    135: "F24",
    144: "numlock",
    145: "scoll_lock",
    160: "lshift",
    161: "rshift",
    162: "lctrl",
    163: "rctrl",
    164: "lalt",
    165: "ralt",
    166: "browser_back",
    167: "browser_forward",
    168: "browser_refresh",
    169: "browser_stop",
    170: "search",
    173: "mute",
    174: "vol_down",
    175: "vol_up",
    176: "next_track",
    177: "previous_track",
    178: "stop",
    179: "play_pause",
    180: "mail",
    181: "media",
    186: ";",
    187: "=",
    188: ",",
    189: "-",
    190: ".",
    191: "?",
    192: "~",
    219: "[",
    220: "\\",
    221: "]",
    222: "quote",
}

keycodeTable = {item[1]: item[0] for item in conversionTable.items()}

#!! circular imports
from snapshot import Snapshot

rightclickOptions = {
    "Copy": Snapshot.copy,
    "Cut": Snapshot.cut,
    "Save": Snapshot.saveImage,
    "Save (scaled)": Snapshot.saveImageScaled,
    "Save (w/Canvas)": Snapshot.saveImageWithCanvas,
    "Save (scaled w/Canvas)": Snapshot.saveImageWithCanvasScaled,
    "Close": Snapshot.close,
    "Crop": Snapshot.startCrop,
    "Toggle Painting": Snapshot.togglePaint,
    "Clear Canvas": Snapshot.clearCanvas
    
    # size options +-20%, reset
    # show recycling
    # show color picker
    # transparency options
    # advanced saving options
    # +more, these are place holder for now.
}


defaultVariables = {  # if im doing this again, these tuples should be dataclasses instead. but im not doing this again.
    "istartup": (0, "main"),
    "istartmin": (0, "main"),
    "imintray": (0, "main"),
    "iminx": (0, "main"),
    "iuserecycle": (0, "main"),
    "irecyclecapacity": (1, "main"),
    "isaveoption": (0, "main"),
    "ishowsaveprompt": (0, "main"),
    "ssavelocation": (os.getenv("HOME"), "main"),
    "iuselastsave": (0, "main"),
    #snapshot
    "iquality": (100, "snapshot"),
     "bfastcrop":(False, "snapshot"),
    # hotkeys
    "licapture": ([17, 49], "global"), #windows global key codes
    "licopy": ([17, 50], "local"),
    "licut": ([17, 88], "local"), 
    "liclose": ([27], "local"),
    "lipaint": ([80], "local"),
    "lisave": ([17, 83], "local"),
    "lizoom10": ([], "local"),
    "lishrink10": ([], "local"),
    "lizoom20": ([], "local"),
    "lishrink20":([] ,"local"),
    "lirecycle": ([], "global"),
    
    # painter   
    "isize": (5, "painter"),
    "ialpha": (100, "painter"),
    "lscolors": (
        [
            "#000000",
            "#ffffff",
            "#ff69b4",
            "#dc143c",
            "#fd6500",
            "#ffd600",
            "#a52a2a",
            "#32ee66",
            "#4169E1",
            "#8A2BE2",
            "#8A2BE2",
            "#8A2BE2",
            "#8A2BE2",
            "#8A2BE2",
            "#8A2BE2",
            
        ],
        "painter",
    ),
    # recycler
    "imaxsize": (10, "reycler"),
    # right click context menu
    "lsavailablecommands": (list(rightclickOptions.keys()), "right_menu"),
    "lscurrentcommands": ([], "right_menu"),
}

import sys
from os import path
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

class ThreadSignal(QObject):
    signal = QtCore.pyqtSignal()