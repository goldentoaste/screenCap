import ctypes
import win32api
from desktopmagic.screengrab_win32 import getDisplayRects, getRectAsImage
PROCESS_PER_MONITOR_DPI_AWARE = 2
MDT_EFFECTIVE_DPI = 0


def print_dpi():
    shcore = ctypes.windll.shcore
    monitors = win32api.EnumDisplayMonitors()
    hresult = shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
    assert hresult == 0
    dpiX = ctypes.c_uint()
    dpiY = ctypes.c_uint()
    for i, monitor in enumerate(monitors):
        shcore.GetDpiForMonitor(
            monitor[0].handle, MDT_EFFECTIVE_DPI, ctypes.byref(dpiX), ctypes.byref(dpiY)
        )
        rect = getDisplayRects()[i]
        print(rect)
        print(
            f"Monitor {i} (hmonitor: {monitor[0]}) = dpiX: {dpiX.value}, dpiY: {dpiY.value}, region:({rect[0]},{rect[1]})|({rect[2]},{rect[3]})"
        )
    input("press enter to exit....")


if __name__ == "__main__":
    print_dpi()