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
ERASE = 4
SELECT = 5


class DrawOptions:

    pen: QPen
    brush: QBrush
    shape: int
    opacity: float


def loadImage(path, x, y):
    return QPixmap(path, "PNG").scaled(
        x, y, transformMode=Qt.TransformationMode.SmoothTransformation
    )


class PaintToolbar(QWidget):
    def __init__(self,config: ConfigManager, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.config = config
        self.currentSelection = 0
        self.currentColor = QColor()
        self.initGui()
        self.initCursors()
        self.initVals()

    def initCursors(self):
        self.cursors = {
            (PATH, False, False): (loadImage("icons/cross.png", 32, 32), 16, 16),
            (PATH, True, False): (loadImage("icons/crossHLine.png", 32, 32), 16, 16),
            (PATH, False, True): (loadImage("icons/crossVLine.png", 32, 32), 16, 16),
            (LINE, False, False): (loadImage("icons/crossLine.png", 32, 32), 16, 16),
            (LINE, True, False): (loadImage("icons/crossZigZag.png", 32, 32), 16, 16),
            (RECT, False, False): (loadImage("icons/crossRect.png", 32, 32), 16, 16),
            (CIRCLE, False, False): (loadImage("icons/crossCircle.png", 32, 32), 16, 16),
            (SELECT, False, False): (Qt.CursorShape.ArrowCursor,),
            (ERASE, False, False): (loadImage("icons/eraserDark.png", 24, 24), 0, 24),
            
        }
    
    def setTestingVals(self):
        pass

    def getCursors(self):
        return self.cursors

    def initVals(self):
        self.radiusField.setText(f'{self.config.isize} px')
        self.radiusSlider.setValue(self.config.isize)
        
        self.alphaField.setText(f'Alpha {self.config.ialpha}%')
        self.alphaSlider.setValue(self.config.ialpha)
        
        colors = self.config.lscolors
        self.currentColor = QColor(colors[0])
        
        for i in range(len(colors)):
            self.colorButtons[i].setColor(QColor(colors[i]))

    def getDrawOptions(self):
        o = DrawOptions()
        o.shape = self.currentSelection
        color = self.currentColor
        color.setAlpha(255)
        o.opacity = self.alphaSlider.value() / 100
        
        o.pen = QPen(
            color,
            self.radiusSlider.value(),
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        o.brush = QBrush(
            color,
            Qt.BrushStyle.NoBrush
            if not self.fillCheck.isChecked()
            else Qt.BrushStyle.SolidPattern,
        )

        return o

    def initGui(self):
        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint 
            
        )

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        metric = QFontMetrics(QFont())
        mainlayout = QHBoxLayout()


        def setConfig(name, val):
            self.config.__setattr__(name, val)
            

        self.radiusField = NumEditTemp("* px", "*", 1, 20)
        self.radiusField.setFixedWidth(metric.horizontalAdvance("20 px  "))

        self.radiusIcon = RadiusIcon(1, Qt.GlobalColor.black, QSize(25, 25))
        self.radiusSlider = QSlider(Qt.Orientation.Horizontal)
        self.radiusSlider.setMinimum(1)
        self.radiusSlider.setMaximum(20)
        self.radiusSlider.setPageStep(1)
        self.radiusSlider.valueChanged.connect(
            lambda val: (
                self.radiusField.setText(f"{val} px"),
                self.radiusIcon.setRadius(val),
                setConfig('isize', val)
            )
        )
        self.radiusField.onFinish = lambda val: (self.radiusSlider.setSliderPosition(val), setConfig('isize', val))

        self.alphaField = NumEditTemp("Alpha *%", "*", 0, 100)
        self.alphaField.setFixedWidth(metric.horizontalAdvance("Alpha 100%  "))

        self.alphaSlider = QSlider(Qt.Orientation.Horizontal)
        self.alphaSlider.setMinimum(0)
        self.alphaSlider.setMaximum(100)
        self.alphaSlider.setPageStep(5)
        self.alphaSlider.valueChanged.connect(
            lambda val: (self.alphaField.setText(f"Alpha {val}%"), setConfig('ialpha', val))
        )
        self.alphaField.onFinish = lambda val: (self.alphaSlider.setSliderPosition(val), setConfig('ialpha', val)   )

        def assignmentSelection(val):
            self.currentSelection = val

        self.penButton = QPushButton(QIcon("icons/pen.svg"), "")
        self.penButton.setIconSize(QSize(24, 24))

        self.penButton.clicked.connect(lambda x: assignmentSelection(PATH))

        self.lineButton = QPushButton(QIcon("icons/line.svg"), "")
        self.lineButton.setIconSize(QSize(24, 24))
        self.lineButton.clicked.connect(lambda x: assignmentSelection(LINE))

        self.rectButton = QPushButton(QIcon("icons/rect.svg"), "")
        self.rectButton.setIconSize(QSize(24, 24))
        self.rectButton.clicked.connect(lambda x: assignmentSelection(RECT))

        self.elipseButton = QPushButton(QIcon("icons/circle.svg"), "")
        self.elipseButton.setIconSize(QSize(24, 24))
        self.elipseButton.clicked.connect(lambda x: assignmentSelection(CIRCLE))

        self.eraseButton = QPushButton(QIcon("icons/eraser.png"), "")
        self.eraseButton.clicked.connect(lambda x: assignmentSelection(ERASE))
        self.eraseButton.setIconSize(QSize(24, 24))

        self.selectButton = QPushButton(QIcon("icons/cursor.png"), "")
        self.selectButton.clicked.connect(lambda x: assignmentSelection(SELECT))
        self.selectButton.setIconSize(QSize(24, 24))

        self.fillCheck = QCheckBox("Fill")

        colorGroup = QGridLayout()
        colorGroup.setVerticalSpacing(0)
        colorGroup.setHorizontalSpacing(0)

        self.colorButtons : List[ColorButton] = []

        

        def updateConfigColor(button :ColorButton):
            color = button.color.name()
            colors = self.config.lscolors
            colors[button.index] = color
            self.config.lscolors = colors
            
            self.currentColor = color

        for i in range(10):
            c = ColorButton(QSize(58, 58), i)
            c.setColor(QColor(i * 10, i * 20, i * 10))
            c.onleftclick = lambda x, c=c: updateConfigColor(c)
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
        buttonGroup.addWidget(self.eraseButton)
        buttonGroup.addWidget(self.selectButton)
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

        painter.drawEllipse(self.rect().center(), self.radius // 2, self.radius // 2)


class ColorButton(QPushButton):
    def __init__(self, size: QSize, index:int, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.preferSize = size
        self.index = index

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
            color = QColorDialog.getColor(self.color, self.parent())
            if not color.isValid():
                return
            self.color = color
            self.setStyleSheet(f"QPushButton {{background-color: {self.color.name()}}}")
            self.onleftclick(self.color)


if __name__ == "__main__":
    import values
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    ex = PaintToolbar(ConfigManager('D:\Python Project\screenCap\QtExperimental\config.ini', values.defaultVariables))
    sys.exit(app.exec_())
