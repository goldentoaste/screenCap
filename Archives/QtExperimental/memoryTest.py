
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication
from PyQt5.sip import setdestroyonexit
from guppy import hpy

from PIL import Image
h = hpy()
# with open("help.png") as f:
#     print(h.iso(f))
#     input("press enter to continue")


# with Image.open("help.png") as f:
#     print(f)
#     print(h.iso(f))
#     input("press enter to continue")

# 

import desktopmagic.screengrab_win32
# with desktopmagic.screengrab_win32.getScreenAsImage() as f:
#     print(f)
#     print(h.iso(f))
#     f.save("screenshot.jpg", "JPEG", quality = 100, subsampling=0)
#     input("press enter to continue")
import sys
from random import random
if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    for s in QApplication.screens():
        print(s, s.geometry())
        img  = s.grabWindow(0)
        img.save(f"{random()}.png", "PNG", 0)
    # print(desktopmagic.screengrab_win32.getDisplayRects())
    
    # timer = QTimer()
    # timer.setInterval(500)
    # timer.timeout.connect(lambda:print(QCursor.pos()))
    # timer.start()
    import pynput
    sys.exit(app.exec_())
    