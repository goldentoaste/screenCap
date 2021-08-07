
from PyQt5 import QtWidgets
from PyQt5.QtCore import QMargins, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, Qt

class SelectionBox(QtWidgets.QRubberBand):
    
    
    
    def __init__(self, a0, parent) -> None:
        super().__init__(a0, parent=parent)
        
        
        

topleft = 0
top = 1
top = 2
topright = 3

class SizeGrip(QtWidgets.QWidget):
    
    
    def __init__(self, parent):
        super().__init__(parent)
        
        