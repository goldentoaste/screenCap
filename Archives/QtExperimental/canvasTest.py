








import sys
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setLayout(QHBoxLayout())
    
    pixmap = QPixmap(500, 500)
    pixmap.fill(Qt.GlobalColor.white)
    painter = QPainter(pixmap)
    
    painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
    painter.setPen(QPen(Qt.GlobalColor.black, 10))
    
    
    label = QLabel()
    label.setPixmap(pixmap)
    window.layout().addWidget(label)
    window.show()
    
    sys.exit(app.exec_())
