

import sys
from typing import Any, Optional
from PySide6.QtCore import QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QKeySequenceEdit, QLabel, QLineEdit, QVBoxLayout, QWidget


class TestInput(QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        print(arg__1.key(), arg__1.modifiers())
        return super().keyPressEvent(arg__1)

class TestKeyEdit(QKeySequenceEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        super().keyPressEvent(arg__1)

        self.setKeySequence(QKeySequence(arg__1.keyCombination()))

class Tester(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, *rest: Any):
        super().__init__(parent, *rest)

        self.setWindowTitle("Tester")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Stuff"))

        self.seq = TestKeyEdit()
        self.seq.setMaximumSequenceLength(1)
        self.seq.keySequenceChanged.connect(lambda x: (print(x[0].key(), x[0].keyboardModifiers()) if x.count() else "pass"))
        self.seq.setClearButtonEnabled(True)
        self.layout().addWidget(self.seq)

        self.line = TestInput()
        self.layout().addWidget(self.line)

        self.show()



if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main = Tester()
        sys.exit(app.exec())
    except RuntimeError as e:
        print(e)
    finally:
        input("press enter to end...")
