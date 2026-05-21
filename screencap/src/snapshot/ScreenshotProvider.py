



import sys
from typing import override

from PySide6.QtGui import QPixmap, QScreen


def getCurrentScreen() -> QScreen:
    """
    Get the screen which is the cursor is currently in.
    """
    screens = [screen for screen in QApplication.screens()]
    pos = QCursor.pos()
    for screen in screens:
        if screen.geometry().contains(pos, False):
            return screen
    return screens[0]


class _ScreenshotProvider:

    @staticmethod
    def takeScreenShot()-> tuple[QPixmap, QScreen]:
        raise NotImplementedError("takeScreenShot method must be implemented by subclass")

if sys.platform == "win32":

    from PySide6.QtGui import QCursor
    from PySide6.QtWidgets import QApplication

    class WindowsScreenshotProvider(_ScreenshotProvider):
        @override
        @staticmethod
        def takeScreenShot():
            '''
            Somehow take a screenshot, then return a QPixmap of the screenshot.
            '''

            screen =  getCurrentScreen()
            img = screen.grabWindow()

            return img, screen

if sys.platform == 'linux':

    import dbus

    class LinuxScreenshotProvider(_ScreenshotProvider):

        @staticmethod
        def getDisplayPermission():


        @override
        @staticmethod
        def takeScreenShot():
            '''
            Somehow take a screenshot, then return a QPixmap of the screenshot.
            '''
            return QPixmap(), QScreen()
        pass

def getScreenshotProvider():
    if sys.platform == "win32":
        return WindowsScreenshotProvider()
    elif sys.platform == 'linux':
        return LinuxScreenshotProvider()
    else:
        raise NotImplementedError(f"Unsupported platform: {sys.platform}")

ScreenshotProvider = getScreenshotProvider()