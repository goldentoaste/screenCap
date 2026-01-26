

import sys
from typing import Any, Optional
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class Tester(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, *rest: Any):
        super().__init__(parent, *rest)

        self.setWindowTitle("Tester")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Stuff"))
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Tester()
    sys.exit(app.exec())
