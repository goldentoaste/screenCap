from typing import Union
from ConfigManager import ConfigManager
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import (
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
from PySide6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QPainter,
    QPen,
    QPixmap,
    QScreen,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSizeGrip,
    QStyleOptionGraphicsItem,
    QWidget,
)
import io
import sys
from selectionbox import SelectionBox
import win32clipboard as clipboard

from paintToolbar import PaintToolbar
from canvas import Canvas, RectItem

import values
from rightclickMenu import MenuPage

LEFTTOP = 0
LEFTBOT = 1
BOTLEFT = 2
BOTRIGHT = 3
RIGHTBOT = 4
RIGHTTOP = 5
TOPRIGHT = 6
TOPLEFT = 9


def postionRects(
    r1: Union[QRectF, QRect],
    r2: Union[QRectF, QRect],
    maxRect: Union[QRectF, QRect],
    prefs: list[int] = None,
) -> Union[QRectF, QRect]:
    """
    return postion to put r2 relative to r1, while trying to not collide with maxRect, trying in order of preference.
    if none works, return first interior corner. This assumes r2 is (much) smaller than r1
    """

    def lefttop():
        r = QRect(r2)
        r.moveTopRight(r1.topLeft())
        return r

    def leftbot():
        r = QRect(r2)
        r.moveBottomRight(r1.bottomLeft())
        return r

    def botleft():
        r = QRect(r2)
        r.moveTopLeft(r1.bottomLeft())
        return r

    def botright():
        r = QRect(r2)
        r.moveTopRight(r1.bottomRight())
        return r

    def rightbot():
        r = QRect(r2)
        r.moveBottomLeft(r1.bottomRight())
        return r

    def righttop():
        r = QRect(r2)
        r.moveTopLeft(r1.topRight())
        return r

    def topright():
        r = QRect(r2)
        r.moveBottomLeft(r1.topRight())
        return r

    def topleft():
        r = QRect(r2)
        r.moveBottomLeft(r1.topLeft())
        return r

    def innertopleft():
        r = QRect(r2)
        r.moveTopLeft(r1.topLeft())
        return r

    def innerbotleft():
        r = QRect(r2)
        r.moveBottomLeft(r1.bottomLeft())
        return r

    def innertopright():
        r = QRect(r2)
        r.moveTopRight(r1.topRight())
        return r

    def innerbotright():
        r = QRect(r2)
        r.moveBottomRight(r1.bottomRight())
        return r

    def conflict(rect: Union[QRectF, QRect]):
        return maxRect.intersects(rect) and not maxRect.contains(rect)

    if not prefs:
        prefs = [LEFTTOP]

    choices = {
        LEFTTOP: lefttop,
        LEFTBOT: leftbot,
        BOTLEFT: botleft,
        BOTRIGHT: botright,
        RIGHTBOT: rightbot,
        RIGHTTOP: righttop,
        TOPRIGHT: topright,
        TOPLEFT: topleft,
    }

    output = None
    for pref in prefs:
        rect = choices[pref]()
        if not conflict(rect):
            output = rect
            break
    else:
        # no good result found
        choices = {
            LEFTTOP: innertopleft,
            LEFTBOT: innerbotleft,
            BOTLEFT: innerbotleft,
            BOTRIGHT: innerbotright,
            RIGHTBOT: innerbotright,
            RIGHTTOP: innertopright,
            TOPRIGHT: innertopright,
            TOPLEFT: innertopleft,
        }
        output = choices[prefs[0]]()
    return output


