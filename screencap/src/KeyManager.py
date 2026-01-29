


import sys
from typing import Union
from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget
from ctypes import wintypes, POINTER, cast, windll
import win32con
user32 = windll.user32


import threading
class LineEdit(QLineEdit):
    '''
    init string, parent.
    or just parent.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("type here...")

        # QApplication.instance().installNativeEventFilter(HotKeyMonitor())

    # def keyPressEvent(self, e: QKeyEvent) -> None:
    #     # print(e.key())
    #     e.accept()
    #     return super().keyPressEvent(e)




class HotKeyMonitor(QAbstractNativeEventFilter):

    def __init__(self) -> None:
        print("init")
        super().__init__()


    def nativeEventFilter(self, eventType: Union[QByteArray, bytes, bytearray, memoryview], message: int) -> object:
        msg = cast(int(message), POINTER(wintypes.MSG)).contents
        if msg.message == win32con.WM_HOTKEY:
            print(msg.message, msg.wParam)
            return True
        return False

class Test(QWidget):

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__()
        print("window0", threading.get_native_id())
        self.setLayout(QVBoxLayout())
        self.inputField = LineEdit()
        self.layout().addWidget(QLabel("Test keyinput: "))
        self.layout().addWidget(self.inputField)

        self.layout().setContentsMargins(16, 16, 16, 16)

        self.show()

        '''
        hwnd,
        hotkey id,
        modifiers flags,
        virtual key code.
        '''
        res = user32.RegisterHotKey(
            None,
            2,
            0x0000,
            0x32
        )
        print("res; ", res)




if __name__ == "__main__":

    app = QApplication()
    filter = HotKeyMonitor()
    app.installNativeEventFilter(filter)
    main = Test(None)

    sys.exit(app.exec())