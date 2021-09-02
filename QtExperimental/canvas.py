
from paintToolbar import PaintToolbar
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



class Canvas:
    
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView, toolbar : PaintToolbar):
        pass
    
    def onClick(self, a0: QMouseEvent):
        pass
    
    def onRelease(self, a0: QMouseEvent):
        pass
    
    def onDrag(self, a0: QMouseEvent):
        pass
    
    def keyDown(self, a0: QKeyEvent):
        pass
    
    def keyUp(self, a0: QKeyEvent):
        pass
    








