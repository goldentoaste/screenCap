from typing import Iterable
from values import *
from PyQt5 import QtGui
from pynput import keyboard
from PyQt5.QtWidgets import *
import sys
import threading
import win32con
import ctypes
from ctypes import wintypes

byref = ctypes.byref
user32 = ctypes.windll.user32

SUCCESSFUL = "successful"
FAILED = "failed"
DUPLICATE = "duplicate"


class HotkeyManager1:
    def __init__(self, debug=False):
        self.listener = keyboard.Listener(
            win32_event_filter=self.eventFilter,
            suppress=False,
        )
        self.debug = debug

        self.hotkeys = (
            dict()
        )  # to be a dict of string of combo name mapped to set of vk codes
        self.recording = None
        self.keyStringCallback = None
        self.currentKeys = set()

    def eventFilter(self, message, data):
        if self.debug:
            if message != 257:
                print(chr(27) + "[2J")
            print("message: ", message, "data: ", data.vkCode)

        # if the event code is not for 'release key'
        if message != 257:
            self.currentKeys.add(data.vkCode)
            if self.recording:
                self.keyStringCallback(self.getKeyString(self.currentKeys))
            else:
                for keys, callback in self.hotkeys.values():
                    if keys == self.currentKeys:
                        self.listener._suppress = True if callback() else False
                        break
        else:
            # releasing a key.
            self.listener._suppress = False
            if self.recording:
                if self.currentKeys in [hotkey[0] for hotkey in self.hotkeys.values()]:
                    self.keyStringCallback(DUPLICATE)
                    del self.hotkeys[self.recording]
                    self.recording = None
                    return

                self.hotkeys[self.recording][0].update(self.currentKeys)
                self.keyStringCallback(SUCCESSFUL)
                self.recording = None
            else:
                try:
                    self.currentKeys.remove(data.vkCode)
                except KeyError as e:
                    print(
                        "attempting to remove a keycode that doesn't currently exist."
                    )

    def recordNewHotkey(self, name, hotkeyCallback, stringCallback):
        self.keyStringCallback = stringCallback
        self.recording = name
        self.currentKeys.clear()
        self.hotkeys[name] = (set(), hotkeyCallback)

    def setHotkey(self, name, keys, hotkeyCallback):
        """
        hotkeyCallback can return true to supress key press if detected.
        Note: callback will be called on a different thread.
        """
        temp = list(keys)
        for i in range(len(temp)):
            if type(temp[i]) is str:
                temp[i] = keycodeTable[temp[i]]
        self.hotkeys[name] = (set(temp), hotkeyCallback)

    def deleteHotkey(self, name):
        if self.hotkeys.pop(name, default="NotFound") == "NotFound":
            print(f"Hotkey {name} is not found.")

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def getKeyString(self, keys):
        return " + ".join(
            [conversionTable.get(key, "Unkown") for key in self.getSortedKeys(keys)]
        )

    def getSortedKeys(self, keys):
        def modKey(key):
            if key in modifiers:
                return 0
            return 1

        return sorted(keys, key=modKey)


