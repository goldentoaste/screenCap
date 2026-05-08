import sys
import time
from PySide6.QtCore import QKeyCombination, QPoint, QRect, QSize, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

from screencap.src.hotkeys.GlobalKeyManager import WinGlobalHotkey
from screencap.src.hotkeys.Common import HotkeyEdit


class HotkeyTimer(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Hotkey Timer")
        self.hotkeyManager = WinGlobalHotkey.getManager()

        self.setLayout(QVBoxLayout())

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.comboEdit = HotkeyEdit()
        self.label = QLabel("Timer: 00:00")
        self.layout().addWidget(self.comboEdit)
        self.layout().addWidget(self.label)

        self.startBtn = QPushButton("Start")
        self.stopBtn = QPushButton("Stop")
        self.layout().addWidget(self.startBtn)
        self.layout().addWidget(self.stopBtn)

        self.t0 = 0
        self.t = 0
        self.timer: QTimer | None = None

        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)

        self.comboEdit.comboChangeSignal.connect(self.regKey)

        self.sizeGrip = QSizeGrip(self)
        self.sizeGrip.resize(16, 16)
        self.sizeGrip.setGeometry(
            QRect(self.rect().bottomRight() - QPoint(16, 16), QSize(16, 16))
        )
        self.sizeGrip.setVisible(True)
        self.show()

    def regKey(self, key: QKeyCombination):
        if self.comboEdit.id:
            UnRegRes = self.hotkeyManager.unregisterHotkey(self.comboEdit.id)

        res = self.hotkeyManager.registerHotKey("Test", key, lambda: self.toggleTimer())
        self.comboEdit.clearFocus()
        if res[0]:
            self.comboEdit.id = res[1]  # pyright: ignore[reportAttributeAccessIssue]

    def toggleTimer(self):
        print("Toggling timer")
        if self.timer and self.timer.isActive():
            self.stop()
        else:
            self.start()

    def stop(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

    def start(self):
        self.t = 0
        self.t0 = time.time()
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start()

    def updateTimer(self):
        self.t = time.time() - self.t0
        minutes = int(self.t // 60)
        seconds = int(self.t % 60)
        miliSeconds = int((self.t - int(self.t)) * 1000)
        self.label.setText(f"Timer: {minutes:02d}:{seconds:02d}.{miliSeconds:03d}")


if __name__ == "__main__":

    a = QApplication()
    w = HotkeyTimer()

    sys.exit(a.exec())
