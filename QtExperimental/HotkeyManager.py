from pynput import keyboard
from values import conversionTable, modifiers
from PyQt5.QtWidgets import *
import sys

SUCCESSFUL = "successful"
FAILED = "failed"
DUPLICATE = "duplicate"



class HotkeyManager:
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
                        self.listener._suppress = True
                        callback()
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
        self.hotkeys[name] = (keys, hotkeyCallback)

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


class HotKeyTestWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing hotkey")
        self.setGeometry(100, 100, 400, 400)
        manager = HotkeyManager(debug=False)
        manager.start()
        manager.setHotkey("testing", {48}, lambda: print("detected!!!!!!"))
        manager.setHotkey("the other one", {164, 165}, lambda: print("the other one detected!!"))
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