class HotkeyManager(threading.Thread):
    def __init__(self):

        threading.Thread.__init__(self, daemon=True)

        self.hotkeys = dict()
        self.callbacks = dict()

        self.currentKey = None
        self.currentMods = set()

        self.recording = False
        self.index = 1

        self.keyStringCallback = None
        
        self.task = []
        

    def getModsCode(self, mods) -> int:
        num = 0
        for mod in mods:
            num |= modCode[mod]
        return num

    def _setHotkey(self, name, key: str or int, modifiers: Iterable, callback):
        """
        Set a hotkey with a pre-defined keys combinations.
        """
        print(threading.get_ident(), "in recording")
        self.currentKey = key if type(key) is int else keycodeTable[key]
        self.currentMods = {
            mod if type(mod) is int else keycodeTable[mod] for mod in modifiers
        }

        self.keyStringCallback = lambda s: ()
        self.recording = name
        self.callbacks[self.index] = callback
        self.hotkeys[name] = [self.index, None, set()]
        self._stopRecording()

    def _recordNewHotKey(self, name, hotkeyCallback, stringCallback):
        
        if self.recording:
            self._stopRecording()
        self.recording = name
        self.keyStringCallback = stringCallback
        self.currentKey = None
        self.currentMods.clear()
        self.hotkeys[name] = [self.index, None, set()]
        self.callbacks[self.index] = hotkeyCallback

    def _stopRecording(self):
        print(threading.get_ident(), "in stop recording")
        if self.recording and self.currentKey is not None:

            vals = (self.index, self.currentKey, self.currentMods)
            print(f"registering hotkey {vals[1]}")

            if not user32.RegisterHotKey(
                None,
                vals[0],
                self.getModsCode(vals[2]),
                vals[1],
            ):
                print(
                    f"registering hotkey {vals[1]} failed!",
                    "params:",
                    vals[0],
                    vals[1],
                    self.getModsCode(vals[2]),
                )
                self.keyStringCallback("None")
            else:
                for item in self.hotkeys.values():
                    if item[1] == self.currentKey and item[2] == self.currentMods:
                        self.keyStringCallback("Duplicate")
                else:
                    self.index += 1
                    self.hotkeys[self.recording][1] = self.currentKey
                    self.hotkeys[self.recording][2].update(self.currentMods)
                    self.recording = None
                    self.keyStringCallback("Success")
                    return

        # removing recording if not successful, return early otherwise
        user32.UnregisterHotKey(None, self.index)
        self.hotkeys.pop(self.recording)
        self.callbacks.pop(self.index)
        self.keyStringCallback("None")
        self.recording = None

    def _removeHotkey(self, name):
        try:
            item = self.hotkeys.pop(name)
            user32.UnregisterHotKey(None, item[0])
            self.callbacks.pop(item[0])
        except KeyError:
            print("such hotkey does not exist")

    def run(self):
        print(threading.get_ident(), "in run")
        try:
            print("event loop started")
            msg = wintypes.MSG()
            while user32.GetMessageW(byref(msg), None, 0, 0) != 0:
                print(msg.message)
                if msg.message == win32con.WM_HOTKEY:
                    func = self.callbacks.get(msg.wParam)
                    if func:
                        func()
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageA(byref(msg))
        finally:
            print("finished")
            for id in self.callbacks.keys():
                user32.UnregisterHotKey(None, id)

    def getKeyString(self, key, mods):
        return (
            " + ".join(
                [
                    conversionTable.get(key, "Unkown") if key is not None else ""
                    for key in self.getSortedKeys(mods + {key})
                ]
            )
            if key is not None
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
        if a0.isAutoRepeat:
            return

        if a0.nativeVirtualKey() in modifiers:
            self.currentMods.add(a0.nativeVirtualKey())
        else:
            self.currentKey = a0.nativeVirtualKey()

        self.keyStringCallback(self.getKeyString(self.currentKey, self.currentMods))

    def keyUp(self, a0: QtGui.QKeyEvent) -> None:
        """
        a0 should the forwarded key event from a Qt widget, for the
        purpose of recording hotkeys
        """
        if a0.nativeVirtualKey() in self.currentMods:

            self.currentMods.pop(a0.nativeVirtualKey())

        elif a0.nativeVirtualKey() == self.currentKey:
            self.currentKey = None

        self.keyStringCallback(self.getKeyString(self.currentKey, self.currentMods))
        pass


class HotKeyTestWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing hotkey")
        self.setGeometry(100, 100, 400, 400)
        manager = HotkeyManager()
        print(threading.get_ident(), "outside")
        manager.start()
        manager.setHotkey("testing 1", "a", {"ctrl"}, lambda: print("nice one!"))
        print(threading.get_ident(), "outside")
        # manager = HotkeyManager1(debug=False)
        # manager.start()
        # manager.setHotkey("testing", {17}, lambda: print("detected!!!!!!"))
        # manager.setHotkey(
        #     "the other one", {164, 165}, lambda: print("the other one detected!!")
        # )
        # manager.recordNewHotkey(
        #     "testing 2",
        #     lambda: print("newly binded key detected."),
        #     lambda msg: print(msg),
        # )
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HotKeyTestWindow()
    sys.exit(app.exec_())