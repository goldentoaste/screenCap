


class x:
    
    def __int__(self):
        print('init obj')
        self.func = lambda: print('1')
        
    def stuff(self, s):
        print('obj', s)
        

o = x()

def mod(item):
    item.func = lambda: print('2')

o.func = lambda: print('3')
o.func()

mod(o)

o.func()
    

from PIL import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtWidgets import QApplication, QSizeGrip, QWidget

def f1(a : int):
    print(a)
    
def f2(b:float):
    print(b, type(b))
    
f1(2); f2(2)


import sys


class stuff(QWidget):
    
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.resize(400, 400
                    )
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint 
        )
        
        
        self.grip = QSizeGrip(self)
        self.grip.resize(16, 16)
        self.show()
        
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.grip.move(a0.size().width() - 16, a0.size().height() - 16)
        return super().resizeEvent(a0)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = stuff()
    sys.exit(app.exec_())
