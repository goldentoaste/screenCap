import gc
import os
import pathlib
import time
from typing import List
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QHBoxLayout,
    QLabel,
    QListView,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

kbCons = 1024

import sys
import ConfigManager


class Recycler(QWidget):
    def __init__(self, path: str, config: ConfigManager.ConfigManager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = path
        self.config = config
        deskSize = QDesktopWidget().screenGeometry().size()
        self.maxSize = QSize(int(deskSize.width() / 6.5), int(deskSize.height() / 5))

        self.containers : List[QWidget] = []

        listholder = QWidget()
        self.listLayout = QVBoxLayout()
        listholder.setLayout(self.listLayout)

        scroller = QScrollArea()
        scroller.setWidget(listholder)
        scroller.setWidgetResizable(True)
        scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        mainlayout = QHBoxLayout()
        mainlayout.addWidget(scroller)

        self.setLayout(mainlayout)

        self.loadImages()

        self.show()
        self.resize(self.width(), int(self.maxSize.height() * 3.5))
        temp = ImageContainer(maxSize=self.maxSize)
        self.setFixedWidth(int(temp.width()))




    def loadImages(self):

        paths = sorted(
            pathlib.Path(self.path).glob("*.png"), key=lambda x: -os.path.getmtime(x)
        )

        if len(paths) > self.config.imaxsize:
            for i in range(len(paths) - 1, self.config.imaxsize - 1, -1):
                os.remove(paths[i])
                paths.pop(i)

        for path in paths:
            img = QPixmap(str(path), "PNG", Qt.ImageConversionFlag.AutoColor)
            self.containers.append(ImageContainer(img, path, self.maxSize))
            self.listLayout.addWidget(self.containers[-1])




class ImageContainer(QWidget):
    def __init__(self, image: QPixmap = None, path = "", maxSize: QSize = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

        layout = QHBoxLayout()
        img = QLabel()
        img.setFixedWidth(maxSize.width())
        if image is not None:
            scale = min(maxSize.width() / image.width(), maxSize.height() / image.height())
            img.setPixmap(
                image.scaled(int(image.width() * scale), int(image.height() * scale))
            )
            text = QLabel(
                text=f"""{time.strftime('%b.%d.%Y %I:%M|%p', time.localtime(os.path.getmtime(self.path)))}
                {image.width()}x{image.height()}
                {'%.2f' % (os.path.getsize(self.path)/kbCons)}kb"""
            )
        else:
            text = QLabel('%b.%d.%Y %I:%M|%p')

        text.setMargin(15)

        layout.addWidget(img)
        layout.addWidget(text)
        self.setLayout(layout)


if __name__ == "__main__":
    import values

    app = QApplication(sys.argv)

    ex = Recycler(
        os.path.join(os.getenv("appdata"), "screenCap"),
        ConfigManager.ConfigManager(
            "D:\\PythonProject\\screenCap\\QtExperimental\\config.ini",
            default=values.defaultVariables,
        ),
    )
    sys.exit(app.exec_())
