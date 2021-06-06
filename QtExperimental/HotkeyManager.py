from pynput import keyboard
from values import conversionTable, modifiers
from PyQt5.QtWidgets import *

import sys
class HotkeyManager:
    def __init__(self):
        self.listener = keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease,
            win32_event_filter=self.eventFilter,
            suppress=False,
        )

    def onPress(self, key):
        #print("-=-=-=-=-=-=-=-=-=-=-=-")
        print("press", key)

    def onRelease(self, key):
        print("release", key)

    def eventFilter(self, message, data):
        if message != 257: 
            print(chr(27) + "[2J")
        print("message: ", message, "data: ", data.vkCode)

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()


class HotKeyTestWindow(QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing hotkey")
        self.setGeometry(100, 100, 100, 100)
        manager = HotkeyManager()
        manager.start()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HotKeyTestWindow()
    sys.exit(app.exec_())