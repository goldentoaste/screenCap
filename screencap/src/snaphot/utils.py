

from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication


def getCurrentScreen():
        """
        Get the screen which is the cursor is currently in.
        """
        screens = [screen for screen in QApplication.screens()]
        pos = QCursor.pos()
        for screen in screens:
            if screen.geometry().contains(pos, False):
                return screen
        return screens[0]