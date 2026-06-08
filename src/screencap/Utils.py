from os import path, makedirs
from datetime import datetime

from PySide6.QtGui import QBitmap, QBrush, QColor, QImage, QPainter, QPixmap, QRegion, Qt

# TODO: use global constants instead
targetPath = "./screencap.log"


class Logger:
    # https://softwareengineering.stackexchange.com/a/380212
    __log: "Logger"
    makedirs(path.dirname(path.abspath(targetPath)), exist_ok=True)
    with open(targetPath, "w", encoding="utf8") as f:
        pass  # clear log on start

    @classmethod
    def log(cls, msg: str):
        print(f"Logger: {msg}")
        with open(targetPath, "a", encoding="utf8") as f:
            f.write(f"{datetime.now().isoformat()}: {msg}")


def pixmapWithMaskedColor(pixmap: QPixmap, color: QColor):

    img = pixmap.toImage()
    painter = QPainter(img)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return QPixmap.fromImage(img)
