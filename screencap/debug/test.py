

import sys
from typing import Any, Optional
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsItem


class Tester(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, *rest: Any):
        super().__init__(parent, *rest)

        self.setWindowTitle("Tester")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Stuff"))
        self.show()

        self.testItem = QGraphicsItem(None)
        print(self.testItem)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main = Tester()
        sys.exit(app.exec())
    except RuntimeError as e:
        print(e)
    finally:
        input("press enter to end...")
