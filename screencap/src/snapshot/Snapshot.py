import sys
from PySide6.QtCore import (
    QKeyCombination,
    QPoint,
    QRect,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QCloseEvent,
    QColor,
    QKeyEvent,
    QMouseEvent,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QStyle,
    QWidget,
)

from screencap.src.GlobalContext import GlobalContext
from screencap.src.Hotkeys.LocalKeyManager import LocalKeyManager
from screencap.src.Selection import SelectionBox
from screencap.src.snapshot.utils import getCurrentScreen


DEBUG = False
MARGIN = 30


class Snapshot(QWidget):
    __init = False

    @classmethod
    def clsInit(cls):
        keyMgr = LocalKeyManager.getManager()
        keyMgr.registerShortCut(
            "Snapshot", "close", QKeyCombination(Qt.Key.Key_Escape), cls.close
        )
        keyMgr.registerShortCut(
            "Snapshot",
            "crop",
            QKeyCombination(Qt.Key.Key_Space),
            lambda obj: cls.startCrop(obj, 30),
        )

    def __init__(self):
        super().__init__(None)
        if not Snapshot.__init:
            Snapshot.clsInit()

        self.ctx = GlobalContext.getCtx()
        self.config = self.ctx.getConfig()

        LocalKeyManager.getManager().registerContext("Snapshot", self)

        self.initialCrop = False
        self.cropping = False
        self.originPos = QPoint()
        self.mini = False

        self.loaded = False

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pixmap = QPixmap()
        self.pixmapItem = self.scene.addPixmap(QPixmap())
        self.pixmapItem.setZValue(-100)
        self.pixmapItem.setPos(0, 0)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.view)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.selectionBox = SelectionBox(self)

        c = QColor(self.config.bgTrans)
        r = QRect()
        p = QPen(Qt.PenStyle.NoPen)

        self.maskTop = self.scene.addRect(r, p, c)
        self.maskLeft = self.scene.addRect(r, p, c)
        self.maskRight = self.scene.addRect(r, p, c)
        self.maskBot = self.scene.addRect(r, p, c)

        self.maskTop.setZValue(-10)
        self.maskLeft.setZValue(-10)
        self.maskRight.setZValue(-10)
        self.maskBot.setZValue(-10)

        self.border = self.scene.addRect(r, QPen(QColor(self.config.border), 1))

        self.cropping = False
        self.cropOffset = 0

        self.initialize()

    def initialize(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )  # | Qt.WindowType.SubWindow

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.setMaximumSize(QApplication.primaryScreen().size())

        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.view.setBackgroundBrush(QBrush(self.config.borderTrans))
        self.view.setStyleSheet(f"border: 0px solid; background:transparent;")

        self.view.setInteractive(False)

        self.pixmapItem.setPos(QPoint(0, 0))

        self.setMouseTracking(True)

    def loadImage(self, img: QPixmap, newPos: QPoint | None = None):
        self.setWindowOpacity(0)
        self.pixmap = img
        self.pixmapItem.setPixmap(self.pixmap)

        self.view.setSceneRect(self.pixmap.rect())
        self.view.setFixedSize(self.pixmap.rect().size() / self.devicePixelRatio())

        self.setGeometry(QRect((self.pos() if not newPos else newPos), self.view.size()))
        self.setBorder(self.pixmapItem.boundingRect())
        self.selectionBox.clampRect = self.rect()
        QApplication.instance().processEvents()  # pyright: ignore[reportOptionalMemberAccess]
        self.setWindowOpacity(1)

    def fromFullscreen(self):
        self.initialCrop = True
        curScreen = getCurrentScreen()
        img = curScreen.grabWindow()
        self.loadImage(img)
        self.move(curScreen.geometry().topLeft())
        self.startCrop()
        self.showNormal()

    def setBorder(self, rect: QRectF):
        self.border.setRect(rect.adjusted(0.25, 0.25, -0.25, -0.25))

    def startCrop(self, margin=0):
        self.cropping = True
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.cropOffset = margin

        if not self.initialCrop and margin > 0:
            rect = self.geometry()
            self.setUpdatesEnabled(False)

            self.setGeometry(
                QRect(
                    rect.topLeft() - QPoint(margin, margin),
                    QSize(rect.width() + margin * 2, rect.height() + margin * 2),
                )
            )

            self.view.setFixedSize(self.size())
            self.view.setSceneRect(QRect(QPoint(), self.size()))
            self.pixmapItem.setPos(QPoint(margin, margin))

            self.setBorder(self.rect().toRectF())

            self.setUpdatesEnabled(True)

    def finishCrop(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.selectionBox.hide()

        rect = self.selectionBox.geometry()

        if self.cropOffset > 0:
            self.setStyleSheet("background-color:unset;")

        if rect.width() < 50 or rect.height() < 50:
            print("rect too small!")
            if self.initialCrop:
                self.close()
            return  # cancel crop

        self.cropping = False
        self.initialCrop = False

        rect.moveTopLeft(
            rect.topLeft() - QPoint(self.cropOffset, self.cropOffset)
        )  # compensate for margin, if any
        rect = QRect(
            rect.topLeft() * self.devicePixelRatio(),
            rect.bottomRight() * self.devicePixelRatio(),
        )

        self.cropOffset = 0

        self.pixmap.convertFromImage(self.pixmap.toImage().copy(rect))
        self.loadImage(self.pixmap, self.mapToGlobal(self.selectionBox.geometry().topLeft()))

        # force image to load before moving, to avoid flicker


    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.originPos = event.position().toPoint()
        if self.cropping:
            self.selectionBox.setUseMinSize(False)
            self.selectionBox.move(event.position().toPoint())
            self.selectionBox.show()
        else:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.cropping and event.buttons() & Qt.MouseButton.LeftButton:
            self.selectionBox.setRect(self.originPos, event.position().toPoint())
            self.selectionBox.clamp()
        else:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self.originPos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # TODO, alternative finish methods
        self.setCursor(Qt.CursorShape.ArrowCursor)
        if self.cropping:
            self.selectionBox.setUseMinSize(True)

            if self.config.quickSnap:
                self.finishCrop()

    def tryClose(self):
        if self.cropping and not self.initialCrop:
            self.finishCrop()

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        if DEBUG:
            sys.exit(0)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Up:
            self.move(self.pos() + QPoint(0, -1))
        if event.key() == Qt.Key.Key_Down:
            self.move(self.pos() + QPoint(0, 1))
        if event.key() == Qt.Key.Key_Right:
            self.move(self.pos() + QPoint(1, 0))
        if event.key() == Qt.Key.Key_Left:
            self.move(self.pos() + QPoint(-1, 0))


if __name__ == "__main__":
    DEBUG = True
    app = QApplication()
    snap = Snapshot()
    snap.fromFullscreen()

    sys.exit(app.exec())
