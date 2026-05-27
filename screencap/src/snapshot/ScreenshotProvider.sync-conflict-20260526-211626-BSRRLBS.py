import sys
from typing import override

from PySide6.QtCore import QEventLoop
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusObjectPath
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
    def takeScreenShot() -> tuple[QPixmap, QScreen]:
        raise NotImplementedError(
            "takeScreenShot method must be implemented by subclass"
        )


if sys.platform == "win32":

    from PySide6.QtGui import QCursor
    from PySide6.QtWidgets import QApplication

    class WindowsScreenshotProvider(_ScreenshotProvider):
        @override
        @staticmethod
        def takeScreenShot():
            """
            Somehow take a screenshot, then return a QPixmap of the screenshot.
            """

            screen = getCurrentScreen()
            img = screen.grabWindow()

            return img, screen


if sys.platform == "linux":
    from PySide6.QtDBus import QDBus

    interface = QDBusInterface(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.ScreenCast",
        QDBusConnection.sessionBus(),
    )

    def waitForResponse(req: QDBusObjectPath):

        loop = QEventLoop()
        res = {}

        def onRes(code, result: dict):
            if code == 0:
                res.update(result)
            else:
                print("Error awaiting response: ", req.path(), "\nError code", code)
            loop.quit()

        path = req.path()
        success = (
            QDBusConnection.sessionBus().connect(  # pyright: ignore[reportCallIssue]
                "org.freedesktop.portal.Desktop",
                path,
                "org.freedesktop.portal.Request",
                "Response",
                onRes,
            )
        )

        if not success:
            print("failed in connect to Dbus success signal")
            return None

        loop.exec()

        return res

    def grantFreeDK_Permission():
        """
        initialize connection permission, using ScreenCast interface.

        Hopefully this permission is remembered.
        """

        # Create session and get it's path
        opts = {
            "handle_token": "goldentoaste_screencap",
            "session_handle_token": "goldentoaste_screencap",
        }
        res = interface.call("CreateSession", opts)
        sessionPath = res.arguments()[0]
        print("create session res", res.arguments(), sessionPath.path())
        session = waitForResponse(sessionPath)
        print(session)

        # Select record monitor source
        opts = {"persist_mode": 2}
        res = interface.call("SelectSources", sessionPath, opts)
        print("select source res", res.arguments())

        # Start the session
        res = interface.call("Start", sessionPath, "")
        print("Start session res", res.arguments())

    if __name__ == "__main__":
        grantFreeDK_Permission()  # testing

    class LinuxScreenshotProvider(_ScreenshotProvider):

        @staticmethod
        def getDisplayPermission():
            pass

        @override
        @staticmethod
        def takeScreenShot():
            """
            Somehow take a screenshot, then return a QPixmap of the screenshot.
            """
            return QPixmap(), QScreen()

        pass


def getScreenshotProvider():
    if sys.platform == "win32":
        return WindowsScreenshotProvider()
    elif sys.platform == "linux":
        return LinuxScreenshotProvider()
    else:
        raise NotImplementedError(f"Unsupported platform: {sys.platform}")


ScreenshotProvider = getScreenshotProvider()
