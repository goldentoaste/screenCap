from enum import Enum
import sys
from weakref import ref
from PySide6.QtCore import QPoint, QPointF, QRect, QSize, QSizeF, Qt
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QRubberBand, QWidget


class Dir(Enum):
    NA = -2
    mid = -1
    top = 0
    topLeft = 1
    topRight = 2
    left = 3
    right = 4
    botLeft = 5
    bot = 6
    botRight = 7


class SelectionBox(QRubberBand):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(QRubberBand.Shape.Rectangle, parent)
        self.margin = 10  # px around edges that are mouse gripper area
        self.setMinimumSize(self.margin * 3, self.margin * 3)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self._parent: QWidget = parent

        self.pressed = False
        self.refRect = QRect()
        self.iniPoint = QPoint()

        self.dir: Dir = Dir.NA

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if not e.buttons() & Qt.MouseButton.LeftButton:
            return

        self.refRect = self.geometry()

        self.iniPoint = e.globalPosition()
        self.pressed = True

        self.updateCursorDirection(e)

    def updateCursorDirection(self, e: QMouseEvent):
        x = e.position().x()
        y = e.position().y()

        rect = self.rect()

        top = rect.top()
        left = rect.left()
        right = rect.right()
        bot = rect.bottom()

        if y - top <= self.margin:
            if x - left <= self.margin:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                self.dir = Dir.topLeft
            elif right - x <= self.margin:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                self.dir = Dir.topRight
            else:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self.dir = Dir.top
        elif bot - y <= self.margin:
            if x - left <= self.margin:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                self.dir = Dir.botLeft

            elif right - x <= self.margin:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                self.dir = Dir.botRight
            else:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self.dir = Dir.bot
        else:
            if x - left <= self.margin:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self.dir = Dir.left

            elif right - x <= self.margin:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self.dir = Dir.right
            else:
                self.dir = Dir.mid
                if e.button() != Qt.MouseButton.LeftButton:
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                else:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.dir = Dir.NA
        self.pressed = False
        if self.cursor() == Qt.CursorShape.ClosedHandCursor:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if not self.pressed:
            self.updateCursorDirection(e)
            return

        diff = e.globalPosition() - self.iniPoint
        x = round(diff.x())
        y = round(diff.y())

        match self.dir:
            case Dir.bot:
                y = min(y, self._parent.height() - self.refRect.bottom())
                self.resize(self.refRect.width(), self.refRect.height() + y)
            case Dir.botLeft:
                x = max(-self.refRect.left(), x)
                y = min(y, self._parent.height() - self.refRect.bottom())
                self.move(
                    self.refRect.x()
                    + +min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y(),
                )
                self.resize(self.refRect.width() - x, self.refRect.height() + y)
            case Dir.botRight:
                x = min(self._parent.width() - self.refRect.right(), x)
                y = min(y, self._parent.height() - self.refRect.bottom())
                self.resize(self.refRect.width() + x, self.refRect.height() + y)
            case Dir.left:
                x = max(-self.refRect.left(), x)
                self.move(
                    self.refRect.x()
                    + min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y(),
                )
                self.resize(self.refRect.width() - x, self.refRect.height())
            case Dir.right:
                x = min(self._parent.width() - self.refRect.right(), x)

                self.resize(self.refRect.width() + x, self.refRect.height())
            case Dir.topLeft:
                x = max(-self.refRect.left(), x)
                y = max(-self.refRect.top(), y)
                self.move(
                    self.refRect.x()
                    + min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width() - x, self.refRect.height() - y)
            case Dir.topRight:
                y = max(-self.refRect.top(), y)
                x = min(self._parent.width() - self.refRect.right(), x)

                self.move(
                    self.refRect.x(),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width() + x, self.refRect.height() - y)
            case Dir.top:
                y = max(-self.refRect.top(), y)

                self.move(
                    self.refRect.x(),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width(), self.refRect.height() - y)
            case Dir.mid:
                self.move(self.refRect.x() + x, self.refRect.y() + y)

        self.move(
            max(0, min(self._parent.width() - self.width(), self.x())),
            max(0, min(self._parent.height() - self.height(), self.y())),
        )

    def paintEvent(self, e: QPaintEvent) -> None:
        super().paintEvent(e)

        painter = QPainter(self)

        painter.setPen(QPen(QColor(100, 100, 150), 3, Qt.PenStyle.DotLine))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(self.rect())


class Test(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 500, 500)

        self.box = SelectionBox(self)
        self.box.move(100, 100)
        self.box.resize(200, 75)

        self.show()

        self.box.show()


if __name__ == "__main__":
    app = QApplication()
    t = Test()

    sys.exit(app.exec())
