from ConfigManager import ConfigManager
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    QBuffer,
    QMargins,
    QMarginsF,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    QSizeF,
    Qt,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QPen,
    QPixmap,
    QImage,
)
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QSizeGrip,
    QWidget,
)
import io

import desktopmagic.screengrab_win32
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from selectionbox import SelectionBox
import win32clipboard as clipboard
import os

from paintToolbar import PaintToolbar
from canvas import Canvas


class Snapshot(QWidget):
    def __init__(self, master, image=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.master = master

        self.cropping = False
        self.lastpos = None
        self.moveLock = False
        self.cropOffset = QPoint()
        self.mini = False

        if image:
            self.fromImage(image)
        else:
            self.fromFullscreen()




    def initialize(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow
        )

        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.scene = QGraphicsScene()

        self.displayPix = self.scene.addPixmap(QPixmap.fromImage(self.displayImage))
        self.displayPix.setZValue(0)
        self.displayPix.setPos(0, 0)

        self.borderRect = self.scene.addRect(
            QRectF(), QPen(QColor(200, 200, 200), 2), QBrush(Qt.BrushStyle.NoBrush)
        )
        self.borderRect.setZValue(100)

        self.view = QGraphicsView(self.scene)

        def resizeView(a0):
            QGraphicsView.resizeEvent(self.view, a0)
            self.borderRect.setRect(
                self.view.mapToScene(self.view.rect()).boundingRect()
            )

        def setRect(newR):
            QGraphicsView.setSceneRect(self.view, newR)
            self.borderRect.setRect(self.view.sceneRect())

        self.view.resizeEvent = resizeView
        self.view.setSceneRect = setRect
        self.view.setStyleSheet("background-color: rgba(40, 40, 40, 0.5); border: 0px")

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.resize(self.displayPix.boundingRect().size().toSize())

        self.resize(self.view.size())

        self.selectionBox = SelectionBox(1, self)
        self.selectionBox.hide()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(QMargins())

        self.layout.addWidget(self.view)

        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent

        self.grip = QSizeGrip(self)
        self.grip.resize(16, 16)

        def press(a):
            QSizeGrip.mousePressEvent(self.grip, a)
            self.moveLock = True

        def release(a):
            QSizeGrip.mouseReleaseEvent(self.grip, a)
            self.moveLock = False

        self.grip.mousePressEvent = press
        self.grip.mouseReleaseEvent = release


        self.currentRect = (0, 0, 0, 0)
        self.currentWidth = self.displayImage.width()
        
        #test canvas
        import values
        self.config = ConfigManager('D:\PythonProject\screenCap\QtExperimental\config.ini',values.defaultVariables )
        self.toolbar = PaintToolbar(self.config)
        self.toolbar.hide()
        self.canvas = Canvas(self.scene, self.view, self.toolbar)
        
        self.painting = False
        

        self.showNormal()
        self.view.setSceneRect(self.displayPix.boundingRect())
    
    
    def startPaint(self):
        self.painting = True
        self.toolbar.show()
        self.canvas.updateCursor()
        
    def stopPaint(self):
        self.painting = False
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
    
    
    

    def fromImage(self, image: Image.Image):
        image.putalpha(255)
        self.originalImage = image
        self.displayImage: QImage = ImageQt(image)
        self.fullscreenCrop = False
        self.move(QCursor.pos())
        self.initialize()
        self.displayPix.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )

    def fromFullscreen(self):
        image = desktopmagic.screengrab_win32.getRectAsImage(self.getBoundBox())
        image.putalpha(255)

        self.originalImage = ImageQt(image)
        self.displayImage = self.originalImage
        self.fullscreenCrop = True

        self.move(*(x for x in self.getBoundBox()[:2]))

        self.initialize()

        c = QColor(0, 0, 0, 100)
        r = QRectF()
        p = QPen(QColor(0, 0, 0, 0), 0)
        self.maskingtop: QGraphicsRectItem = self.scene.addRect(
            self.view.sceneRect(), p, c
        )
        self.maskingleft: QGraphicsRectItem = self.scene.addRect(r, p, c)
        self.maskingright: QGraphicsRectItem = self.scene.addRect(r, p, c)
        self.maskingbot: QGraphicsRectItem = self.scene.addRect(r, p, c)

        self.startCrop(margin=2, useOriginal=True)

    def getNonScaledImage(self):
        return self.displayImage.copy(QRectF(*self.currentRect).toRect())

    def getScaledImage(self):
        return self.displayImage.copy(QRectF(*self.currentRect).toRect()).scaled(
            self.displayPix.scale() * self.displayImage.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def copy(self):
        im = self.getNonScaledImage()
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        im.save(buffer, 'BMP')
        with io.BytesIO(buffer.data()) as bytes:
            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardData(clipboard.CF_DIB, bytes.getvalue()[14:])
            clipboard.CloseClipboard()
    
    def save(self):
        
        filename, _ = QFileDialog.getSaveFileName(self, 'Choose save location', os.getenv('HOME'), 'Image files (*.png *.jpg)')

    def startCrop(self, margin=0, useOriginal=False):
        if self.cropping:
            return

        self.cropping = True
        self.cropMargin = margin
        self.usingOriginal = useOriginal

        if useOriginal:
            self.move(
                self.pos()
                - QPoint(margin, margin)
                - (self.view.sceneRect().topLeft() - self.displayPix.pos()).toPoint()
            )
            self.view.setSceneRect(
                self.displayPix.sceneBoundingRect().marginsAdded(
                    QMarginsF(margin, margin, margin, margin)
                )
            )
        else:
            self.originalOffset = self.view.sceneRect().topLeft()
            self.displayPix.setPixmap(
                QPixmap.fromImage(
                    self.displayImage.copy(QRectF(*self.currentRect).toRect())
                )
            )
            self.view.setSceneRect(
                self.displayPix.sceneBoundingRect().marginsAdded(
                    QMarginsF(margin, margin, margin, margin)
                )
            )
            self.move(self.pos() - QPoint(margin, margin))

        self.resize(self.view.sceneRect().size().toSize())
        self.displayPix.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )

    def replaceOriginal(self):

        self.displayImage = self.displayImage.copy(self.view.sceneRect().toRect())

        self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))
        self.displayPix.setPos(QPoint())
        self.view.setSceneRect(self.displayPix.boundingRect())

        self.cropOffset = QPointF()
        self.currentRect = (0, 0, self.width(), self.height())
        self.currentWidth = self.displayImage.width()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if not self.cropping and not self.mini:
            fullwidth = self.displayImage.width() * self.displayPix.scale()

            size = QSizeF(*self.currentRect[2:])
            size.scale(QSizeF(a0.size()), Qt.AspectRatioMode.KeepAspectRatio)

            self.displayPix.setScale(
                (
                    fullwidth
                    + ((size.width() - self.currentWidth) / self.currentWidth)
                    * fullwidth
                )
                / self.displayImage.width()
            )

            displayrect = QRectF(
                *(i * self.displayPix.scale() for i in self.currentRect)
            )

            self.currentWidth = size.width()
            self.view.setSceneRect(displayrect)
            self.resize(size.toSize())

        self.grip.move(self.rect().bottomRight() - QPoint(16, 16))

    def stopCrop(self, canceling=False):

        if not canceling:
            rect = self.view.mapToScene(self.selectionBox.geometry()).boundingRect()
        else:
            rect = self.view.sceneRect()

        if rect.width() < 40 or rect.height() < 40:
            self.selectionBox.hide()
            return

        limit = self.displayPix.sceneBoundingRect()

        rect = limit.intersected(rect)

        self.cropOffset = rect.topLeft()

        self.move(
            (rect.topLeft() + self.pos() - self.view.sceneRect().topLeft()).toPoint()
        )

        if not self.usingOriginal:
            rect.moveTopLeft(rect.topLeft() + self.originalOffset)
            self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))

        self.view.setSceneRect(rect)

        self.resize(rect.size().toSize())
        self.selectionBox.hide()
        self.cropping = False

        scale = self.displayPix.scale()
        self.currentRect = (
            rect.x() / scale,
            rect.y() / scale,
            rect.width() / scale,
            rect.height() / scale,
        )
        self.currentWidth = rect.width()

        if self.fullscreenCrop:
            self.replaceOriginal()
            self.fullscreenCrop = False
            self.maskingright.hide()
            self.maskingleft.hide()
            self.maskingtop.hide()
            self.maskingbot.hide()

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        a0.accept()

    def mouseReleaseEvent(self, a0: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        
        if self.painting:
            self.canvas.onRelease(a0)
        
        if self.cropping:
            self.stopCrop()
            
    def enterEvent(self, a0) -> None:
        if self.painting:
            self.canvas.onEnter(a0)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.cropping:
            return

        if not self.mini:
            self.mini = True

            self.originalOffset = a0.pos() - QPoint(40, 40)
            self.view.setSceneRect(
                QRectF(self.view.mapToScene(a0.pos() - QPoint(40, 40)), QSizeF(80, 80))
            )
            self.move(self.originalOffset + self.pos())
            self.resize(80, 80)
            self.borderRect.setPen(QPen(QColor(100, 90, 250), 3.5, Qt.PenStyle.DotLine))
        else:
            self.mini = False
            self.move(self.pos() - self.originalOffset)
            rect = QRectF(*(self.displayPix.scale() * i for i in self.currentRect))
            self.resize(rect.size().toSize())
            self.view.setSceneRect(rect)
            self.borderRect.setPen(QPen(QColor(200, 200, 200), 2))

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.painting:
            self.canvas.onClick(a0)
            return
        
        self.inipos = a0.pos()
        self.lastpos = a0.globalPos()

        if self.cropping:
            self.selectionBox.show()
            self.selectionBox.raise_()
            self.selectionBox.move(a0.pos())

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.painting:
            self.canvas.onMove(a0)
            return

        if a0.buttons() == Qt.MouseButton.LeftButton:
            if self.cropping :

                rect = QRect(self.inipos, a0.pos()).normalized()
                self.selectionBox.setGeometry(rect)

                vrect = self.view.sceneRect()

                self.maskingtop.setRect(
                    QRectF(QPointF(0, 0), QSizeF(vrect.width(), rect.top()))
                )
                self.maskingleft.setRect(
                    QRectF(QPointF(0, rect.top()), QSizeF(rect.left(), rect.height()))
                )
                self.maskingbot.setRect(
                    QRectF(
                        QPointF(0, rect.bottom()),
                        QSizeF(vrect.width(), vrect.height() - rect.bottom()),
                    )
                )
                self.maskingright.setRect(
                    QRectF(
                        QPointF(rect.right(), rect.top()),
                        QSizeF(vrect.width() - rect.right(), rect.height()),
                    )
                )
            elif not self.moveLock:
                delta = a0.globalPos() - self.lastpos
                self.move(self.pos() + delta)

                self.lastpos = a0.globalPos()


    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if self.painting:
            self.canvas.keyUp(a0)
            

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        
        if a0.key() == Qt.Key.Key_P:
            self.startPaint()
        
        if self.painting:
            self.canvas.keyDown(a0)
            return


        if a0.key() == Qt.Key.Key_Escape:
            if self.fullscreenCrop or not self.cropping:
                print("closing")
                self.close()
            elif self.cropping:
                self.stopCrop(canceling=True)

        if a0.key() == Qt.Key.Key_Space:
            #self.startCrop(50, False)
            self.copy()

    def getBoundBox(self):
        bounds = desktopmagic.screengrab_win32.getDisplayRects()
        pos = QCursor.pos()
        x = pos.x()
        y = pos.y()
        for bound in bounds:
            if x >= bound[0] and y >= bound[1] and x <= bound[2] and y <= bound[3]:
                return bound
        return bounds[0]

    def enterEvent(self, a0) -> None:
        if self.painting:
            self.canvas.onEnter(a0)
        
        if self.fullscreenCrop or self.cropping or self.mini:
            self.grip.hide()
        else:
            self.grip.show()

    def leaveEvent(self, a0) -> None:
        if self.painting:
            self.canvas.onExit(a0)
            return
        self.grip.hide()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = Snapshot(None, None)
    sys.exit(app.exec_())
