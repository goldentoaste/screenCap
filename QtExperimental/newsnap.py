from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
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
from PyQt5.QtGui import QColor, QCursor, QPen, QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QSizeGrip,
    QSizePolicy,
    QWidget,
)

import desktopmagic.screengrab_win32
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
from selectionbox import SelectionBox


class Snapshot(QWidget):
    def __init__(self, master, image=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.master = master

        self.cropping = False
        self.lastpos = None
        self.moveLock = False

        if image:
            self.fromImage(image)
        else:
            self.fromFullscreen()

    def initialize(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )

        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.scene = QGraphicsScene()

        self.displayPix = self.scene.addPixmap(QPixmap.fromImage(self.displayImage))
        self.displayPix.setZValue(0)
        self.displayPix.setPos(0, 0)

        self.view = QGraphicsView(self.scene)

        self.view.setStyleSheet("background-color: rgba(40, 40, 40, 0.5)")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.resize(self.displayPix.boundingRect().size().toSize())
        self.resize(self.view.size())

        self.selectionBox = SelectionBox(1, self)
        self.selectionBox.hide()

        self.setLayout(QHBoxLayout())

        self.layout().addWidget(self.view)

        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

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
        self.view.wheelEvent = self.wheelEvent
        self.show()

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

        self.move(*(x + 1 for x in self.getBoundBox()[:2]))

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

        self.startCrop(margin=2)

    def startCrop(self, margin=0, useOriginal=False):
        if self.cropping:
            return
        self.cropping = True

        self.cropMargin = margin
        self.usingOriginal = useOriginal

        if useOriginal:
            self.view.setSceneRect(
                self.displayPix.sceneBoundingRect().marginsAdded(
                    QMarginsF(margin, margin, margin, margin)
                )
            )

        else:
            self.originalOffset = self.view.sceneRect().topLeft()
            self.displayPix.setPixmap(
                QPixmap.fromImage(
                    self.displayImage.copy(self.view.sceneRect().toRect())
                )
            )
            self.view.setSceneRect(
                self.view.sceneRect().marginsAdded(
                    QMarginsF(margin, margin, margin, margin)
                )
            )
        self.move(
            self.view.mapToGlobal(
                self.view.mapFromScene(self.displayPix.sceneBoundingRect().topLeft())
            )
            - QPoint(margin, margin)
            + (QPoint(1, 1)
            if self.fullscreenCrop
            else QPoint(2, 2))
        )

        self.resize(self.view.sceneRect().size().toSize())
        self.displayPix.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )

    def replaceOriginal(self):

        self.displayImage = self.displayImage.copy(self.view.sceneRect().toRect())

        self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))
        self.displayPix.setPos(QPoint())
        self.view.setSceneRect(self.displayPix.boundingRect())
        self.move(self.pos() + QPoint(1, 1))

    def stopCrop(self, canceling=False):

        if not canceling:
            rect = self.view.mapToScene(self.selectionBox.geometry()).boundingRect()
        else:
            rect = self.view.sceneRect()

        limit = self.displayPix.sceneBoundingRect()

        print(limit, rect)
        rect = limit.intersected(rect)
        print("limited", rect)
        self.move(
            self.view.mapToGlobal(self.view.mapFromScene(rect.topLeft().toPoint()))
            + (QPoint(1, 1)
            if self.fullscreenCrop
            else QPoint(0, 0))
        )

        if not self.usingOriginal:
            rect.moveTopLeft(rect.topLeft() + self.originalOffset)
            self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))

        self.view.setSceneRect(rect)

        self.resize(rect.size().toSize())

        if self.fullscreenCrop:
            self.replaceOriginal()
            self.fullscreenCrop = False
            self.maskingright.hide()
            self.maskingleft.hide()
            self.maskingtop.hide()
            self.maskingbot.hide()

        self.selectionBox.hide()
        self.cropping = False

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        a0.accept()

    def mouseReleaseEvent(self, a0: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.cropping:
            self.stopCrop()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.inipos = a0.pos()
        self.lastpos = a0.globalPos()

        if self.cropping:
            self.selectionBox.show()
            self.selectionBox.raise_()
            self.selectionBox.move(a0.pos())

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.cropping:

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

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:

        if a0.key() == Qt.Key.Key_Escape:
            if self.fullscreenCrop or not self.cropping:
                self.close()
            elif self.cropping:
                self.stopCrop(canceling=True)

        if a0.key() == Qt.Key.Key_Space:
            self.startCrop(50, True)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:

        if not self.cropping:
            size = self.view.sceneRect().size().toSize()
            size.scale(a0.size(), Qt.AspectRatioMode.KeepAspectRatio)

            self.displayPix.setScale(
                size.width() / self.view.sceneRect().size().width()
            )
            self.displayPix.setPos(self.view.mapToScene(QPoint(0, 0)))
            self.resize(size)
        self.grip.move(self.rect().bottomRight() - QPoint(16, 16))

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
        if self.fullscreenCrop or self.cropping:
            self.grip.hide()
        else:
            self.grip.show()

    def leaveEvent(self, a0) -> None:
        self.grip.hide()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    ex = Snapshot(None, None)
    sys.exit(app.exec_())
