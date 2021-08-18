import sys
from typing import List

from PyQt5 import QtGui, QtWidgets

from PyQt5.QtCore import QRectF, Qt

topleft = 0
top = 1
topright = 2
left = 3
right = 4
botleft = 5
bot = 6
botright = 7

c = Qt.CursorShape
cursors = {
    topleft: c.SizeFDiagCursor,
    top: c.SizeVerCursor,
    topright: c.SizeBDiagCursor,
    left: c.SizeHorCursor,
    right: c.SizeHorCursor,
    botleft: c.SizeBDiagCursor,
    bot: c.SizeVerCursor,
    botright: c.SizeFDiagCursor,
}


class SelectionBox(QtWidgets.QRubberBand):
    def __init__(self, a0, parent) -> None:
        super().__init__(a0, parent=parent)

        self.grips: List[SizeGrip] = []
        for i in range(8):
            self.grips.append(SizeGrip(self, i))

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        self.show()

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)


    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        for grip in self.grips:
            grip.updatePos()

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:

        for grip in self.grips:
            grip.updatePos()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.lastpos = a0.globalPos()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.move(self.x() + a0.globalX() - self.lastpos.x(), self.y() + a0.globalY() - self.lastpos.y())
        self.lastpos = a0.globalPos()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QtGui.QPainter(self)

        painter.setRenderHints(painter.Antialiasing)

        painter.setPen(
            QtGui.QPen(QtGui.QColor(100, 100, 150), 5.5, Qt.PenStyle.DotLine)
        )
        painter.setBrush(QtGui.QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.rect())


class SizeGrip(QtWidgets.QWidget):
    def __init__(self, parent, loc):
        """
        meant to be used with SelectionBox
        """
        super().__init__(parent)
        self.loc = loc

        self.master: QtWidgets.QRubberBand = parent
        self.side = 10
        self.mousepos = None
        self.master.setMinimumSize(
            max(self.side * 3, self.master.minimumWidth()),
            max(self.side * 3, self.master.minimumHeight()),
        )
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.raise_()
        self.show()

        self.setCursor(cursors[self.loc])
        self.resize(10, 10)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        painter = QtGui.QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)

        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 150), 1.35))
        painter.setBrush(QtGui.QColor(100, 100, 200))

        if self.loc == top:
            painter.drawRect(
                QRectF(self.width() // 2 - self.side // 2, 0, self.side, self.side)
            )

        elif self.loc == left:
            painter.drawRect(
                QRectF(0, self.height() // 2 - self.side // 2, self.side, self.side)
            )
        elif self.loc == right:
            painter.drawRect(
                QRectF(
                    self.width() - self.side,
                    self.height() // 2 - self.side // 2,
                    self.side,
                    self.side,
                )
            )
        elif self.loc == bot:
            painter.drawRect(
                QRectF(
                    self.width() // 2 - self.side // 2,
                    self.height() - self.side,
                    self.side,
                    self.side,
                )
            )
        else:
            painter.drawRect(self.rect())

    def updatePos(self):
        m = self.master

        # owo!
        funcs = {
            topleft: lambda: (),
            top: lambda: (
                self.move(self.side, 0),
                self.resize(m.width() - self.side * 2, self.side),
            ),
            topright: lambda: self.move(m.width() - self.side, 0),
            left: lambda: (
                self.move(0, self.side),
                self.resize(self.side, m.height() - self.side * 2),
            ),
            right: lambda: (
                self.move(m.width() - self.side, self.side),
                self.resize(self.side, m.height() - self.side * 2),
            ),
            botleft: lambda: self.move(0, m.height() - self.side),
            bot: lambda: (
                self.move(self.side, m.height() - self.side),
                self.resize(m.width() - self.side * 2, self.side),
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
                m.move(
                    m.x() + dx if m.width() - dx > m.minimumWidth() else m.x(),
                    m.y() + dy if m.height() - dy > m.minimumHeight() else m.y(),
                ),
                m.resize(m.width() - dx, m.height() - dy),
            ),
            top: lambda: (
                m.move(
                    m.x(), m.y() + dy if m.height() - dy > m.minimumHeight() else m.y()
                ),
                m.resize(m.width(), m.height() - dy),
            ),
            topright: lambda: (
                (
                    m.move(
                        m.x(),
                        m.y() + dy if m.height() - dy > m.minimumHeight() else m.y(),
                    ),
                    m.resize(m.width() + dx, m.height() - dy),
                )
            ),
            left: lambda: (
                m.move(
                    m.x() + dx if m.width() - dx > m.minimumWidth() else m.x(), m.y()
                ),
                m.resize(m.width() - dx, m.height()),
            ),
            right: lambda: m.resize(m.width() + dx, m.height()),
            botleft: lambda: (
                m.move(
                    m.x() + dx if m.width() - dx > m.minimumWidth() else m.x(), m.y()
                ),
                m.resize(m.width() - dx, m.height() + dy),
            ),
            bot: lambda: m.resize(m.width(), m.height() + dy),
            botright: lambda: m.resize(m.width() + dx, m.height() + dy),
        }
        funcs[self.loc]()

        self.mousepos = a0.globalPos()


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
    print(ex.children())
    sys.exit(app.exec_())
