from re import S
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QMargins, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, Qt
from PyQt5.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap, QTransform
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsEffect,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QSizeGrip,
    QWidget,
)
import desktopmagic.screengrab_win32
from PIL import Image
from PIL.ImageQt import ImageQt
import sys
import time

"""
-cropping - done owo
-resizing(by dragging corners)
-painting, paint settings controller
-saving
-adapting crop, resize, save wit paint
-right click menu manager
-color picker?


"""


class Grip(QSizeGrip):
    def __init__(self, parent: QWidget, keepRatio=True) -> None:
        super().__init__(parent)
        self.keepRatio = keepRatio
        self.lastPos = None

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.lastPos is None:
            self.lastPos = a0.globalPos()

        if not self.keepRatio:

            return super().mouseMoveEvent(a0)

        dx = a0.globalX() - self.lastPos.x()
        dy = a0.globalY() - self.lastPos.y()

        s = self.parent().size()
        ratio = s.width() / s.height()
        if abs(dx) > abs(dy):

            self.parent().resize(s.width() + dx, int((s.width() + dx) / ratio))

        else:
            self.parent().resize(int((s.height() + dy) * ratio), s.height() + dy)

        self.lastPos = a0.globalPos()


class Snapshot(QWidget):
    def __init__(self, master, image=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master = master
        self.image = None
        self.lastpos = None
        self.windowpos = None
        self.isCropping = False
        self.moveLock = False

        if self.image:
            self.fromImage()
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

        # self.point = self.scene.addEllipse(QRectF(0,0 , 10, 10), QColor(255, 255, 255), QColor(255, 255, 255))
        # self.point.setZValue(100)

        self.view = QGraphicsView(self.scene)

        self.view.setStyleSheet("background-color: rgba(40, 40, 40, 0.5)")
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
        self.layout.setSpacing(0)

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

        self.show()

    def enterEvent(self, a0) -> None:
        if self.firstCrop or self.isCropping:
            self.grip.hide()
        else:
            self.grip.show()

    def leaveEvent(self, a0) -> None:
        self.grip.hide()

    # def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
    #     self.displayPix.setScale(self.displayPix.scale() + 0.1)
    #     return super().wheelEvent(a0)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if not self.isCropping:
            size = self.view.sceneRect().size().toSize()
            size.scale(a0.size(), Qt.AspectRatioMode.KeepAspectRatio)

            self.displayPix.setScale(
                size.width() / self.view.sceneRect().size().width()
            )
            self.displayPix.setPos(self.view.mapToScene(QPoint(0, 0)))
            self.resize(size)

        self.grip.move(self.size().width() - 16, self.size().height() - 16)

    def fromImage(self, pilImage: Image.Image):
        pilImage.putalpha(255)
        self.originalImage = pilImage
        self.displayImage: QImage = ImageQt(pilImage)
        self.firstCrop = False
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
        # image = Image.open("testing.jpeg")
        # image.putalpha(255)
        # self.displayImage = ImageQt(image)
        self.firstCrop = True
        p = self.getBoundBox()[:2]
        self.move(p[0] - 1, p[1] - 1)

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
        self.crop(margin=0)

    def crop(self, margin=50, useOriginal=False):
        if self.isCropping:
            return
        self.isCropping = True
        self.viewRect = self.view.sceneRect()
        self.cropMargin = margin
        self.usingOriginal = useOriginal
        self.move(
            self.pos()
            - QPoint(margin, margin)
            - self.view.mapFromScene(self.displayPix.sceneBoundingRect().topLeft())
        )

        if useOriginal:

            self.view.setSceneRect(
                self.expandRect(self.displayPix.sceneBoundingRect(), margin)
            )
        else:
            # use temp pixmap while useOriginal is not used.
            self.displayPix.setPixmap(
                QPixmap.fromImage(
                    self.displayImage.copy(self.view.sceneRect().toRect())
                )
            )
            r = self.view.sceneRect()
            # r.moveTopLeft(QPoint(0, 0))
            self.view.setSceneRect(self.expandRect(r, margin))

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
        self.displayPix.setPos(QPoint())
        print(self.displayPix.pos())
        # move view to 0,0), where the image is
        self.view.setSceneRect(QRectF(self.displayPix.pixmap().rect()))

    def stopCrop(self, canceling=False):

        print('start', self.displayPix.scale())
        if not canceling:
            selectedRect = self.view.mapToScene(
                self.getCorrectCoord(
                    self.iniPos.x(),
                    self.iniPos.y(),
                    self.selectRect.width() + self.iniPos.x(),
                    self.selectRect.height() + self.iniPos.y(),
                ).toRect()
            ).boundingRect()
         
        else:
            selectedRect = self.view.sceneRect()

        if selectedRect.width() < 20 or selectedRect.height() < 20:
            return
        
        limit = self.view.sceneRect()
        limit.moveTopLeft(
            QPoint(self.cropMargin, self.cropMargin)
        )  # move the limt rect of counter margin

        
        print('before', selectedRect, limit)
        selectedRect = self.limitRect(selectedRect, limit)
        
        print('after', selectedRect)
        # save the limited rect for transformation, before the sceneRect offset
        limitedSelectionRect = QRectF(selectedRect)

        # selectedRect.moveTopLeft(
        #     selectedRect.topLeft() + self.view.sceneRect().topLeft()
        # )  # move the selection rect to show the region actually select, in case the top left corner is not the corner of the image

        
        self.selectRectItem.hide()

        # uses the original selection rect for movement, since the an alternative processed rect is used for grabbing image instead.
    
        self.move(
            self.view.mapToGlobal(limitedSelectionRect.topLeft().toPoint()) - QPoint(3, 3)
        )

        if not self.usingOriginal:
            self.displayPix.setPixmap(QPixmap.fromImage(self.displayImage))

        self.view.setSceneRect(selectedRect)

        self.resize(selectedRect.size().toSize())

        if self.firstCrop:
            self.resize(selectedRect.size().toSize())
            self.replaceOriginalImage()
            self.firstCrop = False
            self.maskingright.hide()
            self.maskingleft.hide()
            self.maskingtop.hide()
            self.maskingbot.hide()
            self.displayPix.setTransformationMode(
                Qt.TransformationMode.SmoothTransformation
            )

        self.isCropping = False

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

        # todo remove later
        if a0.buttons() == Qt.MouseButton.RightButton:
            delta = a0.globalPos() - self.lastpos
            delta = delta.toPoint() if type(delta) is QPointF else delta
            self.move(self.pos() + delta)

            self.lastpos = a0.globalPos()
            return

        if self.isCropping:
            diff: QPointF = a0.pos() - self.iniPos
            self.selectRect.setSize(QSizeF(diff.x(), diff.y()))
            rect = self.getCorrectCoord(
                self.iniPos.x(),
                self.iniPos.y(),
                a0.x(),
                a0.y(),
            )

            self.selectRectItem.setRect(self.selectRect)
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
            delta = delta.toPoint() if type(delta) is QPointF else delta
            self.move(self.pos() + delta)

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
            if self.firstCrop or not self.isCropping:
                self.close()
            elif self.isCropping:
                self.stopCrop(canceling=True)

        if a0.key() == Qt.Key.Key_Space:
            self.crop(50, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Snapshot(None, None)
    sys.exit(app.exec_())
