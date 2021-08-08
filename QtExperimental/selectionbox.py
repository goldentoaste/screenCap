import sys
from typing import List
import typing
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QMargins, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, Qt


class SelectionBox(QtWidgets.QRubberBand):
    def __init__(self, a0, parent) -> None:
        super().__init__(a0, parent=parent)

        self.grips: List[SizeGrip] = []
        for i in range(8):
            self.grips.append(SizeGrip(self, i))

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.resize(100, 100)
        self.move(10, 10)
        self.show()

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        print(self.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        for grip in self.grips:
            grip.updatePos()
            

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:

        for grip in self.grips:
            grip.updatePos()
            

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        print(a0.pos())
        a0.ignore()


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
        """
        meant to be used with SelectionBox
        """
        super().__init__(parent)
        self.loc = loc
        self.setFixedSize(10, 10)
        self.master: QtWidgets.QRubberBand = parent
        self.side = 10
        self.mousepos = None
        self.master.setMinimumSize(
            max(self.side * 3, self.master.minimumWidth()),
            max(self.side * 3, self.master.minimumHeight()),
        )
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.show()
        
       

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QtGui.QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)

        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 150), 1.35))
        painter.setBrush(QtGui.QColor(100, 100, 200))

        painter.drawRect(self.rect())

    def updatePos(self):
        m = self.master

        funcs = {
            topleft: lambda: (),
            top: lambda: self.move(m.width() // 2 - self.side // 2, 0),
            topright: lambda: self.move(m.width() - self.side, 0),
            left: lambda: self.move(0, m.height() // 2 - self.side // 2),
            right: lambda: self.move(
                m.width() - self.side, m.height() // 2 - self.side // 2
            ),
            botleft: lambda: self.move(0, m.height() - self.side),
            bot: lambda: self.move(
                m.width() // 2 - self.side // 2, m.height() - self.side
            ),
            botright: lambda: self.move(m.width() - self.side, m.height() - self.side),
        }

        funcs[self.loc]()

        

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        self.mousepos = a0.globalPos()

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        dx = a0.globalX() - self.mousepos.x()
        dy = a0.globalY() - self.mousepos.y()

        m = self.master
        funcs = {
            topleft: lambda: (
                m.move(m.x() + dx, m.y() + dy),
                m.resize(m.width() - dx, m.height() - dy),
            ),
            top: lambda: (
                m.move(m.x(), m.y() + dy),
                m.resize(m.width(), m.height() - dy),
            ),
            topright: lambda: (
                (m.move(m.x(),  m.y() + dy), m.resize(m.width() + dx, m.height() + dy))
            ),
            left: lambda: (
                m.move(m.x() + dx, m.y()),
                m.resize(m.width() - dx, m.height()),
            ),
            right: lambda: m.resize(m.width() + dx, m.height()),
            botleft: lambda: (
                m.move(m.x() + dx, m.y()),
                m.resize(m.width() - dx, m.height() + dy),
            ),
            bot: lambda: m.resize(m.width(), m.height() + dy),
            botright: lambda: m.resize(m.width() + dx, m.height() + dy),
        }
        funcs[self.loc]()

        self.mousepos = a0.globalPos()

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.cursor().setShape(Qt.ArrowType.up)

class test(QtWidgets.QWidget):
    
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.resize(100, 100)
        
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)

        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 150), 1.35))
        painter.setBrush(QtGui.QColor(100, 100, 200))

        painter.drawRect(self.rect())
        
        
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        print(a0.pos())
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    ex = QtWidgets.QWidget()
    ex.resize(500, 500)
    ex.move(200, 100)
    s = SelectionBox(1, ex)
    # t = test(ex)
    ex.show()
    sys.exit(app.exec_())
