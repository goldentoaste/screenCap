

import sys
from typing import List
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QMargins, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, Qt

class SelectionBox(QtWidgets.QRubberBand):
    
    def __init__(self, a0, parent) -> None:
        super().__init__(a0, parent=parent)
        
        self.grips: List[SizeGrip] = []
        for i in range(8):
            self.grips.append(SizeGrip(self, i))
        
        self.resize(100, 100)
        self.show()

    
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        for grip in self.grips:
            grip.updatePos()


topleft = 0
top = 1
topright = 2
left = 3
right = 4
botleft = 5
bot = 6
botright = 7

class SizeGrip(QtWidgets.QWidget):

    
    
    def __init__(self, parent, loc):
        '''
        meant to be used with SelectionBox
        '''
        super().__init__(parent)
        self.loc = loc
        self.setFixedSize(16, 16)
        self.master : QtWidgets.QRubberBand = parent
        self.side = 16
        self.mousepos = None
        self.master.setMinimumSize(max(self.side * 3, self.master.minimumWidth()),max(self.side * 3, self.master.minimumHeight()) )
        
    
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        return super().paintEvent(a0)
    

    
    def updatePos(self):
        m = self.master
        
        funcs = {
            
            topleft: lambda: self.move(m.pos()),
            top: lambda: self.move(m.width() - self.side//2 + m.x(), m.y()),
            topright: lambda: self.move(m.x() + m.width() - self.side, m.y()),
            left: lambda: self.move(m.x(), m.y() + m.height()// 2),
            right: lambda: self.move(m.x() + m.width() - self.side, m.y() + m.height() // 2),
            botleft: lambda: self.move(m.x(), m.height() + m.y() - self.side),
            bot: lambda: self.move(m.width() - self.side//2 + m.x(), m.y() + m.height() - self.side),
            botright: lambda: self.move(m.x() + m.width() - self.side, m.y() + m.height() - self.side)
        }
        
        funcs[self.loc]()
        
    
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mousepos = a0.globalPos()
        
    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        dx = a0.globalX() - self.mousepos.x()
        dy = a0.globalY() - self.mousepos.y()
        
        m = self.master
        funcs = {
            
            topleft: lambda: (m.move(m.x() + dx, m.y() + dy), m.resize(m.width() + dx, m.height() + dy)),
            top: lambda: (m.move(m.x() , m.y() + dy), m.resize(m.width(), m.height() + dy)),
            topright: lambda: ((m.move(m.x() + m.y() + dy),  m.resize(m.width()+ dx, m.height() + dy))),
            left: lambda: (m.move(m.x() + dx , m.y()), m.resize(m.width() + dx, m.height() )),
            right: lambda: m.resize(m.width() + dx, m.height() ),
            botleft: lambda: (m.move(m.x() + dx, m.y()), m.resize(m.width() + dx, m.height() + dy)),
            bot: lambda:  m.resize(m.width(), m.height() + dy),
            botright: lambda: m.resize(m.width() + dx, m.height() + dy)
        }
        funcs[self.loc]()
        
        self.mousepos = a0.globalPos()
        


if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    ex = QtWidgets.QWidget()
    ex.resize(500, 500)
    
    s = SelectionBox(1, ex)
    ex.show()
    sys.exit(app.exec_())