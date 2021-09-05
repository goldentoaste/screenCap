import sys
from typing import ClassVar
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import (
    QBuffer,
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
    QPen,
    QPixmap,
    QImage,
    QRegExpValidator,
)
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizeGrip,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ConfigManager import ConfigManager
import re

from paintToolbar import PATH, LINE, RECT, CIRCLE, PaintToolbar, DrawOptions


def smoothStep(p1: QPointF, p2: QPointF, amount: float):
    amount = (amount**2 )* (3 - 2 * amount)
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

        self.view.setRenderHints(QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.drawOption: DrawOptions = toolbar.getDrawOptions()

        self.alt = False
        self.ctrl = False

        self.group = self.scene.createItemGroup([])

        self.objects = []
        self.currentObject = 0

        self.currentPos = QPoint()

        self.testrect = self.scene.addRect(
            QRectF(), QColor(0, 0, 0), self.drawOption.brush
        )

    def onEnter(self, a0: QMouseEvent):
        self.drawOption = self.toolbar.getDrawOptions()

    def onClick(self, a0: QMouseEvent):

        self.iniPos = self.view.mapFromParent(a0.pos())
        self.lastPos = self.iniPos
        self.currentLerpPos = a0.pos()

        item = None

        opt = self.drawOption.shape

        if opt == PATH or opt == LINE:
            self.path = QPainterPath(self.view.mapToScene(self.iniPos))
            item = QGraphicsPathItem(self.path)

            self.currentPath = QPainterPath()
        elif opt == RECT:
            item = QGraphicsRectItem()
            return
        elif opt == CIRCLE:
            item = QGraphicsEllipseItem()
            return

        item.setPos(self.view.mapToScene(self.iniPos))
        item.setPen(self.drawOption.pen)
        item.setBrush(self.drawOption.brush)
        item.setPos(QPointF(0, 0))

        self.currentObject = item
        self.group.addToGroup(item)
        self.objects.append(item)

    def onRelease(self, a0: QMouseEvent):
        pass

    def onMove(self, a0: QMouseEvent):
        if a0.buttons() == Qt.MouseButton.LeftButton:
            opt = self.drawOption.shape
            if opt == PATH:
                self.currentLerpPos = smoothStep(self.currentLerpPos, a0.pos(), 0.35)
                if self.alt:
                    self.path.lineTo(
                        self.view.mapToScene(
                            QPoint(int(self.currentLerpPos.x()), self.altPos.y())
                        )
                    )
                elif self.ctrl:
                    self.path.lineTo(
                        self.view.mapToScene(
                            QPoint(self.ctrlPos.x(), int(self.currentLerpPos.y()))
                        )
                    )
                else:
                    self.path.lineTo(
                        self.view.mapToScene(self.currentLerpPos.toPoint())
                    )

                self.currentObject.setPath(self.path)
        
        self.currentPos = a0.pos()

    

    def keyDown(self, a0: QKeyEvent):
        print('??')
        if a0.key() == Qt.Key.Key_Control:
            print('ctrl')
            self.ctrl = True
            self.ctrlPos = QPoint(self.currentPos.x(), self.currentPos.y())

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = True
            self.altPos = QPoint(self.currentPos.x(), self.currentPos.y())

    def keyUp(self, a0: QKeyEvent):
        if a0.key() == Qt.Key.Key_Control:
            
            self.ctrl = False
            

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = False
            


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
        print('key prss')
        self.canvas.keyDown(a0)
        
    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.canvas.keyUp(a0)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    ex = CanvasTesting()
    sys.exit(app.exec_())
