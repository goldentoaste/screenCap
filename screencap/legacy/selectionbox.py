import sys
from typing import List

from PySide6 import QtGui, QtWidgets

from PySide6.QtCore import QPoint, QRect, QRectF, Qt

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
    def __init__(self, a0, parent, changeCallback=None) -> None:
        super().__init__(a0, parent=parent)

        self.grips: List[SizeGrip] = []
        if changeCallback:
            self.callback = changeCallback
        else:
            self.callback = lambda: ()

        for i in range(8):
            self.grips.append(SizeGrip(self, i))

        # self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.show()

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        for grip in self.grips:
            grip.updatePos()
        self.callback(self.rect().translated(self.pos()))

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:

        for grip in self.grips:
            grip.updatePos()
        self.callback(self.rect().translated(self.pos()))

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.lastpos = a0.globalPos()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.move(
            max(
                0,
                min(
                    self.x() + a0.globalX() - self.lastpos.x(),
                    self.parent().width() - self.width(),
                ),
            ),
            max(
                0,
                min(
                    self.y() + a0.globalY() - self.lastpos.y(),
                    self.parent().height() - self.height(),
                ),
            ),
        )
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

    # seperating on the functions inside of dictionary, redefining these lambda each time is pointless.
    def updatePos(self):
        m = self.master
        # if else is prob faster than dictionary creation and then lookup.
        if self.loc == top:
            self.move(self.side, 0),
            self.resize(m.width() - self.side * 2, self.side)
        elif self.loc == topright:
            self.move(m.width() - self.side, 0)
        elif self.loc == left:
            self.move(0, self.side),
            self.resize(self.side, m.height() - self.side * 2)
        elif self.loc == right:
            self.move(m.width() - self.side, self.side),
            self.resize(self.side, m.height() - self.side * 2)
        elif self.loc == botleft:
            self.move(0, m.height() - self.side)
        elif self.loc == bot:
            self.move(self.side, m.height() - self.side),
            self.resize(m.width() - self.side * 2, self.side)
        elif self.loc == botright:
            self.move(m.width() - self.side, m.height() - self.side)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        self.mousepos = a0.globalPos()

    keepInBound = {
        topleft: lambda rect, dx, dy: (rect.topLeft() + QPoint(dx, dy)),
        top: lambda rect, dx, dy: (rect.topLeft() + QPoint(0, dy)),
        topright: lambda rect, dx, dy: (rect.topRight() + QPoint(dx, dy)),
        left: lambda rect, dx, dy: (rect.topLeft() + QPoint(dx, 0)),
        right: lambda rect, dx, dy: (rect.topRight() + QPoint(dx, 0)),
        bot: lambda rect, dx, dy: (rect.bottomLeft() + QPoint(0, dy)),
        botleft: lambda rect, dx, dy: (rect.bottomLeft() + QPoint(dx, dy)),
        botright: lambda rect, dx, dy: (rect.bottomRight() + QPoint(dx, dy)),
    }

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        dx = a0.globalX() - self.mousepos.x()
        dy = a0.globalY() - self.mousepos.y()

        m = self.master
        rect = m.rect().translated(m.pos())
        result: QPoint = SizeGrip.keepInBound[self.loc](rect, dx, dy)

        rect: QRect = self.parent().parent().rect()
        if not (0 < result.x() < rect.width()):
            dx = 0

        if not (0 < result.y() < rect.height()):
            dy = 0

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
    s = SelectionBox(1, ex, lambda rect: ())
    # t = test(ex)
    ex.show()
    print(ex.children())
    sys.exit(app.exec_())
