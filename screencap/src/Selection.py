from enum import Enum
import sys
from weakref import ref
from PySide6.QtCore import QPoint, QPointF, QRect, QSize, QSizeF, Qt
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QRubberBand, QWidget

from screencap.src.GlobalContext import GlobalContext


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

    def __init__(self, parent: QWidget, clampRect: QRect | None = None) -> None:
        super().__init__(QRubberBand.Shape.Rectangle, parent)
        self._margin = 12
        self.margin = 12  # px around edges that are mouse gripper area
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self.pressed = False
        self.refRect = QRect()
        self.iniPoint = QPoint()

        self.pen = QPen(
            QColor(GlobalContext.getCtx().getConfig().border), 3, Qt.PenStyle.DotLine
        )
        self.brush = QBrush(Qt.BrushStyle.NoBrush)

        self.dir: Dir = Dir.NA

        if clampRect:
            self.clampRect = clampRect
        else:
            self.clampRect = parent.rect()


    def setRect(self, p1: QPoint, p2: QPoint):
        self.setGeometry(QRect(p1, p2).normalized())


    def setUseMinSize(self, opt: bool):
        if opt:
            self.margin = self._margin
            self.setMinimumSize(self.margin * 3, self.margin * 3)
        else:
            self.margin = 0
            self.setMinimumSize(QSize(0,0))
            self.setGeometry(QRect(self.pos(), QSize(0,0)))
            print(self.geometry())

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
        if self.cursor().shape() == Qt.CursorShape.ClosedHandCursor:
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
                y = min(y, self.clampRect.bottom() - self.refRect.bottom())
                self.resize(self.refRect.width(), self.refRect.height() + y)
            case Dir.botLeft:
                x = max(self.clampRect.top() - self.refRect.left(), x)
                y = min(y, self.clampRect.bottom() - self.refRect.bottom())
                self.move(
                    self.refRect.x()
                    + min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y(),
                )
                self.resize(self.refRect.width() - x, self.refRect.height() + y)
            case Dir.botRight:
                x = min(self.clampRect.right() - self.refRect.right(), x)
                y = min(y, self.clampRect.bottom() - self.refRect.bottom())
                self.resize(self.refRect.width() + x, self.refRect.height() + y)
            case Dir.left:
                x = max(self.clampRect.left() - self.refRect.left(), x)
                self.move(
                    self.refRect.x()
                    + min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y(),
                )
                self.resize(self.refRect.width() - x, self.refRect.height())
            case Dir.right:
                x = min(self.clampRect.right() - self.refRect.right(), x)

                self.resize(self.refRect.width() + x, self.refRect.height())
            case Dir.topLeft:
                x = max(self.clampRect.left() - self.refRect.left(), x)
                y = max(self.clampRect.top() - self.refRect.top(), y)
                self.move(
                    self.refRect.x()
                    + min(x, self.refRect.width() - self.minimumWidth()),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width() - x, self.refRect.height() - y)
            case Dir.topRight:
                y = max(self.clampRect.top() - self.refRect.top(), y)
                x = min(self.clampRect.right() - self.refRect.right(), x)

                self.move(
                    self.refRect.x(),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width() + x, self.refRect.height() - y)
            case Dir.top:
                y = max(self.clampRect.top() - self.refRect.top(), y)

                self.move(
                    self.refRect.x(),
                    self.refRect.y()
                    + min(y, self.refRect.height() - self.minimumHeight()),
                )
                self.resize(self.refRect.width(), self.refRect.height() - y)
            case Dir.mid:
                self.move(self.refRect.x() + x, self.refRect.y() + y)

        self.move(
            max(
                self.clampRect.left(),
                min(self.clampRect.right() - self.width(), self.x()),
            ),
            max(
                self.clampRect.top(),
                min(self.clampRect.bottom() - self.height(), self.y()),
            ),
        )

    def clamp(self):
        rect = self.geometry()
        rect.setLeft(max(rect.left(), self.clampRect.left()))
        rect.setRight(min(rect.right(), self.clampRect.right()))
        rect.setTop(max(rect.top(), self.clampRect.top()))
        rect.setBottom(min(rect.bottom(), self.clampRect.bottom()))

        self.setGeometry(rect)

    def paintEvent(self, e: QPaintEvent) -> None:
        # super().paintEvent(e)

        painter = QPainter(self)

        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(self.rect())


class Test(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 500, 500)

        self.box = SelectionBox(self, QRect(100, 100, 333, 333))
        self.box.move(100, 100)
        self.box.resize(200, 75)

        self.show()

        self.box.show()


if __name__ == "__main__":
    app = QApplication()
    t = Test()

    sys.exit(app.exec())
