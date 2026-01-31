

from screencap.src.Hotkeys.common import QT_KEY_TO_WIN_VK, HotkeyEdit, QT_NumPad_WIN_VK
from utils import Logger as L
import sys
from typing import Callable, Dict, List, Literal, Tuple, Union
from PySide6.QtCore import (
    QAbstractNativeEventFilter,
    QByteArray,
    QKeyCombination,
    Qt,

)

from PySide6.QtWidgets import (
    QApplication,

    QLabel,

    QListWidget,
    QVBoxLayout,
    QWidget,
)
from ctypes import wintypes, POINTER, cast, windll
import win32con

user32 = windll.user32


class WinGlobalHotkey(QAbstractNativeEventFilter):
    modCodeMap = {16: 0x0004, 17: 0x0002, 18: 0x0001, 91: 0x0008}
    QtModMap = {
        Qt.KeyboardModifier.AltModifier: 0x0001,
        Qt.KeyboardModifier.ControlModifier: 0x0002,
        Qt.KeyboardModifier.ShiftModifier: 0x0004,
        Qt.KeyboardModifier.MetaModifier: 0x0008,
    }
    NO_REPEAT = 0x4000

    _instance: "WinGlobalHotkey | None" = None

    def __init__(self) -> None:
        super().__init__()
        self.index = 1
        self.callbacks: Dict[int, Tuple[Callable, QKeyCombination]] = dict()
        self.mappedCallbacks: Dict[QKeyCombination, Tuple[int, str]] = (
            dict()
        )  # key tuple mapped back to (id, label)

        app = QApplication.instance()
        if app:
            app.installNativeEventFilter(self)

    @classmethod
    def getManager(cls):
        if not WinGlobalHotkey._instance:
            WinGlobalHotkey._instance = cls()

        return WinGlobalHotkey._instance

    def registerHotKey(
        self, label: str, keyCombo: QKeyCombination, callback: Callable
    ) -> Tuple[Literal[True], int] | Tuple[Literal[False], str]:
        """
        return False when hotkey registration is unsuccessful, likely due to key combo is already reserved by system.
        """

        if keyCombo in self.mappedCallbacks:
            return (
                False,
                f"Hotkey already used by: {self.mappedCallbacks[keyCombo][1]}",
            )

        modCode = WinGlobalHotkey.NO_REPEAT
        for key in WinGlobalHotkey.QtModMap:
            if keyCombo.keyboardModifiers() & key:
                modCode |= WinGlobalHotkey.QtModMap[key]

        keyCode = -1

        if keyCombo.keyboardModifiers() & Qt.KeyboardModifier.KeypadModifier:
            keyCode = QT_NumPad_WIN_VK[keyCombo.key()]
        else:
            keyCode = QT_KEY_TO_WIN_VK[keyCombo.key()]

        res = user32.RegisterHotKey(
            None, self.index, modCode, keyCode  # handle hotkey events in main thread,
        )

        if res == 0:
            L.log(
                f"Global hotkey registration failed, mods: {modCode}, key: {keyCode}, callback: {callback}"
            )
            return (
                False,
                "Hotkey register failed, likely hotkey already used by system.",
            )

        self.callbacks[self.index] = (callback, keyCombo)
        self.mappedCallbacks[keyCombo] = (self.index, label)
        self.index += 1

        return (True, self.index - 1)

    def unregisterHotkey(self, hotkeyId: int):
        if hotkeyId not in self.callbacks:
            L.log(f"Hotkey not yet registered: {hotkeyId}")
            return

        res = user32.UnregisterHotKey(None, hotkeyId)
        if res == 0:
            L.log(f"Failed to unregister hotkey using user32 api: {hotkeyId}")

        return res != 0

    def nativeEventFilter(
        self, eventType: Union[QByteArray, bytes, bytearray, memoryview], message: int
    ) -> object:
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
        self.setMinimumWidth(300)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.comboEdit = HotkeyEdit()
        self.listList = QListWidget()

        self.layout().addWidget(self.comboEdit)
        self.layout().addWidget(self.listList)

        self.keyManager = WinGlobalHotkey.getManager()

        self.comboEdit.comboChangeSignal.connect(self.regKey)

        self.show()

    def regKey(self, key: QKeyCombination):

        if self.comboEdit.id:
            UnRegRes = self.keyManager.unregisterHotkey(self.comboEdit.id)
            self.listList.insertItem(0, f"Unreg result: {UnRegRes}")

        self.listList.insertItem(0, f"RegKey: {key}")
        res = self.keyManager.registerHotKey(
            "Test",
            key,
            lambda: self.listList.insertItem(
                0, f"Hotkey activation: {self.comboEdit.id}"
            ),
        )
        self.listList.insertItem(0, f"Reg Result: {res}")
        if res[0]:
            self.comboEdit.id = res[1]  # pyright: ignore[reportAttributeAccessIssue]


if __name__ == "__main__":
    app = QApplication()
    main = Test(None)

    sys.exit(app.exec())
