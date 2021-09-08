import sys
from typing import ClassVar
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import (
    QBuffer,
    QLine,
    QLineF,
    QMargins,
    QMarginsF,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QRegExp,
    QSize,
    QSizeF,
    Qt,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QFontMetrics,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsOpacityEffect,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QWidget,
)

from ConfigManager import ConfigManager


from paintToolbar import PATH, LINE, RECT, CIRCLE, SELECT, PaintToolbar, DrawOptions


def smoothStep(p1: QPointF, p2: QPointF, amount: float):
    amount = (amount ** 2) * (3 - 2 * amount)
    return QPointF(
        (1 - amount) * p1.x() + p2.x() * amount, (1 - amount) * p1.y() + p2.y() * amount
    )


class Canvas:
    def __init__(
        self, scene: QGraphicsScene, view: QGraphicsView, toolbar: PaintToolbar
    ):
        self.scene = scene
        self.view = view
        self.toolbar = toolbar

        self.view.setRenderHints(
            QtGui.QPainter.HighQualityAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )

        self.drawOption: DrawOptions = toolbar.getDrawOptions()

        self.alt = False
        self.ctrl = False

        self.group = self.scene.createItemGroup([])

        self.objects = []
        self.currentObject = 0

        self.currentPos = QPoint()

        self.tempLine: QGraphicsLineItem = self.scene.addLine(QLineF(), QPen())
        self.tempLine.hide()

        self.drawingLine = False
        self.view.setMouseTracking(True)

    def updateCursor(self):

        self.view.setCursor(
            QCursor(
                self.toolbar.getCursors().get(
                    (self.drawOption.shape, self.ctrl, self.alt),
                    self.toolbar.getCursors().get((self.drawOption, False, False)),
                ),
                16,
                16,
            )
        )

    def onEnter(self, a0: QMouseEvent):
        self.drawOption = self.toolbar.getDrawOptions()
        self.updateCursor()

    def onClick(self, a0: QMouseEvent):

        self.iniPos = self.view.mapFromParent(a0.pos())
        mapped = self.view.mapToScene(self.iniPos)

        if a0.buttons() == Qt.MouseButton.RightButton and self.drawingLine:
            self.drawingLine = False
            self.tempLine.hide()
            self.finishLine()
            return

        if self.drawingLine:
            self.path.lineTo(mapped)
            self.lastPos = mapped
            self.currentObject.setPath(self.path)

            if not self.ctrl:
                self.drawingLine = False
                self.tempLine.hide()
                self.finishLine()

            return
        item = None
        opt = self.drawOption.shape
        filled = self.drawOption.brush.style() != Qt.BrushStyle.NoBrush
        if opt == PATH:
            self.currentLerpPos = self.iniPos
            self.path = QPainterPath(mapped)
            item = PathItem(
                filled, self.path
            )
            if self.ctrl:
                self.lockMode = "h"
                self.lockVal = self.iniPos.x()

            elif self.alt:
                self.lockMode = "v"
                self.lockVal = self.iniPos.y()
            else:
                self.lockMode = "n"

        elif opt == LINE:
            self.path = QPainterPath(mapped)
            item = PathItem(
                filled, self.path
            )
            self.lastPos = self.iniPos
            self.tempLine.show()
            self.tempLine.setPen(self.drawOption.pen)
            self.tempLine.setLine(QLineF(mapped, mapped))

            self.drawingLine = True
        elif opt == RECT:
            item = RectItem(filled)

        elif opt == CIRCLE:
            item = CircleItem(filled)
        elif opt == SELECT:
            print(self.view.itemAt(self.iniPos))
            return

        if (opt == RECT or opt == CIRCLE) and self.ctrl:
            self.lockMode = "b"
        elif not opt == PATH:
            self.lockMode = "n"

        item.setPos(self.view.mapToScene(self.iniPos))
        item.setPen(self.drawOption.pen)
        item.setBrush(self.drawOption.brush)
        item.setPos(QPointF(0, 0))

        opacityEffect = QGraphicsOpacityEffect()
        opacityEffect.setOpacity(self.drawOption.opacity)
        item.setGraphicsEffect(opacityEffect)

        self.currentObject = item
        self.group.addToGroup(item)
        self.objects.append(item)

    def onRelease(self, a0: QMouseEvent):
        s = self.drawOption.shape
        print("on release", s)
        if s == PATH or s == CIRCLE or s == RECT:
            self.finishLine()

    def finishLine(self):
        print("final")
        self.currentObject.finalize()

    def onMove(self, a0: QMouseEvent):
        self.currentPos = a0.pos()
        opt = self.drawOption.shape
        if a0.buttons() == Qt.MouseButton.LeftButton:
            if opt == PATH:

                if self.lockMode == "v":
                    self.path.lineTo(
                        self.view.mapToScene(QPoint(int(a0.x()), self.lockVal))
                    )
                elif self.lockMode == "h":
                    self.path.lineTo(
                        self.view.mapToScene(QPoint(self.lockVal, int(a0.y())))
                    )
                else:
                    self.currentLerpPos = smoothStep(
                        self.currentLerpPos, a0.pos(), 0.35
                    )
                    self.path.lineTo(
                        self.view.mapToScene(self.currentLerpPos.toPoint())
                    )

                self.currentObject.setPath(self.path)
            elif opt == RECT:
                if self.lockMode == "b":
                    dx = a0.x() - self.iniPos.x()
                    dy = a0.y() - self.iniPos.y()
                    size = QSizeF(1, 1).scaled(
                        QSizeF(dx, dy), Qt.AspectRatioMode.KeepAspectRatio
                    )
                    if dy > 0 and dx < 0:
                        size.setHeight(size.height() * -1)
                    elif dx > 0 and dy < 0:
                        size.setWidth(size.width() * -1)
                    self.currentObject.setRect(QRectF(self.iniPos, size).normalized())
                else:
                    self.currentObject.setRect(
                        QRectF(
                            self.view.mapToScene(self.iniPos),
                            self.view.mapToScene(a0.pos()),
                        ).normalized()
                    )

            elif opt == CIRCLE:
                size = QSizeF(a0.x() - self.iniPos.x(), a0.y() - self.iniPos.y())
                if self.lockMode == "b":
                    size = QSizeF(1, 1).scaled(size, Qt.AspectRatioMode.KeepAspectRatio)

                self.currentObject.setRect(
                    QRectF(
                        self.iniPos.x() - size.width() / 2,
                        self.iniPos.y() - size.height() / 2,
                        size.width(),
                        size.height(),
                    )
                )

        if opt == LINE and self.drawingLine:
            self.tempLine.show()
            mapped = self.view.mapToScene(a0.pos())
            self.tempLine.setLine(QLineF(self.lastPos, mapped))

    def keyDown(self, a0: QKeyEvent):

        if a0.key() == Qt.Key.Key_Control:
            self.ctrl = True

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = True

    def keyUp(self, a0: QKeyEvent):
        if a0.key() == Qt.Key.Key_Control:
            self.ctrl = False

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = False


