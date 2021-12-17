
import sys
from PyQt5 import QtGui, QtWidgets

from PyQt5.QtCore import QRectF, Qt

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QListWidget, QPushButton, QVBoxLayout, QWidget

from ConfigManager import ConfigManager
import values

divider = "————————————"

class MenuPage(QtWidgets.QWidget):
    
    '''a gui to customize right click context menu for snapshots'''
    def __init__(self, config: ConfigManager, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.config = config
        self.initGui()
        self.show()
    
    
    def initGui(self):
        
        layout = QHBoxLayout()
        
        
        self.currentList = QListWidget()
        self.availableList = QListWidget()
        
        layout.addWidget(self.currentList)
        
        middleLayout = QVBoxLayout()
        self.leftButton = QPushButton("<")
        self.rightButton = QPushButton(">")
        self.dividerButton = QPushButton("—")
        
        middleLayout.addWidget(self.leftButton)
        middleLayout.addWidget(self.rightButton)
        middleLayout.addWidget(self.dividerButton)
        
        layout.addWidget(middleLayout)
        layout.addWidget(self.availableList)
        
        

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    ex = QWidget()
    ex.resize(500, 500)
    ex.move(200, 200)
    # s = MenuPage(ConfigManager(values.))