from configparser import ConfigParser
from os import path, getenv
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
        
        startUpCheck = QCheckBox('Run on Start up')
        startminCheck = QCheckBox('Start minimalized')
        
        
        
        
        self.generaltab.layout.addLayout()
        
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