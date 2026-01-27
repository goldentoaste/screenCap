import sys
from PySide6 import QtGui, QtWidgets

from PySide6.QtCore import QRectF, QSize, Qt

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ConfigManager import ConfigManager
import values

divider = "——————————"
shortDivider = "div"


class MenuPage(QtWidgets.QWidget):
    """a gui to customize right click context menu for snapshots"""

    def __init__(self, config: ConfigManager, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.config = config

        self.menu = None
        self.needUpdate = False
        self.lastTarget = None
        self.initGui()
        self.initValues()
        self.show()

    def sizeHint(self):
        return QSize(300, 300)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:

        self.menu = self.buildMenu()
        self.menu.popup(self.mapToGlobal(a0.pos()))
        return super().contextMenuEvent(a0)

    def initGui(self):
        layout = QHBoxLayout()
        self.currentList = CurrentListView(self.config, self)
        self.availableList = AvailableListView()
        self.currentList.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.availableList.setDefaultDropAction(Qt.DropAction.MoveAction)

        left = QVBoxLayout()
        left.addWidget(QLabel("Currently using:"))
        left.addWidget(self.currentList)

        self.addDividerButton = QPushButton("Add Divider")
        left.addWidget(self.addDividerButton)
        layout.addLayout(left)

        right = QVBoxLayout()
        right.addWidget(QLabel("Available options:"))
        right.addWidget(self.availableList)
        layout.addLayout(right)

        self.setLayout(layout)

    def initValues(self):

        current = self.config.lscurrentcommands
        available = self.config.lsavailablecommands
        for command in current:
            if command not in values.rightclickOptions and command != shortDivider:
                current = (
                    []
                )  # if any of the items in the ini is not compatible, just reset it.
                break
        available = [
            item for item in values.rightclickOptions.keys() if item not in current
        ]  # available is the commands not yet used

        if available:
            self.availableList.addItems(available)

        if current:
            self.currentList.addItems(
                [item if item != shortDivider else divider for item in current]
            )

        self.availableList.setMovement(QListView.Movement.Free)
        self.currentList.setMovement(QListView.Movement.Free)

        def onDividerClick():
            self.currentList.addItem(divider)
            self.config.lscurrentcommands = self.config.lscurrentcommands + [
                shortDivider
            ]

        self.addDividerButton.clicked.connect(onDividerClick)

    def buildMenu(self, target=None) -> QMenu:
        # .TODO maybe cache the menu generated
        if self.menu is not None and not self.needUpdate and target == self.lastTarget:
            return self.menu

        def callFunc(key):
            values.rightclickOptions[key](target)

        self.menu = QMenu(target)
        for i in range(self.currentList.count()):
            text = self.currentList.item(i).text()

            if text == divider:
                self.menu.addSeparator()
            else:
                # . TODO quick recycling view
                action = self.menu.addAction(text)
                action.triggered.connect(
                    (lambda t: (lambda: callFunc(key=t)))(text)
                    if target is not None
                    else (lambda text=text: print(text, type(text), "hi"))
                )
        self.lastTarget = target
        return self.menu


class CurrentListView(QListWidget):
    def __init__(self, config: ConfigManager, master, *args, **kwargs):

        self.config = config
        self.master = master
        super().__init__(*args, **kwargs)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        super().dropEvent(event)
        self.master.needUpate = True
        self.parent().needUpdate = True  # breaking oop in python :v
        commands = [
            self.item(i).text() if self.item(i).text() != divider else shortDivider
            for i in range(self.count())
        ]  # all strings in current list, but replace long div with short div
        self.config.lscurrentcommands = commands

        commands = set(commands)
        self.config.lsavailablecommands = [
            val for val in values.rightclickOptions.keys() if val not in commands
        ]  # puts available options thats not used yet in config. order preservd.


class AvailableListView(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        super().dropEvent(event)
        for i in range(self.count()):

            if self.item(i).text() == divider:
                self.takeItem(i)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = QWidget()
    ex.resize(400, 300)
    ex.move(200, 200)
    ex.setLayout(QHBoxLayout())

    s = MenuPage(ConfigManager(values.debugConfigPath, values.defaultVariables))
    ex.layout().addWidget(s)
    ex.show()
    sys.exit(app.exec_())
