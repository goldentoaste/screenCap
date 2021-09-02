import sys
from typing import ClassVar, List
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


PATH = 0
LINE = 1
RECT = 2
CIRCLE = 3


class DrawOptions:
    
    pen: QPen
    brush: QBrush
    shape: int


class PaintToolbar(QWidget):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.initGui()

    def initVals(self):
        #todo, to be called after initGui()
        pass
    
    def getDrawOptions(self):
        return 

    
    
    def initGui(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        metric = QFontMetrics(QFont())
        mainlayout = QHBoxLayout()

        self.radiusField = NumEditTemp("* px", "*", 1, 20)
        self.radiusField.setFixedWidth(metric.horizontalAdvance("20 px  "))

        self.radiusIcon = RadiusIcon(1, Qt.GlobalColor.black, QSize(40, 40))
        self.radiusSlider = QSlider(Qt.Orientation.Horizontal)
        self.radiusSlider.setMinimum(1)
        self.radiusSlider.setMaximum(15)
        self.radiusSlider.setPageStep(1)
        self.radiusSlider.valueChanged.connect(
            lambda val: (
                self.radiusField.setText(f"{val} px"),
                self.radiusIcon.setRadius(val),
            )
        )
        self.radiusField.onFinish = lambda val : self.radiusSlider.setSliderPosition(val)

        self.alphaField = NumEditTemp("Alpha *%", "*", 0, 100)
        self.alphaField.setFixedWidth(metric.horizontalAdvance("Alpha 100%  "))

        self.alphaSlider = QSlider(Qt.Orientation.Horizontal)
        self.alphaSlider.setMinimum(0)
        self.alphaSlider.setMaximum(100)
        self.alphaSlider.setPageStep(5)
        self.alphaSlider.valueChanged.connect(
            lambda val: self.alphaField.setText(f"Alpha {val}%")
        )
        self.alphaField.onFinish = lambda val: self.alphaSlider.setSliderPosition(val)

        self.penButton = QPushButton(QIcon("icons/pen.svg"), "")
        self.penButton.setIconSize(QSize(35, 35))

        self.lineButton = QPushButton(QIcon("icons/line.svg"), "")
        self.lineButton.setIconSize(QSize(35, 35))

        self.rectButton = QPushButton(QIcon("icons/rect.svg"), "")
        self.rectButton.setIconSize(QSize(35, 35))

        self.elipseButton = QPushButton(QIcon("icons/circle.svg"), "")
        self.elipseButton.setIconSize(QSize(35, 35))
        self.fillCheck = QCheckBox("Fill")

        colorGroup = QGridLayout()
        colorGroup.setVerticalSpacing(0)
        colorGroup.setHorizontalSpacing(0)

        self.colorButtons = []
        for i in range(10):
            c = ColorButton(QSize(58, 58))
            c.setColor(QColor(i * 10, i * 20, i * 10))
            self.colorButtons.append(c)

            colorGroup.addWidget(c, i // 5, i % 5)

        upperGroup = QGridLayout()

        sizeGroup = QHBoxLayout()
        sizeGroup.addWidget(self.radiusField)
        sizeGroup.addWidget(self.radiusIcon)

        upperGroup.addLayout(sizeGroup, 0, 0)
        upperGroup.addWidget(self.radiusSlider, 0, 1)
        upperGroup.addWidget(self.alphaField, 1, 0)
        upperGroup.addWidget(self.alphaSlider, 1, 1)

        sliderGroup = QVBoxLayout()
        sliderGroup.addWidget(self.radiusSlider)
        sliderGroup.addWidget(self.alphaSlider)

        buttonGroup = QHBoxLayout()

        buttonGroup.addWidget(self.penButton)
        buttonGroup.addWidget(self.lineButton)
        buttonGroup.addWidget(self.rectButton)
        buttonGroup.addWidget(self.elipseButton)
        buttonGroup.addWidget(self.fillCheck)

        allleftGroup = QVBoxLayout()
        allleftGroup.addLayout(upperGroup)
        allleftGroup.addLayout(buttonGroup)

        mainlayout.addLayout(allleftGroup)
        mainlayout.addLayout(colorGroup)

        self.setLayout(mainlayout)

        self.show()


class NumEditTemp(QLineEdit):
    def __init__(
        self, format: str, blankChar: str, min: int, max: int, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.format = format
        self.blankChar = blankChar
        self.min = min
        self.max = max
        self.onFinish = lambda s: ()

        self.editingFinished.connect(self.finish)
        self.setStyleSheet("margin: 0px")

    def finish(self):
        try:
            num = int(re.sub("[^0-9]", "", self.text()))
            num = min(max(num, self.min), self.max)
        except:
            num = self.min

        self.setText(self.format.replace(self.blankChar, str(num)))
        self.onFinish(num)


class RadiusIcon(QWidget):
    def __init__(self, radius: float, color: QColor, size: QSize, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.radius = radius
        self.color = color
        self.prefSize = size
        self.setFixedSize(size)

    def sizeHint(self) -> QtCore.QSize:
        print(self.prefSize)
        return self.prefSize

    def minimumSizeHint(self) -> QtCore.QSize:
        return self.prefSize

    def setColor(self, newcolor: QColor):
        self.color = newcolor
        self.repaint()

    def setRadius(self, newRad):
        self.radius = newRad
        self.repaint()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)

        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(self.color)
        painter.setBackground(QColor(230, 230, 230))

        painter.drawEllipse(self.rect().center(), self.radius, self.radius)


class ColorButton(QPushButton):
    def __init__(self, size: QSize, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.preferSize = size

        self.onleftclick = lambda color: ()

    def sizeHint(self) -> QtCore.QSize:
        return self.preferSize

    def setColor(self, color: QColor):
        self.color = color
        self.setStyleSheet(f"QPushButton {{background-color: {self.color.name()}}}")

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(e)
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.onleftclick(self.color)
        elif e.buttons() == Qt.MouseButton.RightButton:
            color = QColorDialog.getColor()
            if not color.isValid():
                return
            self.color = color
            self.setStyleSheet(f"QPushButton {{background-color: {self.color.name()}}}")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    ex = PaintToolbar()
    sys.exit(app.exec_())
