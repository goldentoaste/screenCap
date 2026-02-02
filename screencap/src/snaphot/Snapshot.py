
from ast import Lambda
from math import e
import sys
from traceback import print_tb
from PySide6.QtCore import (
    QEvent,
    QKeyCombination,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QImage, QMouseEvent, QPen, QPixmap
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
from screencap.src.snaphot.utils import getCurrentScreen


DEBUG = False

class Snapshot(QWidget):
    __init = False

    @classmethod
    def clsInit(cls):
        keyMgr = LocalKeyManager.getManager()
        keyMgr.registerShortCut(
            "Snapshot", "close", QKeyCombination(Qt.Key.Key_Escape), cls.close
        )


    def __init__(self):
        super().__init__(None)
        if not Snapshot.__init:
            Snapshot.clsInit()

        self.ctx = GlobalContext.getCtx()
        self.config = self.ctx.getConfig()

        LocalKeyManager.getManager().registerContext("Snapshot", self)

        self.cropping = False
        self.originPos = QPoint()
        self.mini = False

        self.loaded = False

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet(f"border: 0px solid;")
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

        self.cropping = False
        self.cropOffset = QPoint()

        self.initialize()

    def initialize(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.setMaximumSize(QApplication.primaryScreen().size())

        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setMouseTracking(True)

    def loadImage(self, img: QPixmap):
        self.pixmap = img
        self.pixmapItem.setPixmap(self.pixmap)
        self.view.setSceneRect(self.pixmap.rect())
        self.view.setFixedSize(self.pixmap.rect().size() / self.devicePixelRatio())
        self.setFixedSize(self.view.size() )

        self.scene.addRect(
            self.pixmapItem.boundingRect(),
            QPen(Qt.GlobalColor.blue, 1),
        )

        self.selectionBox.clampRect = self.rect()

    def fromFullscreen(self):
        curScreen = getCurrentScreen()
        self.loadImage(curScreen.grabWindow(0))
        self.move(curScreen.geometry().topLeft())
        self.startCrop()

        self.showNormal()


    def startCrop(self, margin = 0):
        self.cropOffset = 0
        self.cropping = True
        self.setCursor(Qt.CursorShape.CrossCursor)

    def finishCrop(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.cropping = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.originPos = event.position().toPoint()
        if self.cropping:
            self.selectionBox.setUseMinSize(False)
            self.selectionBox.move(event.position().toPoint())
            self.selectionBox.show()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        print(event.buttons() & Qt.MouseButton.LeftButton)
        if self.cropping and event.buttons() & Qt.MouseButton.LeftButton:
            self.selectionBox.setGeometry(QRect(self.originPos, event.position().toPoint()))
            self.selectionBox.clamp()

            print(QRect(self.originPos, event.position().toPoint()))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # TODO, alternative finish methods
        print("release")
        if self.cropping:
            self.selectionBox.setUseMinSize(True)
            self.finishCrop()


    def closeEvent(self, event: QCloseEvent) -> None:
        if DEBUG:
            sys.exit(0)



if __name__ == "__main__":
    DEBUG = True
    app = QApplication()
    snap = Snapshot()
    snap.fromFullscreen()

    sys.exit(app.exec())
