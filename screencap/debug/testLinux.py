

import os
import sys

from PySide6.QtWidgets import QApplication, QWidget

class Tester(QWidget):

    def __init__(self) -> None:
        super().__init__(None)

        self.setGeometry(200, 200, 400, 400)
        self.show()

        # createPolicy("./helper")

        # subprocess.run([
        #     "pkexec",
        #     "./helper",
        # ], check=True) # start socket




if __name__  == '__main__':
    a = QApplication()
    t = Tester()
    sys.exit(a.exec())