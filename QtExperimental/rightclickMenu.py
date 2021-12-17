
import sys
from PyQt5 import QtGui, QtWidgets

from PyQt5.QtCore import QRectF, QSize, Qt

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QListView, QListWidget, QPushButton, QVBoxLayout, QWidget

from ConfigManager import ConfigManager
import values

divider = "————————————"

class MenuPage(QtWidgets.QWidget):
    
    '''a gui to customize right click context menu for snapshots'''
    def __init__(self, config: ConfigManager, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.config = config
        self.initGui()
        self.initValues()
        self.show()
        
    
    
    def initGui(self):
        layout = QHBoxLayout()
        self.currentList = QListWidget()
        self.availableList = ListView()
        self.currentList.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.availableList.setDefaultDropAction(Qt.DropAction.MoveAction)

        
        left = QVBoxLayout()
        left.addWidget(QLabel("Currently using:"))
        left.addWidget(self.currentList)
        
        self.addDividerButton = QPushButton("Add Divider")
        left.addWidget(self.addDividerButton)
        layout.addLayout(left)
        
        middleLayout = QVBoxLayout()
        self.leftButton = QPushButton("<")
        self.rightButton = QPushButton(">")
        

        
        middleLayout.addWidget(self.leftButton)
        middleLayout.addWidget(self.rightButton)

        layout.addLayout(middleLayout)
        
        right = QVBoxLayout()
        right.addWidget(QLabel("Available options:"))
        right.addWidget(self.availableList)
        layout.addLayout(right)
        
        self.setLayout(layout)
        self.leftButton.setMaximumWidth(50)
        self.rightButton.setMaximumWidth(50)
        # self.leftButton.setStyleSheet(f'''QPushButton{{
        #     margin: 1px;
        #     }}''')
    
    
    def initValues(self):

        
        available = self.config.lsavailablecommands
        current = self.config.lscurrentcommands
        
        if available:
            
            self.availableList.addItems(available)
            
        if current:
            self.currentList.addItems(current)
        
        self.availableList.setMovement(QListView.Movement.Free)
        self.currentList.setMovement(QListView.Movement.Free)

        
        self.addDividerButton.clicked.connect(lambda: self.currentList.addItem(divider))

class ListView(QListWidget):
    
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