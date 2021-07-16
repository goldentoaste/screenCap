from configparser import ConfigParser
from os import path, getenv
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
import sys
configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")


class Main(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initGUI()
        
    def initGUI(self):
        self.setWindowTitle("screenCap owo")
        
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
        self.recycleCapacityEdit = QLineEdit()
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
        self.defaultSaveLocation = QLineEdit()
        self.useLastLocationCheck = QCheckBox('Use last save location')
            
        savelayoutUp = QHBoxLayout()
        
        
        savelayoutLeft = QVBoxLayout()
        savelayoutLeft.addWidget(QLabel('Default save options'))
        savelayoutLeft.addWidget(QLabel('Default save location'))
        
        saveUpRight = QHBoxLayout()
        saveUpRight.addWidget()

        
        
        #bottom
        self.generaltab.layout.addLayout(temphbox)
        self.generaltab.layout.addWidget(recycleGroup)
        self.generaltab.layout.addWidget(savingGroup)
        self.captureButton = QPushButton('Capture')
    
        self.generaltab.layout.addWidget(self.captureButton)
        
        self.resize(self.tabs.sizeHint())
    
        
        self.show()
    
    def loadConfig(self):
        self.config = ConfigParser()
        self.config.read(configFile)
        
        if not self.config.has_section("General"):
            self.config.add_section("General")
        
        if not self.config.has_section("Painter"):
            self.config.add_section("Painter")
        
        if not self.config.has_section("KeyBinds"):
            self.config.add_section("KeyBinds")
                
        def getIntConfig(section, varName, default=0):
            try:
                return self.config.getint(section, varName)
            except Exception:
                return default

        def getStrConfig(section,varName, default=""):
            try:
                return self.config.get(section, varName)
            except Exception:
                return default
        
        self.startUp = getIntConfig("General", "startUp")
        self.startMin = getIntConfig("General", "startMin")
        self.minimize = getIntConfig("General", "minimize")
        self.admin = getIntConfig("General", "admin")
        self.recycleSize = getIntConfig("General", "recycleSize")




if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    print(sys.argv)
    ex = Main()
    
    sys.exit(app.exec_())