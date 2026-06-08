import sys
from typing import Any, override

from PySide6.QtCore import SLOT, QEventLoop, QObject, QTimer, Slot
from PySide6.QtGui import QPixmap, QScreen
print(sys.path)
from screencap.GlobalContext import GlobalContext


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
    from PySide6.QtDBus import QDBus,QDBusConnection, QDBusInterface, QDBusObjectPath, QDBusPendingCall, QDBusPendingCallWatcher

    interface = QDBusInterface(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.ScreenCast",
        QDBusConnection.sessionBus(),
    )



    class QDBusAwait(QObject):

        def __init__(self) -> None:
            super().__init__(None)

            self.path = f'/org/freedesktop/portal/desktop/request/{QDBusConnection.sessionBus().baseService()[1:].replace('.', '_')}/goldentoaste_screencap'

            self.loop = QEventLoop()
            self.result: dict[str, Any] = {}
            self.code = -1

        def waitForResponse(self, *args):
            self.setup()
            res = interface.call(*args)
            print(res.arguments()[0].path())
            self.loop.exec()

            return self.result


        @Slot('uint', dict)  # pyright: ignore[reportCallIssue, reportArgumentType]
        def onResult(self, code:int, res:dict[Any, Any]):
            self.result = res
            self.loop.quit()

        def setup(self):
            print(self.path)
            success = (
                QDBusConnection.sessionBus().connect(  # pyright: ignore[reportCallIssue]
                    "org.freedesktop.portal.Desktop",
                    self.path,
                    "org.freedesktop.portal.Request",
                    "Response",
                    self,
                    SLOT('onResult(uint, QVariantMap)')  # pyright: ignore[reportArgumentType]
                )
            )

            if not success:
                print("failed in connect to Dbus success signal")
                return None


    def grantFreeDK_Permission():
        """
        initialize connection permission, using ScreenCast interface.

        Hopefully this permission is remembered.
        """

        waiter = QDBusAwait()
        config = GlobalContext.getCtx().getConfig()

        # Create session and get it's path
        opts = {
            "handle_token": "goldentoaste_screencap",
            "session_handle_token": "goldentoaste_screencap",
        }

        res = waiter.waitForResponse("CreateSession", opts)
        if not res["session_handle"]:
            raise Exception("Failed to create session, no session handle returned")

        sessionHandle = QDBusObjectPath(res['session_handle'])


        # Select record monitor source
        opts: dict[str, Any] = {"persist_mode": 2, 'cursor_mode': 1}

        if config.permToken:
            opts['restore_token'] = config.permToken

        res = waiter.waitForResponse("SelectSources", sessionHandle, opts)
        print(res)

        # Start the session
        # res = interface.call("Start", sessionHandle, "")
        # print("Start session res", res.arguments())

    if __name__ == "__main__":
        from PySide6.QtWidgets import QApplication
        a = QApplication()
        timer = QTimer()
        timer.timeout.connect(lambda: (grantFreeDK_Permission(), sys.exit()))
        timer.setInterval(10)
        timer.setSingleShot(True)
        timer.start()

        a.exec()


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
