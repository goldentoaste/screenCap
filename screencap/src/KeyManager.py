

from datetime import datetime
from utils import Logger as L
import sys
from typing import Callable, Dict, List, Literal, Tuple, Union
from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QKeySequenceEdit, QLabel, QLineEdit, QVBoxLayout, QWidget
from ctypes import wintypes, POINTER, cast, windll
import win32con

user32 = windll.user32


class WinGlobalHotkey(QAbstractNativeEventFilter):
    modCodeMap = {16: 0x0004, 17: 0x0002, 18: 0x0001, 91: 0x0008}
    NO_REPEAT = 0x4000

    _instance : "WinGlobalHotkey | None" = None

    def __init__(self) -> None:
        super().__init__()
        self.index = 1
        self.callbacks : Dict[int, Tuple[Callable, Tuple]]= dict()
        self.mappedCallbacks : Dict[Tuple, Tuple[int, str]] = dict() # key tuple mapped back to (id, label)

        app = QApplication.instance()
        if app:
            app.installNativeEventFilter(self)

    @classmethod
    def getManager(cls):
        if not WinGlobalHotkey._instance:
            WinGlobalHotkey._instance = cls()

        return WinGlobalHotkey._instance

    def registerHotKey(self, label:str, modKeyCodes: List[int], keyCode: int, callback: Callable)-> Tuple[Literal[True], int] | Tuple[Literal[False], str]:
        '''
        return False when hotkey registration is unsuccessful, likely due to key combo is already reserved by system.
        '''
        keyTuple = (tuple(sorted(modKeyCodes)), keyCode)
        if keyTuple in self.mappedCallbacks:
            return (False, f"Hotkey already used by: {self.mappedCallbacks[keyTuple][1]}")

        modCode = WinGlobalHotkey.NO_REPEAT
        for key in modKeyCodes:
            if key not in WinGlobalHotkey.modCodeMap:
                L.log(f"Error, unsupported modifier: {key}")
                continue

            modCode |= WinGlobalHotkey.modCodeMap[key]

        res = user32.RegisterHotKey(
            None, # handle hotkey events in main thread,
            self.index,
            modCode,
            keyCode
        )

        if res == 0:
            L.log(f"Global hotkey registration failed, mods: {modKeyCodes}, key: {keyCode}, callback: {callback}")
            return (False, "Hotkey register failed, likely hotkey already used by system.")

        self.callbacks[self.index] = (callback, keyTuple)
        self.mappedCallbacks[keyTuple] = (self.index, label)
        self.index += 1

        return (True, self.index - 1)

    def unregisterHotkey(self, hotkeyId:int):
        if hotkeyId not in self.callbacks:
            L.log(f"Hotkey not yet registered: {hotkeyId}")
            return

        res = user32.UnregisterHotKey(None, hotkeyId)
        if res == 0:
            L.log(f"Failed to unregister hotkey using user32 api: {hotkeyId}")



    def nativeEventFilter(self, eventType: Union[QByteArray, bytes, bytearray, memoryview], message: int) -> object:
        msg = cast(int(message), POINTER(wintypes.MSG)).contents
        if msg.message == win32con.WM_HOTKEY:
            if msg.wParam in self.callbacks:
                self.callbacks[msg.wParam][0]()
            return True
        return False

class Test(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Hello Bread!"))
        self.layout().setContentsMargins(16, 16, 16, 16)

        x = QKeySequence()
        self.seq = QKeySequenceEdit()
        self.seq.setMaximumSequenceLength(1)
        self.seq.editingFinished.connect(lambda: print("edit finished"))
        self.seq.keySequenceChanged.connect(lambda seq: print(seq[0]))
        self.layout().addWidget(self.seq)
        self.show()

        '''
        hwnd,
        hotkey id,
        modifiers flags,
        virtual key code.
        '''

        res = WinGlobalHotkey.getManager().registerHotKey("tester", [], 0x2c, lambda: print("nice!", datetime.now().isoformat()))
        res2 = WinGlobalHotkey.getManager().registerHotKey("tester", [], 0x2c, lambda: print("nice2!", datetime.now().isoformat()))



if __name__ == "__main__":
    app = QApplication()
    main = Test(None)

    sys.exit(app.exec())