import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget

from PyQt5.QtCore import QSize, Qt


from values import resource_path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from snapshot import Snapshot

class SnapshotMenu(QWidget):

  
    def __init__(self, parent : 'Snapshot') -> None:
        super().__init__(parent)
        self.master = parent
        self.initGui()

    def initGui(self):

        self.setLayout(QHBoxLayout())

        self.saveButton = QPushButton(QIcon(resource_path("icons/save.svg")), "")
        self.saveButton.setWhatsThis("Save button")
        self.saveButton.setIconSize(QSize(24, 24))
        self.saveButton.clicked.connect(lambda: (self.master.stopCrop(), self.master.saveImage()))

        self.copyButton = QPushButton(QIcon(resource_path("icons/copy.svg")), "")
        self.copyButton.setWhatsThis("Copy image into clipboard")
        self.copyButton.setIconSize(QSize(24, 24))
        self.copyButton.clicked.connect(lambda: (self.master.stopCrop(), self.master.copy()))

        self.cutButton = QPushButton(QIcon(resource_path("icons/cut.svg")), "")
        self.cutButton.setWhatsThis("Cut: copy and close")
        self.cutButton.setIconSize(QSize(24, 24))
        self.cutButton.clicked.connect(lambda: (self.master.stopCrop(), self.master.cut()))

        self.closeButton = QPushButton(QIcon(resource_path("icons/cross.svg")), "")
        self.closeButton.setWhatsThis("Cancel and close")
        self.closeButton.setIconSize(QSize(24, 24))
        self.closeButton.clicked.connect(lambda: (self.master.close()))

        self.doneButton = QPushButton(QIcon(resource_path("icons/check.svg")), "")
        self.doneButton.setWhatsThis("Finish cropping")
        self.doneButton.setIconSize(QSize(24, 24))
        self.doneButton.clicked.connect(lambda: self.master.stopCrop())

        self.layout().addWidget(self.saveButton)
        self.layout().addWidget(self.copyButton)
        self.layout().addWidget(self.cutButton)
        self.layout().addWidget(self.closeButton)
        self.layout().addWidget(self.doneButton)

        self.setStyleSheet(
            """
            QPushButton:hover:!pressed{
                border-radius: 6px;
                border : none;
                background: #9191b6;
            }
            QPushButton{
                border : none;
                padding: 5px;
            }
            QWidget{
                background: #646496
            }
            
            """
        )
        self.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = SnapshotMenu(None)
    # ex = PaintToolbar(ConfigManager("D:\PythonProject\screenCap\QtExperimental\config.ini", values.defaultVariables), None)
    sys.exit(app.exec_())
