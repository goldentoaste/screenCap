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
        recycleMainLayout = QVBoxLayout()
        recycleGroup.setLayout(recycleMainLayout)
        
        recyclelayout1 = QHBoxLayout()
        self.recycleCheck = QCheckBox('Use recycle bin')
        self.showRecycleButton = QPushButton('Show recycle bin')
        self.clearRecycleButton = QPushButton('Clear recycle bin')
        recyclelayout1.addWidget(self.recycleCheck)
        recyclelayout1.addWidget(self.showRecycleButton)
        recyclelayout1.addWidget(self.clearRecycleButton)
        recycleMainLayout.addLayout(recyclelayout1)
        
        reyclelayout2 = QHBoxLayout()
        reyclelayout2.addWidget(QLabel('Recycle bin capacity'))
        self.recycleCapacityEdit = QLineEdit()
        self.recycleCapacityEdit.setValidator(QIntValidator(1, 200))
        reyclelayout2.addWidget(self.recycleCapacityEdit)
        recycleMainLayout.addLayout(reyclelayout2)
        
        #third row, saving stuff
        savingGroup = QGroupBox('Save Options')
        mainsavingLayout = QVBoxLayout()
        savingGroup.setLayout(mainsavingLayout)
        
        savelayout1 = QHBoxLayout()
        savelayout1.addWidget(QLabel('Default save options'))
        self.savingOption = QComboBox() #scaled image, original, scaled with drawing, original with drawing.
        self.savePromptCheck = QCheckBox('Alwasys show prompt')
        savelayout1.addWidget(self.savingOption)
        savelayout1.addWidget(self.savePromptCheck)
        mainsavingLayout.addLayout(savelayout1)
        
        savelayout2 = QHBoxLayout()
        savelayout2.addWidget(QLabel('Default save location'))
        self.defaultSaveLocation = QLineEdit()
        self.useLastLocationCheck = QCheckBox('Use last save location')
        savelayout2.addWidget(self.defaultSaveLocation)
        mainsavingLayout.addLayout(savelayout2)
        mainsavingLayout.addWidget(self.useLastLocationCheck )
        
        
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