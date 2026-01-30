import sys

from typing import Any, Optional
from PySide6.QtCore import QKeyCombination, Qt, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from screencap.src.Consts import (
    QT_KEY_TO_WIN_VK,
    QT_MODIFIERS,
    QT_SHIFT_NUMPAD_WIN_CASE,
    QT_SHIFT_WIN_CASE,
    QT_NumPad_WIN_VK,
)


class TestInput(QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        return super().keyPressEvent(arg__1)


class HotkeyEdit(QKeySequenceEdit):
    comboChangeSignal = Signal((QKeyCombination))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = -1

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)

        keyCombo = e.keyCombination()
        key = keyCombo.key()
        keyMod = keyCombo.keyboardModifiers()

        if key in QT_MODIFIERS:
            return

        if keyMod & Qt.KeyboardModifier.ShiftModifier:
            if key in QT_SHIFT_WIN_CASE:
                keyCombo = QKeyCombination(keyMod, QT_SHIFT_WIN_CASE[key])
            if key in QT_SHIFT_NUMPAD_WIN_CASE and not (
                keyMod & Qt.KeyboardModifier.KeypadModifier
            ):
                keyCombo = QKeyCombination(keyMod, QT_SHIFT_NUMPAD_WIN_CASE[key])

        self.setKeySequence(QKeySequence(keyCombo))
        self.comboChangeSignal.emit(keyCombo)

    def getHotkey(self):
        seq = self.keySequence()
        if seq.count() > 0:
            return seq[0]  # pyright: ignore[reportIndexIssue]
        return None

    def setId(self, id: int):
        self.id = id


class Tester(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, *rest: Any):
        super().__init__(parent, *rest)

        self.setWindowTitle("Tester")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Stuff"))

        self.seq = HotkeyEdit()
        self.seq.setMaximumSequenceLength(1)
        self.seq.comboChangeSignal.connect(lambda x: print(x, self.seq.getHotkey()))

        self.seq.setClearButtonEnabled(True)
        self.layout().addWidget(self.seq)

        self.line = TestInput()
        self.layout().addWidget(self.line)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.show()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main = Tester()
        sys.exit(app.exec())
    except RuntimeError as e:
        print(e)
