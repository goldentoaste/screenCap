


import sys
from PySide6.QtCore import QKeyCombination, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QImage, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QHBoxLayout, QWidget

from screencap.src.GlobalContext import GlobalContext
from screencap.src.Hotkeys.LocalKeyManager import LocalKeyManager
from screencap.src.Selection import SelectionBox
from screencap.src.snaphot.utils import getCurrentScreen



class Snapshot(QWidget):
    __init = False

    @classmethod
    def clsInit(cls):
        keyMgr = LocalKeyManager.getManager()
        keyMgr.registerShortCut("Snapshot", "close", QKeyCombination(Qt.Key.Key_Escape), cls.close)


    def __init__(self):
        super().__init__(None)
        if not Snapshot.__init:
            Snapshot.clsInit()

        self.ctx = GlobalContext.getCtx()
        self.config = self.ctx.getConfig()

        LocalKeyManager.getManager().registerContext("Snapshot", self)

        self.cropping = False
        self.originPos = QPoint()
        self.cropOffset = QPoint()
        self.mini = False

        self.loaded = False

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.pixmap = QPixmap()
        self.pixmapItem = self.scene.addPixmap(QPixmap())
        self.pixmapItem.setZValue(-100)
        self.pixmapItem.setPos(0,0)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.view)
        self.layout().setContentsMargins(0,0,0,0)

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

        self.initialize()


    def initialize(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(20, 20))
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.setMaximumSize(
            QApplication.primaryScreen().size()
        )

        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def loadImage(self, img: QPixmap):
        self.pixmap = img
        self.pixmapItem.setPixmap(self.pixmap)
        self.view.setSceneRect(self.pixmap.rect())
        self.view.setFixedSize(self.pixmap.rect().size())
        self.setFixedSize(self.view.size())
        self.scene.setBackgroundBrush(QColor('#fb493433'))
        self.view.setStyleSheet("border: 1px solid red")

        self.scene.addRect(self.pixmapItem.boundingRect(), QPen(Qt.GlobalColor.blue, 2),)


        print(self.pixmap.rect(), self.pixmapItem.boundingRect(), self.view.size(), self.view.sceneRect())



    def fromFullscreen(self):
        curScreen = getCurrentScreen()
        self.loadImage( curScreen.grabWindow(0))
        self.move(curScreen.geometry().topLeft())
        self.startCrop()

        self.showNormal()

    def startCrop(self):
        return



if __name__ == "__main__":

    app = QApplication()
    snap = Snapshot()
    snap.fromFullscreen()

    sys.exit(app.exec())