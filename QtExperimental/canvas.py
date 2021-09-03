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


class Canvas:
    def __init__(
        self, scene: QGraphicsScene, view: QGraphicsView, toolbar: PaintToolbar
    ):
        self.scene = scene
        self.view = view
        self.toolbar = toolbar

        self.drawOption: DrawOptions = toolbar.getDrawOptions()

        self.alt = False
        self.ctrl = False

        self.group = self.scene.createItemGroup([])

        self.objects = []
        self.currentObject = 0

        self.currentPos = QPoint()

    def onEnter(self, a0: QMouseEvent):
        self.drawOption = self.toolbar.getDrawOptions()

    def onClick(self, a0: QMouseEvent):
        print('clikc!!!!!!!')
        self.iniPos = a0.pos()
        self.lastPos = a0.pos()

        item = None

        opt = self.drawOption.shape

        if opt == PATH or opt == LINE:
            path = QPainterPath(self.view.mapToScene(self.iniPos))
            item = QGraphicsPathItem(path)
        elif opt == RECT:
            item = QGraphicsRectItem()
        elif opt == CIRCLE:
            item = QGraphicsEllipseItem()

        item.setPos(self.view.mapToScene(self.iniPos))
        self.currentObject = item
        self.

    def onRelease(self, a0: QMouseEvent):
        pass

    def onMove(self, a0: QMouseEvent):
        if a0.buttons() == Qt.MouseButton.LeftButton:
            opt = self.drawOption.shape
            print('dragggg', a0.pos())
            if opt == PATH:
                print('???/')
                if self.alt:
                    self.currentObject.path().lineTo(
                        self.view.mapToScene(QPoint(a0.x(), self.altPos.y()))
                    )
                elif self.ctrl:
                    self.currentObject.path().lineTo(
                        self.view.mapToScene(QPoint(self.ctrlPos.x(), a0.y()))
                    )
                else:
                    self.currentObject.path().lineTo(self.view.mapToScene(a0.pos()))

        else:
            self.currentPos = a0.pos()

    def keyDown(self, a0: QKeyEvent):

        if a0.key() == Qt.Key.Key_Control:
            self.ctrl = True
            self.ctrlPos = QPoint(self.currentPos.x(), self.currentPos.y())

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = True
            self.altPos = QPoint(self.currentPos.x(), self.currentPos.y())

    def keyUp(self, a0: QKeyEvent):
        pass


class CanvasTesting(QWidget):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.resize(500, 500)

        self.scene = QGraphicsScene(self)

        layout = QHBoxLayout()

        self.view = QGraphicsView(self.scene)

        layout.addWidget(self.view)

        self.setLayout(layout)

        self.view.resize(self.size())
        
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
        self.canvas.keyUp(a0)
        
        

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
   
    ex = CanvasTesting()
    sys.exit(app.exec_())
