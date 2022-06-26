from typing import Iterable
from values import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import sys
import threading
import win32con
import ctypes
from ctypes import wintypes
import time

byref = ctypes.byref
user32 = ctypes.windll.user32


class HotkeyManager(threading.Thread):
    def __init__(self, config = None):

        threading.Thread.__init__(self, daemon=True)

        self.hotkeys = dict()
        self.callbacks = dict()

        self.currentKey = None
        self.currentMods = set()
        self.allkeys = set()

        self.recording = False
        self.index = 1

        self.keyStringCallback = None

        self.task = []
        self.islocal = False
        
        self.config = config

    def getModsCode(self, mods) -> int:
        num = 0
        for mod in mods:
            num |= modCode[mod]
        return num

    def setHotkey(self, name, keys :Iterable, callback):
        keys = self.getSortedKeys(keys)
        if not keys:
            key = None
            modifiers = None
        else:
            key = keys[-1]
            modifiers = keys[:-1]
        self.task.append((self._setHotkey, [name, key, modifiers, callback], {}))

    def _setHotkey(self, name, key: str, modifiers: Iterable, callback):
        """
        Set a hotkey with a pre-defined keys combinations.
        """

        self.currentKey = key if type(key) is int else keycodeTable[key]
        
        self.currentMods = {
            mod if type(mod) is int else keycodeTable[mod] for mod in modifiers
        }

        self.keyStringCallback = lambda s: ()
        self.recording = name
        self.callbacks[self.index] = callback
        self.hotkeys[name] = [self.index, None, set()]
        self._stopRecording()

    def recordNewHotkey(self, name, hotkeyCallback, stringCallback, islocal=False):

        self.islocal = islocal
        self.task.append(
            (self._recordNewHotKey, [name, hotkeyCallback, stringCallback, islocal], {})
        )

    def _recordNewHotKey(self, name, hotkeyCallback, stringCallback, islocal):

        if self.recording:

            self._stopRecording()
        self.recording = name
     
        self.keyStringCallback = stringCallback
        self.currentKey = None
        self.currentMods.clear()
        self.hotkeys[name] = [self.index, None, set()]
        self.callbacks[self.index] = hotkeyCallback

    def stopRecording(self):
        self.task.append((self._stopRecording, [], {}))

    def _stopRecording(self):
        def clearFields():
            self.recording = None
            self.currentKey = None
            self.currentMods.clear()
            self.keyStringCallback = None
    
        if self.recording and self.currentKey is not None:

            vals = (self.index, self.currentKey, self.currentMods)

            if not self.islocal and not user32.RegisterHotKey(
                None,
                vals[0],
                self.getModsCode(vals[2]),
                vals[1],
            ):
            
                self.keyStringCallback("None")
                clearFields()

            else:
                for item in self.hotkeys.values():
                    if item[1] == self.currentKey and item[2] == self.currentMods:
                        self.keyStringCallback("Duplicate")
                        clearFields()
                else:
                    #success
                    self.index += 1
                    self.hotkeys[self.recording][1] = self.currentKey
                    self.hotkeys[self.recording][2].update(self.currentMods)
                    self.config[self.recording] =list(self.currentMods)+ [self.currentKey] 
                    clearFields()
                    return

        # removing recording if not successful, return early otherwise
        user32.UnregisterHotKey(None, self.index)
        self.hotkeys.pop(self.recording)
        self.callbacks.pop(self.index)
        self.keyStringCallback("None")
        clearFields()

    def _removeHotkey(self, name):
        try:
            item = self.hotkeys.pop(name)
            user32.UnregisterHotKey(None, item[0])
            self.callbacks.pop(item[0])
        except KeyError:
            print("such hotkey does not exist")

    def run(self):
        """
        http://timgolden.me.uk/python/win32_how_do_i/catch_system_wide_hotkeys.html
        thanks!
        """
        msg = wintypes.MSG()
        try:
            while True:
                if self.task:
                    func, args, kwargs = self.task.pop(0)
                    func(*args, **kwargs)
                if user32.PeekMessageA(byref(msg), None, 0, 0, 1) != 0:

                    if msg.message == win32con.WM_HOTKEY:
                        func = self.callbacks.get(msg.wParam)
                        if func and not self.recording:
                            func()
                    user32.TranslateMessage(byref(msg))
                    user32.DispatchMessageA(byref(msg))
                time.sleep(0.1)
        finally:
            for id in self.callbacks.keys():
                user32.UnregisterHotKey(None, id)

    def getKeyString(self, key, mods):
        return (
            " + ".join(
                [
                    conversionTable.get(key, "Unkown") if key else ""
                    for key in self.getSortedKeys(mods | ({key} if key else set())) #FIXME this is really bad and janky, more clearly define what key & mods is if using in another object
                ]
            )
            if key or mods
            else "None"
        )

    def getSortedKeys(self, keys):
        def modKey(key):
            if key in modifiers:
                return modifiers.index(key)
            return 10

        return sorted(keys, key=modKey)

    def keyDown(self, a0: QtGui.QKeyEvent) -> None:
        """
        a0 should the forwarded key event from a Qt widget, for the
        purpose of recording hotkeys
        """

        if a0.isAutoRepeat() or not self.recording:
            return

        if not self.allkeys:
            self.currentKey = None
            self.currentMods.clear()

        if a0.nativeVirtualKey() in modifiers:
            self.currentMods.add(a0.nativeVirtualKey())
        else:
            self.currentKey = a0.nativeVirtualKey()

        self.keyStringCallback(self.getKeyString(self.currentKey, self.currentMods))
        self.allkeys.add(a0.nativeVirtualKey())

    def keyUp(self, a0: QtGui.QKeyEvent) -> None:
        """
        a0 should the forwarded key event from a Qt widget, for the
        purpose of recording hotkeys
        """

        if not self.recording:
            return

        if a0.nativeVirtualKey() in self.currentMods and self.currentKey is None:
            self.currentMods.remove(a0.nativeVirtualKey())

        self.keyStringCallback(self.getKeyString(self.currentKey, self.currentMods))
        try:
            self.allkeys.remove(a0.nativeVirtualKey())
        except KeyError:
            self.allkeys.clear()


class HotKeyTestWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing hotkey")
        self.setGeometry(100, 100, 400, 400)
        self.manager = HotkeyManager()

        self.manager.start()
        self.manager.setHotkey("testing 1",  {"ctrl", "a",}, lambda: print("nice one!"))
        self.manager.setHotkey("testing 2",  {"ctrl","b",}, lambda: print("nice 2!"))
        self.manager.setHotkey("testing 3", {"num_*"}, lambda: print("nice b!"))

        self.show()

        l = QHBoxLayout()

        button = QPushButton("push me to stop")

        button.clicked.connect(lambda: self.manager.stopRecording())

        label = QLabel("empty label", self)
        l.addWidget(button)
        l.addWidget(label)
        self.setLayout(l)
        self.manager.recordNewHotkey(
            "testing recording",
            lambda: print("recorded hot stuff clicked"),
            lambda s: (label.setText(s), ""),
        )

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.manager.keyDown(a0)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.manager.keyUp(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HotKeyTestWindow()
    sys.exit(app.exec_())
