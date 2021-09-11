from os import path
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
    QGraphicsItem,
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


from paintToolbar import (
    ERASE,
    PATH,
    LINE,
    RECT,
    CIRCLE,
    SELECT,
    PaintToolbar,
    DrawOptions,
)   


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
        self.currentObject = None
        self.currentLerpPos = QPointF()

        self.tempLine: QGraphicsLineItem = self.scene.addLine(QLineF(), QPen())
        self.tempLine.hide()

        self.drawingLine = False
        self.view.setMouseTracking(True)

    def updateCursor(self):

        self.view.setCursor(
            QCursor(
                *(
                    self.toolbar.getCursors().get(
                        (self.drawOption.shape, self.ctrl, self.alt),
                        self.toolbar.getCursors().get((self.drawOption, False, False)),
                    )
                ),
            )
        )
        
    def clear(self) :
        for item in self.objects:
            self.scene.removeItem(item)
        self.objects.clear()   
    
    def scale(self):
        return self.group.scale()
    
    def setScale(self, scale: float):
        self.group.setScale(scale)

    def onEnter(self, a0: QMouseEvent):
        print('updating')
        self.drawOption = self.toolbar.getDrawOptions()
        self.updateCursor()

    def onClick(self, a0: QMouseEvent):

        self.iniPos = self.view.mapFromParent(a0.pos())
        mapped = self.view.mapToScene(self.iniPos)
        opt = self.drawOption.shape
        self.lastPos = mapped

        # handling line behaviour
        if opt != LINE or (
            a0.buttons() == Qt.MouseButton.RightButton and self.drawingLine
        ):

            self.drawingLine = False
            self.tempLine.hide()
            self.finishLine()
            if opt == LINE:

                return

        if self.drawingLine:
            self.path.lineTo(mapped)

            self.currentObject.setPath(self.path)

            if not self.ctrl:
                self.drawingLine = False
                self.tempLine.hide()
                self.finishLine()
            return

        # dealing with select and erase

        if opt == SELECT:
            self.currentObject = self.view.itemAt(self.iniPos)

            self.offset = (
                (mapped - self.currentObject.pos())
                if self.currentObject is not None
                else None
            )
            return
        elif opt == ERASE:
            item = self.view.itemAt(self.iniPos)
            self.deleteObj(self.iniPos)
            return

        item = None
        filled = self.drawOption.brush.style() != Qt.BrushStyle.NoBrush
        if opt == PATH:
            self.currentLerpPos = mapped
            self.path = QPainterPath(mapped)
            item = PathItem(filled, self.path)
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
            item = PathItem(filled, self.path)
            self.lastPos = self.iniPos
            self.tempLine.show()
            self.tempLine.setPen(self.drawOption.pen)
            self.tempLine.setLine(QLineF(mapped, mapped))

            self.drawingLine = True
        elif opt == RECT:
            item = RectItem(filled)

        elif opt == CIRCLE:
            item = CircleItem(filled)

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
        if self.currentObject is not None:
            opt = self.drawOption.shape
            if opt == LINE or opt == PATH:
                if self.currentObject.path().length() == 0:
                    self.deleteObj(self.currentObject)
            elif opt == RECT or opt == CIRCLE:
                if self.currentObject.rect().size() == QSizeF():
                    self.deleteObj(self.currentObject)
            return
        s = self.drawOption.shape

        if s == PATH or s == CIRCLE or s == RECT:
            self.finishLine()

    def undo(self):
        if len(self.objects) > 0:
            self.deleteObj(self.objects[-1])

    def deleteObj(self, o):
        if isinstance(o, QGraphicsItem):
            item = o
        else:
            item = self.view.itemAt(o)
        if item is None:
            return
        self.objects.remove(item)
        self.scene.removeItem(item)

    def finishLine(self):
        if self.currentObject is None or type(self.currentObject) is QGraphicsPathItem:
            return
        self.currentObject.finalize()

    def onMove(self, a0: QMouseEvent):

        opt = self.drawOption.shape

        if a0.buttons() == Qt.MouseButton.LeftButton:
            mappedIniPos = self.view.mapToScene(self.iniPos)
            mappedCurPos = self.view.mapToScene(a0.pos())
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
                        self.currentLerpPos, mappedCurPos, 0.35
                    )
                    self.path.lineTo(self.currentLerpPos.toPoint())

                self.currentObject.setPath(self.path)

            elif opt == CIRCLE or opt == RECT:
                dx = mappedCurPos.x() - mappedIniPos.x()
                dy = mappedCurPos.y() - mappedIniPos.y()

                size = QSizeF(dx, dy)

                if self.lockMode == "b":
                    size = QSizeF(1, 1).scaled(size, Qt.AspectRatioMode.KeepAspectRatio)
                    if dy > 0 and dx < 0:
                        size.setHeight(size.height() * -1)
                    elif dx > 0 and dy < 0:
                        size.setWidth(size.width() * -1)

                if opt == CIRCLE:
                    self.currentObject.setRect(
                        QRectF(
                            mappedIniPos.x() - size.width(),
                            mappedIniPos.y() - size.height(),
                            size.width() * 2,
                            size.height() * 2,
                        ).normalized()
                    )
                elif opt == RECT:
                    self.currentObject.setRect(QRectF(mappedIniPos, size).normalized())

            elif opt == SELECT and self.currentObject is not None:
                self.currentObject.setPos(self.view.mapToScene(a0.pos()) - self.offset)
            elif opt == ERASE:
                self.deleteObj(a0.pos())

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
