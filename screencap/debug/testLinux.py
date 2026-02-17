
from concurrent.futures import thread
import os
from selectors import EVENT_READ, DefaultSelector
import sys
from typing import final, override

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget
import evdev as ev
from glob import glob
import threading

def listReadableKeyBoards():
    kbs: list[str] = []

    paths = glob("/dev/input/event*")

    for p in paths:
        try:
            device = ev.InputDevice(p)
            caps = device.capabilities()
            
            if ev.ecodes.EV_KEY not in caps:
                device.close()
                continue

            if ev.ecodes.KEY_SPACE not in caps[ev.ecodes.EV_KEY]:
                device.close()
                continue

            kbs.append(p)


        except (PermissionError, OSError) as e:
            print(f"Error accessing device: {e}")
    return kbs

class LinuxKeyListner(QObject):
    
    keyEvent = Signal((QKeyEvent))

    def __init__(self, parent:QObject | None = None) -> None:
        super().__init__(parent)
        self.devices : list[ev.InputDevice[str]] = []
        self.selector : DefaultSelector = DefaultSelector()
        self.finished = False
        self.R, self.W = os.pipe()
        self.worker : threading.Thread | None = None

        self.destroyed.connect(lambda: self.onDestroy())

    def onDestroy(self):
        print("destroying linux key event listner")
        self.finished = True
        if self.worker:
            os.write(self.W, b"\x00")
            self.worker.join()

    def startListen(self, devices: list[str]):
        for d in devices:
            device = ev.InputDevice(d)
            self.devices.append(device)
            _ = self.selector.register(device, EVENT_READ)
        
        self.selector.register(self.R, EVENT_READ)

        self.worker = threading.Thread(target=self._listen) 
        self.worker.start()
        
        

    def _listen(self):
        '''
            run in thread to avoid blocking main thread.
        '''

        while not self.finished:
            for key, mask in self.selector.select():
                device = key.fileobj
                if device == self.R:
                    break
                for event in device.read():
                    print(ev.categorize(event))




class Tester(QWidget):

    def __init__(self) -> None:
        super().__init__(None)

        self.setGeometry(200, 200, 400, 400)
        self.show()

        kbs = listReadableKeyBoards()
        
        self.process = LinuxKeyListner(self)
        self.process.startListen(kbs)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        

if __name__  == '__main__':
    a = QApplication()
    t = Tester()
    sys.exit(a.exec())