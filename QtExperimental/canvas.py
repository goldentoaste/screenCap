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
    QGraphicsLineItem,
    QGraphicsOpacityEffect,
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

        self.tempLine : QGraphicsLineItem = self.scene.addLine(QLineF(), QPen())
        self.tempLine.hide()
        
        self.drawingLine = False
        self.view.setMouseTracking(True)



    def onEnter(self, a0: QMouseEvent):
        self.drawOption = self.toolbar.getDrawOptions()

    def onClick(self, a0: QMouseEvent):

        self.iniPos = self.view.mapFromParent(a0.pos())
        mapped = self.view.mapToScene(self.iniPos)
        
        if a0.buttons() == Qt.MouseButton.RightButton:
            self.drawingLine = False
            self.tempLine.hide()
            return
        
        if self.drawingLine: 
            self.path.lineTo(mapped)
            self.lastPos = mapped
            self.currentObject.setPath(self.path)
            
            if not self.ctrl:
                self.drawingLine = False
                self.tempLine.hide()
                
            return

        
        item = None

        opt = self.drawOption.shape

        if opt == PATH:
            self.currentLerpPos = self.iniPos
            self.path = QPainterPath(mapped)
            item = QGraphicsPathItem(self.path)
            if self.ctrl:
                print('ctrl')
                self.lockMode = 'h'
                self.lockVal = self.iniPos.x()

            elif self.alt:
                print('alt')
                self.lockMode = 'v'
                self.lockVal= self.iniPos.y()
            else:
                print('none')
                self.lockMode = 'n'
            
        elif opt == LINE:
            self.path = QPainterPath(mapped)
            item = QGraphicsPathItem(self.path)
            self.lastPos = self.iniPos
            self.tempLine.show()
            self.tempLine.setPen(self.drawOption.pen)
            self.tempLine.setLine(QLineF(mapped,mapped))
            
            self.drawingLine = True
        elif opt == RECT:
            item = QGraphicsRectItem()
            

        elif opt == CIRCLE:
            item = QGraphicsEllipseItem()
        
        if (opt == RECT or opt == CIRCLE) and self.ctrl:
            self.lockMode = 'b'
        else:
            self.lockMode = 'n'
        

        item.setPos(self.view.mapToScene(self.iniPos))
        item.setPen(self.drawOption.pen)
        item.setBrush(self.drawOption.brush)
        item.setPos(QPointF(0, 0))
        
        item.setGraphicsEffect(QGraphicsOpacityEffect())
        item.setOpacity(self.drawOption.opacity)
        print(self.drawOption.opacity)
        

        self.currentObject = item
        self.group.addToGroup(item)
        self.objects.append(item)

    def onRelease(self, a0: QMouseEvent):
        pass

    def onMove(self, a0: QMouseEvent):
        self.currentPos = a0.pos()
        opt = self.drawOption.shape
        if a0.buttons() == Qt.MouseButton.LeftButton:
            if opt == PATH:
                if self.lockMode == 'v':
                    self.path.lineTo(
                        self.view.mapToScene(
                            QPoint(int(a0.x()), self.lockVal)
                        )
                    )
                elif self.lockMode == 'h':
                    self.path.lineTo(
                        self.view.mapToScene(   
                            QPoint(self.lockVal, int(a0.y()))
                        )
                    )
                else:
                    self.currentLerpPos = smoothStep(self.currentLerpPos, a0.pos(), 0.35)
                    self.path.lineTo(
                        self.view.mapToScene(self.currentLerpPos.toPoint())
                    )

                self.currentObject.setPath(self.path)
    
            elif opt == RECT:
                
                if self.lockMode == 'b':
                    size = QSizeF(1, 1).scaled(QSizeF(a0.x() - self.iniPos.x(), a0.y() - self.iniPos.y()), Qt.AspectRatioMode.KeepAspectRatio)
                    self.currentObject.setRect(QRectF(self.iniPos, size).normalized())
                    
                else:
                    self.currentObject.setRect(QRectF(self.view.mapToScene(self.iniPos), self.view.mapToScene(a0.pos())).normalized())
                    
                    
            elif opt == CIRCLE:
                size = QSizeF(a0.x() - self.iniPos.x(), a0.y() - self.iniPos.y())
                if self.lockMode == 'b':
                    size = QSizeF(1, 1).scaled(size, Qt.AspectRatioMode.KeepAspectRatio)
                
                self.currentObject.setRect(QRectF(self.iniPos.x() - size.width() /2, self.iniPos.y() - size.height()/2, size.width(), size.height()))
                
            
                
            
        
        if opt == LINE and self.drawingLine:
            self.tempLine.show()
            mapped = self.view.mapToScene(a0.pos())
            self.tempLine.setLine(QLineF(self.lastPos, mapped))

    

    def keyDown(self, a0: QKeyEvent):
        print(a0.key())
        if a0.key() == Qt.Key.Key_Control:
            self.ctrl = True
            

        elif a0.key() == Qt.Key.Key_Alt:
            self.alt = True

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