class PathItem(QGraphicsPathItem):
    def __init__(self, filled=False, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.filled = filled

    def shape(self) -> QtGui.QPainterPath:
        if self.filled:
            return super().shape()
        else:
            p = QPainterPathStroker()
            p.setWidth(4)
            p.setCapStyle(Qt.PenCapStyle.SquareCap)
            p.createStroke(self.path())


class CanvasTesting(QWidget):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.resize(500, 500)

        self.scene = QGraphicsScene(self)

        layout = QHBoxLayout()

        self.view = QGraphicsView(self.scene)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(self.view)

        self.setLayout(layout)

        self.view.resize(self.size())
        self.view.setSceneRect(QRectF(0, 0, 500, 500))

        self.toolbar = PaintToolbar()
        self.toolbar.show()
        self.canvas = Canvas(self.scene, self.view, self.toolbar)

        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent

        self.setMouseTracking(True)
        self.show()

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.canvas.onEnter(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.canvas.onMove(a0)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        self.canvas.onClick(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        print("mouse release")
        self.canvas.onRelease(a0)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:

        self.canvas.keyDown(a0)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.canvas.keyUp(a0)


class CircleItem(QGraphicsEllipseItem):
    def __init__(self, filled=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filled = filled

        self.lineShape = None

    def finalize(self):

        path = QPainterPath()
        path.addEllipse(self.rect())
        p = QPainterPathStroker()

        p.setWidth(self.pen().width())
        self.lineShape = p.createStroke(path)

    def shape(self) -> QtGui.QPainterPath:
        if self.filled or self.lineShape is None:
            return super().shape()
        return self.lineShape


class RectItem(QGraphicsRectItem):
    def __init__(self, filled=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filled = filled

        self.lineShape = None

    def finalize(self):

        path = QPainterPath()
        path.addRect(self.rect())
        p = QPainterPathStroker()

        p.setWidth(self.pen().width())
        self.lineShape = p.createStroke(path)

    def shape(self) -> QtGui.QPainterPath:
        if self.filled or self.lineShape is None:
            return super().shape()
        return self.lineShape


class PathItem(QGraphicsPathItem):
    def __init__(self, filled=False, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.filled = filled

        self.lineShape = None

    def finalize(self):
        p = QPainterPathStroker()
        p.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setWidth(self.pen().width())
        self.lineShape = p.createStroke(self.path())

    def shape(self) -> QtGui.QPainterPath:
        if self.filled or self.lineShape is None:
            return super().shape()
        return self.lineShape


if __name__ == "__main__":

    app = QApplication(sys.argv)

    ex = CanvasTesting()
    sys.exit(app.exec_())
