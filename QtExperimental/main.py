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
        startUpCheck = QCheckBox('Run on Start up')
        startminCheck = QCheckBox('Start minimalized')
        startupLayout.addWidget(startUpCheck)
        startupLayout.addWidget(startminCheck)
        startupGroup.setLayout(startupLayout)
        
        #controls
        miscGroup = QGroupBox('System Tray')
        temphbox.addWidget(miscGroup)
        misclayout = QVBoxLayout()
        miscGroup.setLayout(misclayout)

        minTrayCheck = QCheckBox('Minimize to system tray')
        xTrayCheck = QCheckBox('Minimize to tray when \'X\' is pressed')
        
        misclayout.addWidget(minTrayCheck)
        misclayout.addWidget(xTrayCheck)
        
        #second row (recycler stuff)
        recycleGroup = QGroupBox('Recycle Bin')
        recycleMainLayout = QVBoxLayout()
        recycleGroup.setLayout(recycleMainLayout)
        
        recyclelayout1 = QHBoxLayout()
        recycleCheck = QCheckBox('Use recycle bin')
        showRecycleButton = QPushButton('Show recycle bin')
        clearRecycleButton = QPushButton('Clear recycle bin')
        recyclelayout1.addWidget(recycleCheck)
        recyclelayout1.addWidget(showRecycleButton)
        recyclelayout1.addWidget(clearRecycleButton)
        recycleMainLayout.addLayout(recyclelayout1)
        
        reyclelayout2 = QHBoxLayout()
        reyclelayout2.addWidget(QLabel('Recycle bin capacity'))
        recycleCapacity = QLineEdit()
        recycleCapacity.setValidator(QIntValidator(1, 200))
        reyclelayout2.addWidget(recycleCapacity)
        recycleMainLayout.addLayout(reyclelayout2)
        
        self.generaltab.layout.addLayout(temphbox)
        self.generaltab.layout.addWidget(recycleGroup)
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