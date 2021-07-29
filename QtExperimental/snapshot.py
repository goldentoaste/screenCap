from re import S
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QMargins, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtGui import QColor, QCursor, QImage, QPen, QPixmap, QTransform
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QWidget,
)
import desktopmagic.screengrab_win32
from PIL import Image
from PIL.ImageQt import ImageQt
import sys


"""
-cropping - done owo
-resizing(by dragging corners)
-painting, paint settings controller
-saving
-adapting crop, resize, save wit paint
-right click menu manager
-color picker?


"""


class Snapshot(QWidget):
    def __init__(self, master, image=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master = master
        self.image = None
        self.lastpos = None
        self.windowpos = None
        self.isCropping = False

        if self.image:
            self.fromImage()
        else:
            self.fromFullscreen()

    def initialize(self):

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(QSize(20, 20))
        self.scene = QGraphicsScene()

        self.displayPix = self.scene.addPixmap(QPixmap.fromImage(self.displayImage))
        self.displayPix.setZValue(0)
        self.displayPix.setPos(0, 0)

        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: rgba(40, 40, 40, 0.6)")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.resize(self.displayPix.boundingRect().size().toSize())
        self.resize(self.view.size())

        self.selectRect = QRectF()
        self.selectRectItem = self.scene.addRect(
            self.selectRect, QPen(QColor(200, 200, 200), 2)
        )

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(QMargins())

        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent
        self.show()

    def updateDisplay(self):
        pass

    def fromImage(self, pilImage: Image.Image):
        pilImage.putalpha(255)
        self.originalImage = pilImage
        self.displayImage: QImage = ImageQt(pilImage)
        self.firstCrop = False
        self.move(QCursor.pos())
        self.initialize()

    def fromFullscreen(self):
        image = desktopmagic.screengrab_win32.getRectAsImage(self.getBoundBox())
        image.putalpha(255)
        self.originalImage = ImageQt(image)
        self.displayImage = self.originalImage
        image = Image.open("testing.jpeg")
        image.putalpha(255)
        self.displayImage = ImageQt(image)
        self.firstCrop = True
        self.move(*self.getBoundBox()[:2])
        self.initialize()
        self.crop()

    def crop(self, margin=50, useOriginal = False):
        if self.isCropping:
            return
        self.isCropping = True
        self.viewRect = self.view.sceneRect()
        self.cropMargin = margin
        self.move(self.pos() - QPoint(margin, margin) - self.view.sceneRect().topLeft().toPoint())

        if useOriginal:
            self.view.setSceneRect(self.expandRect(self.displayImage.rect(), margin))
        else:
            #use temp pixmap while useOriginal is not used. TODO 
            self.view.setSceneRect(self.expandRect(self.view.sceneRect(), margin))
        self.resize(self.view.sceneRect().size().toSize())

    def expandRect(self, rect: QRectF, amount: float) -> QRectF:
        """
        expands a QRectF by 'amount' px in all directions
        """
        if amount <= 0:
            return QRectF(rect)
        rect = QRectF(rect)
        rect.moveTopLeft(rect.topLeft() - QPointF(amount, amount))
        rect.setWidth(rect.width() + amount * 2)
        rect.setHeight(rect.height() + amount * 2)
        return rect

    def qPointToTuple(self, p: QPointF):
        return (p.x(), p.y())

    def replaceOriginalImage(self):

        self.displayImage = self.displayImage.copy(self.view.sceneRect().toRect())
        # the pixmap stays at 0,0
        self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))

        # move view to 0,0), where the image is
        rect = self.view.sceneRect()
        self.view.setSceneRect(QRectF(0, 0, rect.width(), rect.height()))

    def stopCrop(self):

        selectedRect = self.getCorrectCoord(
            self.iniPos.x(),
            self.iniPos.y(),
            self.selectRect.width() + self.iniPos.x(),
            self.selectRect.height() + self.iniPos.y(),
        )
        if selectedRect.width() < 20 or selectedRect.height() < 20:
            return
        limit = self.displayPix.pixmap().rect()
        limit.moveTopLeft(
            QPoint(self.cropMargin, self.cropMargin)
        )  # move the limt rect of counter margin

        selectedRect = self.limitRect(selectedRect, limit)
        # save the limited rect for transformation, before the sceneRect offset
        limitedSelectionRect = QRectF(selectedRect)
    
        selectedRect.moveTopLeft(
            selectedRect.topLeft() + self.view.sceneRect().topLeft()
        )  # move the selection rect to show the region actually select, in case the top left corner is not the corner of the image

        self.selectRectItem.hide()

        self.isCropping = False

        # uses the original selection rect for movement, since the an alternative processed rect is used for grabbing image instead.

        self.move(self.mapToGlobal(limitedSelectionRect.topLeft().toPoint()))

        # change size after moving, since resizing could cause window pos to change?
        self.view.setSceneRect(selectedRect)
        self.resize(selectedRect.size().toSize())
        if self.firstCrop:
            self.replaceOriginalImage()
            self.firstCrop = False

    def mouseReleaseEvent(self, a0: QtWidgets.QGraphicsSceneMouseEvent) -> None:

        self.stopCrop()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.lastpos = a0.globalPos()
        self.iniPos = a0.pos()

        if self.isCropping or True:
            self.selectRectItem.show()
            self.selectRectItem.setZValue(1000)
            self.selectRectItem.setPos(self.view.mapToScene(a0.pos()))
            self.selectRect = QRectF()
            self.selectRectItem.setRect(self.selectRect)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.isCropping:
            diff: QPointF = a0.pos() - self.iniPos
            self.selectRect.setSize(QSizeF(diff.x(), diff.y()))
            self.selectRectItem.setRect(
                self.getCorrectCoord(
                    self.selectRect.x(),
                    self.selectRect.y(),
                    self.selectRect.bottomRight().x(),
                    self.selectRect.bottomRight().y(),
                )
            )
        else:
            delta = a0.globalPos() - self.lastpos
            delta = delta.toPoint() if type(delta) is QPointF else delta
            self.move(self.pos() + delta)
            print(self.pos(), self)
            self.lastpos = a0.globalPos()

    def limitRect(self, rect: QRectF, limit: QRectF):

        x1 = max(rect.topLeft().x(), limit.topLeft().x())
        y1 = max(rect.topLeft().y(), limit.topLeft().y())
        x2 = min(rect.bottomRight().x(), limit.bottomRight().x())
        y2 = min(rect.bottomRight().y(), limit.bottomRight().y())

        return QRectF(QPointF(x1, y1), QPointF(x2, y2))

    def getCorrectCoord(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        # true for pos
        table = {
            (True, True): (x1, y1, x2 - x1, y2 - y1),
            (True, False): (x1, y2, x2 - x1, y1 - y2),
            (False, True): (x2, y1, x1 - x2, y2 - y1),
            (False, False): (x2, y2, x1 - x2, y1 - y2),
        }
        return QRectF(*table[(dx > 0, dy > 0)])

    def getBoundBox(self):
        bounds = desktopmagic.screengrab_win32.getDisplayRects()
        pos = QCursor.pos()
        x = pos.x()
        y = pos.y()
        for bound in bounds:
            if x >= bound[0] and y >= bound[1] and x <= bound[2] and y <= bound[3]:
                return bound
        return bounds[0]

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:

        if a0.key() == Qt.Key.Key_Escape:
            self.close()

        if a0.key() == Qt.Key.Key_Space:
            self.crop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Snapshot(None, None)
    sys.exit(app.exec_())
