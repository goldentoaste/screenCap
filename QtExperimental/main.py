import os
from ConfigManager import ConfigManager
from os import path, getenv
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
import sys
configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")

from values import defaultVariables
from PyQt5.QtCore import QFile, Qt
class Main(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initConfig()
        self.initGUI()
        
    
    def initConfig(self):
        self.config = ConfigManager('D:\Python Project\screenCap\QtExperimental\config.ini', defaultVariables)
    
    def initGUI(self):
        self.setWindowTitle("screenCap owo")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        self.tabs = QTabWidget(self)
        self.generaltab = QWidget()
        self.hotkeystab = QWidget()
        self.generaltab.layout = QVBoxLayout()
        
        self.generaltab.setLayout(self.generaltab.layout)
        self.tabs.addTab(self.generaltab, "General")
        self.tabs.addTab(self.hotkeystab, "Hotkeys")
        
        
        #first row
        temphbox = QHBoxLayout()
        #start up options
        startupGroup = QGroupBox('Start up options')
        temphbox.addWidget(startupGroup)
        
        startupLayout = QVBoxLayout()
        self.startUpCheck = QCheckBox('Run on Start up')
        self.startminCheck = QCheckBox('Start minimalized')
        startupLayout.addWidget(self.startUpCheck)
        startupLayout.addWidget(self.startminCheck)
        startupGroup.setLayout(startupLayout)
        
        #controls
        miscGroup = QGroupBox('System Tray')
        temphbox.addWidget(miscGroup)
        misclayout = QVBoxLayout()
        miscGroup.setLayout(misclayout)

        self.minTrayCheck = QCheckBox('Minimize to system tray')
        self.xTrayCheck = QCheckBox('Minimize to tray when \'X\' is pressed')
        
        misclayout.addWidget(self.minTrayCheck)
        misclayout.addWidget(self.xTrayCheck)
        
        #second row (recycler stuff)
        recycleGroup = QGroupBox('Recycle Bin')
        self.showRecycleButton = QPushButton('Show recycle bin')
        self.clearRecycleButton = QPushButton('Clear recycle bin')
        self.recycleCapacityEdit = CustomLineEdit()
        self.recycleCapacityEdit.setValidator(QIntValidator(1, 200))
        self.recycleCheck = QCheckBox('Use recycle bin')
        
        recycleMainLayout = QHBoxLayout()
        recycleGroup.setLayout(recycleMainLayout)
        
        recyclelayout1 = QVBoxLayout()
        recyclelayout2 = QVBoxLayout()
        recycleButtonGroup = QHBoxLayout()
        
        recyclelayout1.addWidget(self.recycleCheck)
        recyclelayout1.addWidget(QLabel('Recycle bin capacity'))
        
        recycleButtonGroup.addWidget(self.showRecycleButton)
        recycleButtonGroup.addWidget(self.clearRecycleButton)
        
        recyclelayout2.addLayout(recycleButtonGroup)
        recyclelayout2.addWidget(self.recycleCapacityEdit)
        
        
        recycleMainLayout.addLayout(recyclelayout1)
        recycleMainLayout.addLayout(recyclelayout2)
        
        
    
        #third row, saving stuff
        savingGroup = QGroupBox('Save Options')
        mainsavingLayout = QVBoxLayout()
        savingGroup.setLayout(mainsavingLayout)
        
        self.savingOption = QComboBox() #scaled image, original, scaled with drawing, original with drawing.
        self.savePromptCheck = QCheckBox('Alwasys show prompt')
        self.defaultSaveLocation = CustomLineEdit()
        self.useLastLocationCheck = QCheckBox('Use last save location')
            
        savelayoutUp = QHBoxLayout()
        
        
        savelayoutLeft = QVBoxLayout()
        savelayoutLeft.addWidget(QLabel('Default save options'))
        savelayoutLeft.addWidget(QLabel('Default save location'))
        
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

        
        
        #bottom
        self.generaltab.layout.addLayout(temphbox)
        self.generaltab.layout.addWidget(recycleGroup)
        self.generaltab.layout.addWidget(savingGroup)
        self.captureButton = QPushButton('Capture')
    
        self.generaltab.layout.addWidget(self.captureButton)
        self.setupGeneralTab()
        
        self.resize(self.tabs.sizeHint())
    
        
        self.show()
    
    
    def setupGeneralTab(self):
        
        def connectck(check, func):
            check.stateChanged.connect(lambda i: func())
        
        def startUp():
            
            self.config.istartup = int(self.startUpCheck.isChecked())
            #TODO implement start up behaviour
            
        self.startUpCheck.stateChanged.connect(lambda i: startUp())
        
        def startMin():
            
            self.config.istartup = int(self.startminCheck.isChecked())
            #TODO implement start up behaviour
            
        self.startminCheck.stateChanged.connect(lambda i: startMin())
        
        def minToTray():
            self.config.imintray = int(self.minTrayCheck.isChecked())
        connectck(self.minTrayCheck, minToTray)
        
        def minX():
            self.config.iminx = int(self.xTrayCheck.isChecked())
        connectck(self.xTrayCheck, minX)

        def useRecycle():
            self.config.iuserecycle =  int(self.recycleCheck.isChecked())
        connectck(self.recycleCheck, useRecycle)
        
        def showRecycle():
            print('show recycle clicked')
            #TODO implement recycle menu
        
        self.showRecycleButton.clicked.connect(lambda: showRecycle())
        
        def clearRecycle():
            print('clear recycle cliked')
            #TODO implement recycle menu
        self.clearRecycleButton.clicked.connect(lambda: clearRecycle())
        
        
        def capacityChange():
            if self.recycleCapacityEdit.text() == '':
                self.recycleCapacityEdit.setText('0')
            print('capacityChange',int(self.recycleCapacityEdit.text()))
            
        self.recycleCapacityEdit.lostFocus = capacityChange

        def saveOption(val):
            self.config.isaveoption = val
        
        self.savingOption.currentIndexChanged.connect(lambda i: saveOption(i))
        
        def alwaysShowPrompt():
            self.config.ishowsaveprompt = int(self.savePromptCheck.isChecked())
            self.savingOption.setDisabled(self.savePromptCheck.isChecked())
            
        connectck(self.savePromptCheck, alwaysShowPrompt)
        
        def getSaveLocation():
            path, _ = QFileDialog.getExistingDirectory(self, 'Choose default save location', os.getenv('HOME'))
            if path:
                self.config.ssavelocation = path
                print(path)

        def checkValidPath():
            if not os.path.exists(self.defaultSaveLocation.text()):
                self.defaultSaveLocation.setText(self.config.ssavelocation)
                
        self.defaultSaveLocation.onFocus = getSaveLocation
        self.defaultSaveLocation.lostFocus = checkValidPath
        
        def useLastLocation():
            self.config.iuselastsave = int(self.useLastLocationCheck.isChecked())
            self.defaultSaveLocation.setDisabled(self.useLastLocationCheck.isChecked())
        
        connectck(self.useLastLocationCheck, useLastLocation)
        
        
        

class CustomLineEdit(QLineEdit):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onFocus = lambda: ()
        self.lostFocus = lambda: ()

    def focusInEvent(self, a0) -> None:
        self.onFocus()
        return super().focusInEvent(a0)
    
    def focusOutEvent(self, a0) -> None:
        self.lostFocus()
        return super().focusOutEvent(a0)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())