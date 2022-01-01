from typing import List

from PyQt5 import QtCore
from HotkeyManager import HotkeyManager
import os
from ConfigManager import ConfigManager
from os import path, getenv, remove
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
import sys

configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")

from values import defaultVariables, debugConfigPath
from PyQt5.QtCore import QObject, QSize, Qt
from win32com.client import Dispatch
import pythoncom

from snapshot import Snapshot
from rightclickMenu import MenuPage
from paintToolbar import PaintToolbar

from recycler import Recycler



def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


executable = "screenCap.exe"
iconName = "icon.ico"
configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")
singletonFile = path.join(configDir, "singleton.lock")
shortCutDest = path.join(
    getenv("appdata"), "Microsoft\Windows\Start Menu\Programs\Startup"
)
shortCutFile = path.join(shortCutDest, "screenCap.lnk")
shortCutTarget = path.join(
    resource_path(path.dirname(path.abspath(__file__))), executable
)

class ThreadSignal(QObject):
    signal = QtCore.pyqtSignal()
    
class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.initConfig()
        self.initHotkeys()
        self.initGUI()
        self.snapshots = []
        self.currentPainting : Snapshot = None

    def initRecycling(self):
        self.recycling = Recycler(debugConfigPath, self.config)

    def initHotkeys(self):
        self.captureSignal =ThreadSignal()
        self.captureSignal.signal.connect(self.takeSnapshot)
        self.hotkeys = {
            "licapture": (self.captureSignal.signal.emit, "Capture Screen(global)"), #configname : ()
        }
        self.hotkeysManager = HotkeyManager(self.config)
        self.hotkeysManager.start()
        for key, val in self.hotkeys.items():
            keys : List[int] = self.hotkeysManager.getSortedKeys(self.config[key])
            if len(keys) == 0:
                continue
            self.hotkeysManager.setHotkey(key, keys[-1], keys[:-1], val[0] )

    def initConfig(self):
        self.config = ConfigManager(
            "D:\PythonProject\screenCap\QtExperimental\config.ini", defaultVariables
        )
        

    def closeEvent(self, a0) -> None:
        if self.config.iminx:
            print("closing")
            a0.ignore()
            return
        return super().closeEvent(a0)

    def hideEvent(self, a0) -> None:
        if self.config.imintray:
            print("closing")
            a0.ignore()
            return
        return super().hideEvent(a0)

    def initGUI(self):
        self.setWindowTitle("screenCap owo")
        
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.tabs = SizeAdjustingTabs([3],self)
        
        self.generaltab = QWidget()
        
        self.hotkeystab = QWidget()
        
        self.generaltab.layout = QVBoxLayout()

        self.generaltab.setLayout(self.generaltab.layout)
        self.tabs.addTab(self.generaltab, "General")

        # first row
        temphbox = QHBoxLayout()
        # start up options
        startupGroup = QGroupBox("Start up options")
        temphbox.addWidget(startupGroup)

        startupLayout = QVBoxLayout()
        self.startUpCheck = QCheckBox("Run on Start up")
        self.startminCheck = QCheckBox("Start minimalized")
        startupLayout.addWidget(self.startUpCheck)
        startupLayout.addWidget(self.startminCheck)
        startupGroup.setLayout(startupLayout)

        # controls
        miscGroup = QGroupBox("System Tray")
        temphbox.addWidget(miscGroup)
        misclayout = QVBoxLayout()
        miscGroup.setLayout(misclayout)

        self.minTrayCheck = QCheckBox("Minimize to system tray")
        self.xTrayCheck = QCheckBox("Minimize to tray when 'X' is pressed")

        misclayout.addWidget(self.minTrayCheck)
        misclayout.addWidget(self.xTrayCheck)

        # second row (recycler stuff)
        recycleGroup = QGroupBox("Recycle Bin")
        self.showRecycleButton = QPushButton("Show recycle bin")
        self.clearRecycleButton = QPushButton("Clear recycle bin")
        self.recycleCapacityEdit = CustomLineEdit()
        self.recycleCapacityEdit.setValidator(QIntValidator(1, 200))
        self.recycleCheck = QCheckBox("Use recycle bin")

        recycleMainLayout = QHBoxLayout()
        recycleGroup.setLayout(recycleMainLayout)

        recyclelayout1 = QVBoxLayout()
        recyclelayout2 = QVBoxLayout()
        recycleButtonGroup = QHBoxLayout()

        recyclelayout1.addWidget(self.recycleCheck)
        recyclelayout1.addWidget(QLabel("Recycle bin capacity"))

        recycleButtonGroup.addWidget(self.showRecycleButton)
        recycleButtonGroup.addWidget(self.clearRecycleButton)

        recyclelayout2.addLayout(recycleButtonGroup)
        recyclelayout2.addWidget(self.recycleCapacityEdit)

        recycleMainLayout.addLayout(recyclelayout1)
        recycleMainLayout.addLayout(recyclelayout2)

        # third row, saving stuff
        savingGroup = QGroupBox("Save Options")

        mainsavingLayout = QVBoxLayout()
        savingGroup.setLayout(mainsavingLayout)

        self.savingOption = (
            QComboBox()
        )  # scaled image, original, scaled with drawing, original with drawing.
        self.savePromptCheck = QCheckBox("Alwasys show prompt")
        self.defaultSaveLocation = CustomLineEdit()
        self.useLastLocationCheck = QCheckBox("Use last save location")

        savelayoutUp = QHBoxLayout()

        savelayoutLeft = QVBoxLayout()
        savelayoutLeft.addWidget(QLabel("Default save options"))
        savelayoutLeft.addWidget(QLabel("Default save location"))

        saveRight = QVBoxLayout()
        saveUpRight = QHBoxLayout()
        saveUpRight.addWidget(self.savingOption)
        saveUpRight.addWidget(self.savePromptCheck)

        saveRight.addLayout(saveUpRight)
        saveRight.addWidget(self.defaultSaveLocation)

        savelayoutUp.addLayout(savelayoutLeft)
        savelayoutUp.addLayout(saveRight)
        mainsavingLayout.addLayout(savelayoutUp)
        mainsavingLayout.addWidget(self.useLastLocationCheck)

        # bottom
        self.generaltab.layout.addLayout(temphbox)
        self.generaltab.layout.addWidget(recycleGroup)
        self.generaltab.layout.addWidget(savingGroup)
        self.captureButton = QPushButton("Capture")

        self.generaltab.layout.addWidget(self.captureButton)
        self.applyGeneralConfig()
        self.setupGeneralTab()
        self.initHotkeysTab()
        self.setupContextMenuTab()
        self.setupPaintTool()
        self.show()
        self.adjustSize()
        self.tabs.onItemChanged()

    def initHotkeysTab(self):
        def lineeditRecord(item, name, func, islocal):

            self.hotkeysManager.recordNewHotkey(
                name, func, lambda s: item.setText(s), islocal
            )
            item.onkeydown = self.hotkeysManager.keyDown
            item.onkeyup = self.hotkeysManager.keyUp

        def makeFunc(func, params):
            return lambda: func(*params)

        form = QFormLayout()
        form.titles = []
        form.lines = []
        self.hotkeystab.setLayout(form)

        r = iter(range(len(self.hotkeys)))
        for key, val in self.hotkeys.items():
            i = next(r)
            form.titles.append(QLabel(val[1]))
            form.lines.append(CustomLineEdit(self.hotkeysManager.getKeyString(None,set(self.config[key])))) #knee deep in jank

            form.lines[i].onFocus = makeFunc(
                lineeditRecord,
                (form.lines[i], key, val[0], not val[1].endswith("(global)")),
            )
            form.lines[i].lostFocus = self.hotkeysManager.stopRecording

            form.addRow(form.titles[i], form.lines[i])
        
    
        self.hotkeystab.setLayout(form)
        scroll = QScrollArea()
        scroll.setWidget(self.hotkeystab)
        self.tabs.addTab(scroll, "Hotkeys")
        
    def applyGeneralConfig(self):

        self.startUpCheck.setChecked(bool(self.config.istartup))
        self.startminCheck.setChecked(bool(self.config.istartmin))
        self.minTrayCheck.setChecked(bool(self.config.imintray))
        self.xTrayCheck.setChecked(bool(self.config.iminx))
        self.recycleCheck.setChecked(bool(self.config.iuserecycle))
        self.recycleCapacityEdit.setText(str(self.config.irecyclecapacity))
        self.savingOption.addItems(
            ["Scaled", "Scaled w/ sketch", "Original", "Original w/ sketch"]
        )
        self.savingOption.setCurrentIndex(self.config.isaveoption)
        self.savePromptCheck.setChecked(bool(self.config.ishowsaveprompt))
        self.defaultSaveLocation.setText(self.config.ssavelocation)
        self.useLastLocationCheck.setChecked(bool(self.config.iuselastsave))

    def updateDisabled(self):
        self.showRecycleButton.setEnabled(self.recycleCheck.isChecked())
        self.clearRecycleButton.setEnabled(self.recycleCheck.isChecked())
        self.recycleCapacityEdit.setEnabled(self.recycleCheck.isChecked())
       # self.savingOption.setDisabled(self.savePromptCheck.isChecked())
        self.defaultSaveLocation.setDisabled(self.useLastLocationCheck.isChecked())

    def setupGeneralTab(self):
        
        
        def connectck(check, func):
            check.stateChanged.connect(lambda i: func())

        def startUp():
            self.config.istartup = int(self.startUpCheck.isChecked())
            # TODO implement start up behaviour

            if self.startUpCheck.isChecked():
                pythoncom.CoInitialize()
                shell = Dispatch("WScript.Shell")
                st = shell.CreateShortCut(shortCutFile)
                st.Targetpath = shortCutTarget
                st.save()
            else:
                if path.isfile(shortCutFile):
                    remove(shortCutFile)

        self.startUpCheck.stateChanged.connect(lambda i: startUp())

        def startMin():
            self.config.istartmin = int(self.startminCheck.isChecked())
            # TODO implement start up behaviour

        self.startminCheck.stateChanged.connect(lambda i: startMin())

        def minToTray():
            self.config.imintray = int(self.minTrayCheck.isChecked())

        connectck(self.minTrayCheck, minToTray)

        def minX():
            self.config.iminx = int(self.xTrayCheck.isChecked())

        connectck(self.xTrayCheck, minX)

        def useRecycle():
            self.config.iuserecycle = int(self.recycleCheck.isChecked())
            self.updateDisabled()

        connectck(self.recycleCheck, useRecycle)

        def showRecycle():
            print("show recycle clicked")
            # TODO implement recycle menu

        self.showRecycleButton.clicked.connect(lambda: showRecycle())

        def clearRecycle():
            print("clear recycle cliked")
            # TODO implement recycle menu

        self.clearRecycleButton.clicked.connect(lambda: clearRecycle())

        def capacityChange():
            if self.recycleCapacityEdit.text() == "":
                self.recycleCapacityEdit.setText("0")
            print("capacityChange", int(self.recycleCapacityEdit.text()))

        self.recycleCapacityEdit.lostFocus = capacityChange

        def saveOption(val):
            self.config.isaveoption = val

        self.savingOption.currentIndexChanged.connect(lambda i: saveOption(i))

        def alwaysShowPrompt():
            self.config.ishowsaveprompt = int(self.savePromptCheck.isChecked())
            self.updateDisabled()

        connectck(self.savePromptCheck, alwaysShowPrompt)

        def getSaveLocation():
            path = QFileDialog.getExistingDirectory(
                self, "Choose default save location", os.getenv("HOME")
            )
            if path:
                self.config.ssavelocation = path
                self.defaultSaveLocation.setText(path)

        def checkValidPath():
            if not os.path.exists(self.defaultSaveLocation.text()):
                self.defaultSaveLocation.setText(self.config.ssavelocation)

        self.defaultSaveLocation.onclick = getSaveLocation
        self.defaultSaveLocation.lostFocus = checkValidPath

        def useLastLocation():
            self.config.iuselastsave = int(self.useLastLocationCheck.isChecked())
            self.updateDisabled()

        connectck(self.useLastLocationCheck, useLastLocation)

    def setupContextMenuTab(self):
        self.contextMenuTab = MenuPage(self.config)
        self.tabs.addTab(self.contextMenuTab, "Context Menu")

    def setupPaintTool(self):
        self.paintTool = PaintToolbar(self.config, self)
        self.paintToolContainer = QWidget()
        self.paintToolContainer.setLayout(QHBoxLayout())
        self.paintToolContainer.layout().addWidget(self.paintTool)
        self.paintToolContainer.layout().setContentsMargins(0,0,0,0)
        self.tabs.addTab(self.paintToolContainer, "Paint Tools")
    
    def takeSnapshot(self): 
        self.snapshots.append(Snapshot(master= self, image= None, config = self.config, contextMenu=self.contextMenuTab, paintTool= self.paintTool)) #call from full screen

    def snapshotCloseEvent(self, snap: Snapshot):
        try:
            self.snapshots.remove(snap)
        except ValueError as e:
            print(e, "oh no! trying to delete a snap that doesnt exist")
        if not self.snapshots or snap is self.currentPainting:
            #if the last snap is closed, then painttool is no longer needed
            #or if the snap closed is the one currently painting
            self.paintToolJoin()
    
    def snapshotPaintEvent(self, snap : Snapshot):
        if self.currentPainting: # current is not none
            self.currentPainting.stopPaint()
        self.currentPainting = snap
        self.paintToolPop()
        
    def snapshotStopPaintEvent(self, snap : Snapshot):
        if snap is self.currentPainting:
            self.paintToolJoin()
            
    def paintToolPop(self):
        self.paintTool.setParent(None)
        self.paintTool.show()
    
    def paintToolJoin(self):
        self.paintToolContainer.layout().addWidget(self.paintTool)
        
    
class CustomLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onFocus = lambda: ()
        self.lostFocus = lambda: ()
        self.onclick = lambda: ()
        self.onkeydown = lambda a: ()
        self.onkeyup = lambda a: ()

    def focusInEvent(self, a0) -> None:
        self.onFocus()
        return super().focusInEvent(a0)

    def focusOutEvent(self, a0) -> None:
        self.lostFocus()
        return super().focusOutEvent(a0)

    def mousePressEvent(self, a0) -> None:
        self.onclick()
        return super().mousePressEvent(a0)

    def keyPressEvent(self, a0) -> None:

        self.onkeydown(a0)

    def keyReleaseEvent(self, a0) -> None:
        self.onkeyup(a0)


class SizeAdjustingTabs(QTabWidget):
    
    def __init__(self, excluded = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded = excluded if excluded else []
        self.maxSize = None
        self.currentChanged.connect(self.onItemChanged)
    
    def minimumSizeHint(self):
        return self.sizeHint()
    
    def sizeHint(self):
        
        if self.currentIndex() in self.excluded:
            return QSize(self.currentWidget().sizeHint().width(), self.currentWidget().sizeHint().height() + 30 )
        
        try:
            maxWidth = max([self.widget(i).sizeHint().width() for i in range(self.count()) if i not in self.excluded])
            maxHeight = max([self.widget(i).sizeHint().height() for i in range(self.count()) if i not in self.excluded]) + 30
            return  QSize(maxWidth, maxHeight)
        except ValueError as e:
            return super().sizeHint()

    def onItemChanged(self):
        if self.sizeHint().width() < 50 or self.sizeHint().height() < 50:
            return 
        self.setFixedSize(self.sizeHint())
        self.parent().adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