class Snapshot(QWidget):
    def __init__(
        self,
        master=None,
        image=None,
        debugConfigPath=None,
        config=None,
        contextMenu: MenuPage = None,
        paintTool: PaintToolbar = None,
        *args,
        **kwargs,
    ):

        from main import Main

        super().__init__(*args, **kwargs)

        #    self.needrecycle = needrecycle #if the snapshot is spawned from recycler, then no need to recycle again.
        self.config = ConfigManager(debugConfigPath) if debugConfigPath else config
        #: TODO each snapshould not create their own config! should be given by main, so that every entity shares the same config.

        self.master: Main = master

        self.contextMenu = contextMenu
        self.paintTool = paintTool

        self.cropping = False
        self.lastpos = None
        self.moveLock = False
        self.cropOffset = QPoint()
        self.mini = False

        if image:
            self.fromImage(image)
        else:
            self.fromFullscreen()

    def initHotkeys(
        self,
    ):

        hotkeys = {
            "licopy": (self.copy),
        }

    def initialize(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # self.maxHeight = QApplication.primaryScreen().size().height()
        # self.maxWidth = QApplication.primaryScreen().size().width()

        self.setMaximumHeight(QApplication.primaryScreen().size().height())
        self.setMaximumWidth(QApplication.primaryScreen().size().width())

        self.scene = QGraphicsScene()

        self.displayPix = self.scene.addPixmap(self.displayImage)

        self.displayPix.setZValue(-100)
        self.displayPix.setPos(0, 0)

        self.borderRect = RectItem(False, True, QRectF())
        self.borderRect.setPen(QPen(QColor(200, 200, 200), 2))
        self.borderRect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.borderRect.finalize()
        self.scene.addItem(self.borderRect)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, True)

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
        self.view.setStyleSheet("background-color: rgba(40, 40, 40, 0.4); border: 0px")

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.resize(self.displayPix.boundingRect().size().toSize())

        self.resize(self.view.size())

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
            self.displayPix.setTransformationMode(
                Qt.TransformationMode.FastTransformation
            )
            self.canvas.canvas.setTransformationMode(
                Qt.TransformationMode.FastTransformation
            )
            self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        def release(a):
            QSizeGrip.mouseReleaseEvent(self.grip, a)
            self.moveLock = False
            self.displayPix.setTransformationMode(
                Qt.TransformationMode.SmoothTransformation
            )
            self.canvas.canvas.setTransformationMode(
                Qt.TransformationMode.SmoothTransformation
            )
            self.view.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.grip.mousePressEvent = press
        self.grip.mouseReleaseEvent = release

        self.currentRect = (0, 0, 0, 0)
        self.currentWidth = self.displayImage.width()
        self.canvas = Canvas(
            self.scene, self.view, self.paintTool, self.displayPix.pixmap().size()
        )

        self.painting = False

        self.view.setSceneRect(self.displayPix.boundingRect())

        # cropping masks
        c = QColor(0, 0, 0, 100)
        r = QRectF()
        p = QPen(Qt.PenStyle.NoPen)
        # p = QPen(QColor(0, 0, 0, 0), 0)

        self.maskingtop: QGraphicsRectItem = self.scene.addRect(
            self.view.sceneRect(), p, c
        )
        self.maskingleft: QGraphicsRectItem = self.scene.addRect(r, p, c)
        self.maskingright: QGraphicsRectItem = self.scene.addRect(r, p, c)
        self.maskingbot: QGraphicsRectItem = self.scene.addRect(r, p, c)

        self.maskingtop.setZValue(-10)
        self.maskingleft.setZValue(-10)
        self.maskingright.setZValue(-10)
        self.maskingbot.setZValue(-10)

        # label for current crop size

        self.sizeLabel = QLabel(self)
        self.sizeLabel.hide()
        self.sizeLabel.setText("1000 x 1000")
        self.sizeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet(
            """
            QLabel{
                border-radius: 5px;
                background: #646496;
                color: #fffef2;
                font-size: 14px;
                padding: 5px;
                }
            """
        )
        # self.sizeLabel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Ignored)
        self.sizeLabel.adjustSize()
        from snapshotMenu import SnapshotMenu

        self.cropTools = SnapshotMenu(self)
        self.cropTools.setFixedSize(self.cropTools.sizeHint())
        self.cropTools.hide()

        self.selectionBox = SelectionBox(QtWidgets.QRubberBand.Shape.Rectangle, self, self.updateMask)
        self.selectionBox.hide()

        print(self.selectionBox, self.cropTools, self.sizeLabel)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        if self.painting or self.cropping:
            print("skipped context")
            return  # ignore context menu / right click while painting
        self.contextMenu.buildMenu(target=self).popup(a0.globalPos())

    def clearCanvas(self):
        self.canvas.clear()

    def togglePaint(self):
        print(self.painting)
        if self.painting:
            self.stopPaint()
        else:
            self.startPaint()

    def startPaint(self):
        print("in srtart paint")
        self.painting = True
        self.master.snapshotPaintEvent(self)
        self.canvas.updateCursor()
        self.grip.hide()

    def stopPaint(self):
        self.painting = False
        self.master.snapshotStopPaintEvent(self)
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.grip.show()

    def fromImage(self, image: QPixmap):

        self.displayImage: QPixmap = image
        self.fullscreenCrop = False
        self.move(QCursor.pos())
        self.initialize()
        self.displayPix.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self.showNormal()

    def fromFullscreen(self):
        curScreen = self.getCurrentScreen()
        self.displayImage: QPixmap = curScreen.grabWindow(0)
        self.fullscreenCrop = True
        self.move(curScreen.geometry().topLeft())
        self.initialize()
        self.startCrop(margin=0, useOriginal=True)
        self.showNormal()

    def getNonScaledImage(self) -> QPixmap:
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
        im.save(buffer, "BMP")
        with io.BytesIO(buffer.data()) as b:
            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardData(clipboard.CF_DIB, b.getvalue()[14:])
            clipboard.CloseClipboard()

    def cut(self):
        self.copy()
        self.close()

    formatTable = {"P": "PNG", "J": "JPG", "B": "BMP"}

    def getSaveName(self):

        output = QFileDialog.getSaveFileName(
            self,
            "Choose save location",
            self.config.ssavelocation,
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;Bitmap (*.bmp)",
        )
        if output:  # file dialog reutrns none if user cancels
            print(output)
            filename, ext = output
            if filename and ext:
                ext = Snapshot.formatTable[ext[0].upper()]
                return (filename, ext)
            return None
        return None  # -> file selection canceled

    def getImage(self) -> QPixmap:
        region = QRect(
            (self.view.sceneRect().topLeft() / self.displayPix.scale()).toPoint(),
            (self.view.sceneRect().size() / self.displayPix.scale()).toSize(),
        )
        # the region of the original image which the current scene rect is covering.
        return self.displayImage.copy(region)

    def getCanvasImage(self) -> QPixmap:
        """
        yoink
        https://stackoverflow.com/a/50358905/12471420

        drawing canvas onto given image
        """
        # return self.canvas.canvas.pixmap()
        rect = self.displayPix.boundingRect()
        if len(self.canvas.group.childItems()) and (
            rect.isNull() or not rect.isValid()
        ):
            return None

        pixmap = QPixmap(self.displayPix.boundingRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)

        for item in self.canvas.group.childItems():
            item.paint(painter, QStyleOptionGraphicsItem())
        painter.end()

        return pixmap.toImage().copy(
            self.view.sceneRect().toRect()
        )  # danger!!! scale is current scale!! #also, only keeping the visible region

    def saveImage(self):
        filename, format = self.getSaveName()

        self.getImage().save(filename, format, 100)

    def saveImageScaled(self):
        filename, format = self.getSaveName()
        img = self.getImage()
        img.scaled(
            img.width() * self.displayPix.scale(),
            img.height() * self.displayPix.scale(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ).save(filename, format, self.config.iquality)

    def saveImageWithCanvas(self, scaled: bool = False):
        filename, format = self.getSaveName()

        image = self.getImage()
        canvasImg = self.getCanvasImage()

        if (
            canvasImg
        ):  # if canvasimg is null, then no need to scale and layer the image on top.

            if scaled:

                image = image.scaled(
                    image.width() * self.displayPix.scale(),
                    image.height() * self.displayPix.scale(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                scale = self.displayPix.scale()
                canvasImg = canvasImg.scaled(
                    canvasImg.width() * scale,
                    canvasImg.height() * scale,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                canvasImg.save(filename, format, self.config.iquality)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
            painter.drawImage(image.rect(), canvasImg)
            painter.end()
        image.save(filename, format, self.config.iquality)

    def saveImageWithCanvasScaled(self):
        self.saveImageWithCanvas(True)

    def startCrop(self, margin=50, useOriginal=False):
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
        else:
            self.originalOffset = self.view.sceneRect().topLeft()
            self.displayPix.setPixmap(
                self.displayImage.copy(QRectF(*self.currentRect).toRect())
            )
            self.move(self.pos() - QPoint(margin, margin))

        self.view.setSceneRect(
            self.displayPix.sceneBoundingRect().marginsAdded(
                QMarginsF(margin, margin, margin, margin)
            )
        )
        self.resize(self.view.sceneRect().size().toSize())
        self.displayPix.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )

    def replaceOriginal(self):

        self.displayImage = self.displayImage.copy(self.view.sceneRect().toRect())

        self.displayPix.setPixmap(self.displayImage)
        self.displayPix.setPos(QPoint())
        self.view.setSceneRect(self.displayPix.boundingRect())

        self.cropOffset = QPointF()
        self.currentRect = (0, 0, self.width(), self.height())
        self.currentWidth = self.displayImage.width()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:

        # if a0.size().width() > self.maxWidth or a0.size().height() > self.maxHeight:
        #     a0.accept()
        #     return
        # print(a0.size())
        if not self.cropping and not self.mini:
            fullwidth = self.displayImage.width() * self.displayPix.scale()

            size = QSizeF(*self.currentRect[2:])
            size.scale(QSizeF(a0.size()), Qt.AspectRatioMode.KeepAspectRatio)
            scale = (
                fullwidth
                + ((size.width() - self.currentWidth) / self.currentWidth) * fullwidth
            ) / self.displayImage.width()

            self.displayPix.setScale(scale)
            self.canvas.setScale(scale)  # scales both canvas items and image

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
            self.displayPix.setPixmap(self.displayImage)

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
        self.sizeLabel.hide()
        self.cropTools.hide()
        self.grip.show()

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        a0.accept()

    def mouseReleaseEvent(self, a0: QtWidgets.QGraphicsSceneMouseEvent) -> None:

        if self.painting:
            self.canvas.onRelease(a0)

        if self.cropping and self.config.bfastcrop:
            self.stopCrop()

        self.cropTools.raise_()  # incase the button group has to cover selection box.

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.cropping or self.painting:
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
        print("clikc event")
        if self.painting:
            self.canvas.onClick(a0)
            return

        self.inipos = a0.pos()
        self.lastpos = a0.globalPos()

        if self.cropping and a0.buttons() == Qt.MouseButton.LeftButton:
            self.selectionBox.show()
            self.selectionBox.move(a0.pos())

            self.sizeLabel.show()
            rect = postionRects(
                self.selectionBox.rect().translated(self.selectionBox.pos()),
                self.sizeLabel.rect(),
                self.rect(),
                [TOPLEFT, LEFTTOP],
            )
            self.sizeLabel.move(rect.topLeft())
            self.sizeLabel.setText(
                f"{self.selectionBox.width()} x {self.selectionBox.height()}"
            )

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:

        if self.painting:
            self.canvas.onMove(a0)
            if a0.buttons() == 0 or a0.buttons() == Qt.MouseButton.LeftButton:
                return

        if (
            a0.buttons() == Qt.MouseButton.LeftButton
            or a0.buttons() == Qt.MouseButton.MiddleButton
        ):
            if self.cropping:
                rect = QRect(self.inipos, a0.pos()).normalized()
                self.selectionBox.setGeometry(rect)
            elif not self.moveLock:
                delta = a0.globalPos() - self.lastpos
                self.move(self.pos() + delta)
                self.lastpos = a0.globalPos()

    def updateMask(self, rect: QRect):
        vrect = self.view.sceneRect()
        self.maskingtop.setRect(
            QRectF(QPointF(0, 0), QSizeF(vrect.width(), rect.top()))
        )
        self.maskingleft.setRect(
            QRectF(QPointF(0, rect.top()), QSizeF(rect.left(), rect.height()))
        )
        self.maskingbot.setRect(
            QRectF(
                QPointF(0, rect.bottom() + 1),  # idk why plus 1 :x
                QSizeF(vrect.width(), vrect.height() - rect.bottom()),
            )
        )
        self.maskingright.setRect(
            QRectF(
                QPointF(rect.right(), rect.top()),
                QSizeF(vrect.width() - rect.right(), rect.height()),
            )
        )
        rect = rect.intersected(
            self.view.mapFromScene(self.displayPix.boundingRect()).boundingRect()
        )
        selectionrect = self.selectionBox.rect().translated(self.selectionBox.pos())
        self.sizeLabel.setText(f"{rect.width()} x {rect.height()}")
        self.sizeLabel.move(
            postionRects(
                selectionrect, self.sizeLabel.rect(), self.rect(), [TOPLEFT, LEFTTOP]
            ).topLeft()
        )

        if not self.config.bfastcrop:
            self.cropTools.move(
                postionRects(
                    selectionrect, self.cropTools.rect(), self.rect(), prefs=[BOTRIGHT]
                ).topLeft()
            )
            self.cropTools.show()

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if self.painting:
            self.canvas.keyUp(a0)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:

        if a0.key() == Qt.Key.Key_S:
            if self.cropping and not self.config.bfastcrop:
                self.stopCrop()

        if a0.key() == Qt.Key.Key_P:
            self.startPaint()

        if self.painting:
            self.canvas.keyDown(a0)
            return

        if a0.key() == Qt.Key.Key_Escape:
            if self.fullscreenCrop or not self.cropping:
                self.close()
            elif self.cropping:
                self.stopCrop(canceling=True)

        if a0.key() == Qt.Key.Key_Space:
            self.startCrop(20, True)
            # self.copy()

    def getCurrentScreen(self) -> QScreen:
        """
        Get the screen which is the cursor is currently in.
        """
        screens = [screen for screen in QApplication.screens()]
        pos = QCursor.pos()
        for screen in screens:
            if screen.geometry().contains(pos, False):
                return screen
        return screens[0]

    def enterEvent(self, a0) -> None:
        if self.painting:
            self.canvas.onEnter(a0)
            return

        if self.fullscreenCrop or self.cropping or self.mini:
            self.grip.hide()
        else:
            self.grip.show()

    def leaveEvent(self, a0) -> None:
        if self.painting:
            self.canvas.onExit(a0)
            return
        self.grip.hide()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        self.master.snapshotCloseEvent(self)  # notify controller


if __name__ == "__main__":

    app = QApplication(sys.argv)
    from paintToolbar import PaintToolbar
    from rightclickMenu import MenuPage

    config = ConfigManager(values.defaultConfigPath, values.defaultVariables)

    painttool = PaintToolbar(config, None)
    contextMenu = MenuPage(config)
    contextMenu.hide()

    ex = Snapshot(None, None, None, config, contextMenu, painttool)
    sys.exit(app.exec_())
