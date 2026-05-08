from ctypes import c_void_p
from ctypes.wintypes import HWND, INT, UINT
from enum import Enum
import sys

from typing import TYPE_CHECKING

from PySide6.QtCore import QByteArray, QPoint, QRect, Qt
from PySide6.QtGui import QPainter
from win32con import HTCAPTION, WVR_REDRAW, WVR_VALIDRECTS


class ResizeDir(Enum):
    NONE = 0
    VER = 1
    HOR = 2
    BOTH = 3


if sys.platform == "win32":
    if TYPE_CHECKING:
        from screencap.src.snapshot.Snapshot import Snapshot
    from ctypes import POINTER, cast, wintypes, c_short, Structure
    from ctypes.wintypes import MSG, RECT

    from win32con import (
        WM_NCHITTEST,
        HTTOP,
        HTLEFT,
        HTTOPLEFT,
        HTRIGHT,
        HTTOPRIGHT,
        HTBOTTOM,
        HTBOTTOMLEFT,
        HTBOTTOMRIGHT,
        WM_ENTERSIZEMOVE,
        WM_EXITSIZEMOVE,
        WM_SIZING,
        WMSZ_BOTTOM,
        WMSZ_BOTTOMLEFT,
        WMSZ_BOTTOMRIGHT,
        WMSZ_LEFT,
        WMSZ_RIGHT,
        WMSZ_TOP,
        WMSZ_TOPLEFT,
        WMSZ_TOPRIGHT,
        WM_NCCALCSIZE,
    )

    class WINDOWPOS(Structure):
        """
        https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowpos
        """

        hwnd: HWND
        hwndInsertAfter: HWND
        x: INT
        y: INT
        cx: INT
        cy: INT
        flags: UINT

        _fields_ = [
            ("hwnd", HWND),
            ("hwndInsertAfter", HWND),
            ("x", INT),
            ("y", INT),
            ("cx", INT),
            ("cy", INT),
            ("flags", UINT),
        ]

    class NCCALCSIZE_PARAMS(Structure):
        """
        https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-nccalcsize_params

        Notes on how rgrc works,

        """

        rgrc: list[RECT]
        lppos: int

        _fields_ = [
            ("rgrc", RECT * 3),
            ("lppos", c_void_p),
        ]

    class WindowResizeHelper:
        """
        Intercepts Windows API messages to enforce a fixed aspect ratio when the snapshot window is resized.
        """

        def __init__(self, window: "Snapshot") -> None:
            self.margin = 10
            self.window = window
            self.resizeDir: ResizeDir = ResizeDir.NONE
            self.isResizing = False

            self.aspectRatio = 1

            self.lastWidth = 0
            self.lastHeight = 0

            self.window.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.SubWindow
            )

        def nativeEvent(
            self,
            eventType: QByteArray | bytes | bytearray | memoryview,
            message: int,
        ):
            """
            Forward the target window's nativeEvent filter here

            return type: (boolean (if event is handled), result (lparam, for windows only))
            """

            msg = cast(int(message), POINTER(MSG)).contents
            if msg.message == WM_ENTERSIZEMOVE:
                self.isResizing = True
                self.lastWidth = self.window.width() * self.window.devicePixelRatio()
                self.lastHeight = self.window.height() * self.window.devicePixelRatio()

                self.aspectRatio = (
                    self.window.pixmap.width() / self.window.pixmap.height()
                )

                # Disable high-quality rendering during live resize for performance
                self.window.pixmapItem.setTransformationMode(
                    Qt.TransformationMode.FastTransformation
                )
                self.window.view.setRenderHint(
                    QPainter.RenderHint.SmoothPixmapTransform, False
                )
                self.window.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
                return True, 0
            elif msg.message == WM_EXITSIZEMOVE:
                self.isResizing = False
                self.window.pixmapItem.setTransformationMode(
                    Qt.TransformationMode.SmoothTransformation
                )
                self.window.view.setRenderHint(
                    QPainter.RenderHint.SmoothPixmapTransform, True
                )
                self.window.view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                return True, 0
            elif msg.message == WM_NCHITTEST and not self.window.cropping:
                hitRes = self.hitTest(msg)
                if hitRes:
                    return hitRes
            elif msg.message == WM_SIZING:
                sizingRes = self.nativeSizeEvent(msg)
                if sizingRes:
                    return sizingRes

            return False

        def nativeSizeEvent(self, msg: MSG):
            """
            Maintains the original aspect ratio during window resize.
            - Edge resizes (top/bottom/left/right): Scale symmetrically from the center.
            - Corner resizes: The opposite corner stays fixed. Width dictates the new height.
            """
            sizeEdge = msg.wParam  # See, WMSZ_<Edge>
            rect = cast(int(msg.lParam), POINTER(RECT)).contents
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            if width < 50 or height < 50:
                return False

            if sizeEdge == WMSZ_TOP or sizeEdge == WMSZ_BOTTOM:
                newWidth = height * self.aspectRatio
                dw = round(newWidth - self.lastWidth)  # renamed to dw for width!
                dw_half = round(dw / 2)
                rect.left -= dw_half
                rect.right += dw - dw_half

            elif sizeEdge == WMSZ_LEFT or sizeEdge == WMSZ_RIGHT:
                newHeight = width / self.aspectRatio
                dh = round(newHeight - self.lastHeight)
                dh_half = round(dh / 2)
                rect.top -= dh_half
                rect.bottom += dh - dh_half

            elif sizeEdge in (
                WMSZ_TOPLEFT,
                WMSZ_TOPRIGHT,
                WMSZ_BOTTOMLEFT,
                WMSZ_BOTTOMRIGHT,
            ):
                newWidth = rect.right - rect.left
                newHeight = round(newWidth / self.aspectRatio)

                if sizeEdge == WMSZ_TOPLEFT:
                    rect.left = rect.right - newWidth
                    rect.top = rect.bottom - newHeight
                elif sizeEdge == WMSZ_TOPRIGHT:
                    rect.right = rect.left + newWidth
                    rect.top = rect.bottom - newHeight
                elif sizeEdge == WMSZ_BOTTOMLEFT:
                    rect.left = rect.right - newWidth
                    rect.bottom = rect.top + newHeight
                elif sizeEdge == WMSZ_BOTTOMRIGHT:
                    rect.right = rect.left + newWidth
                    rect.bottom = rect.top + newHeight
                else:
                    return False  # bad size edge
            else:
                return False  # bad size edge

            self.lastWidth = rect.right - rect.left
            self.lastHeight = rect.bottom - rect.top
            return True, 1

        def hitTest(self, msg: MSG):
            """
            Checks if mouse coordinates fall onto window resize edges/corners.
            Also accounts for multi-monitor negative coordinate spaces.
            """
            geo = self.window.geometry()
            dpi = self.window.devicePixelRatioF()
            x = int(c_short(msg.lParam & 0xFFFF).value / dpi)
            y = int(c_short((msg.lParam >> 16) & 0xFFFF).value / dpi)
            left = geo.left()
            right = geo.right()
            top = geo.top()
            bottom = geo.bottom()

            if y < top + self.margin:
                if x < left + self.margin:
                    self.resizeDir = ResizeDir.BOTH
                    return True, HTTOPLEFT
                elif x > right - self.margin:
                    self.resizeDir = ResizeDir.BOTH
                    return True, HTTOPRIGHT
                else:
                    self.resizeDir = ResizeDir.VER
                    return True, HTTOP
            elif y > bottom - self.margin:
                if x < left + self.margin:
                    self.resizeDir = ResizeDir.BOTH
                    return True, HTBOTTOMLEFT
                elif x > right - self.margin:
                    self.resizeDir = ResizeDir.BOTH
                    return True, HTBOTTOMRIGHT
                else:
                    self.resizeDir = ResizeDir.VER
                    return True, HTBOTTOM
            elif x < left + self.margin:
                self.resizeDir = ResizeDir.HOR
                return True, HTLEFT
            elif x > right - self.margin:
                self.resizeDir = ResizeDir.HOR
                return True, HTRIGHT
            else:
                return True, HTCAPTION # Treat the entire window as draggable

        def handleResize(self):
            """
            During handling of windows resizing msg (nativeSizeEvent), the window should already be in the correct aspect ratio.
            This method resizes the image to fit the new window size. Since aspect ratio is based on image, only scale adjustments is needed.
            """
            newScale = (
                self.window.width() * self.window.devicePixelRatioF()
            ) / self.window.pixmap.width()
            self.window.scale = newScale
            self.window.pixmapItem.setScale(self.window.scale)
            self.window.view.setFixedSize(self.window.size())
            self.window.view.setSceneRect(QRect(QPoint(), self.window.size()))
            self.window.setBorder(self.window.rect().toRectF())
