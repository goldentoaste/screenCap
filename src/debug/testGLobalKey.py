

import sys
from PySide6.QtWidgets import QApplication, QWidget
import ctypes as c
import ctypes.wintypes as w
import win32con as const

user32 = c.windll.user32
kernel32 = c.windll.kernel32



# typedef struct tagKBDLLHOOKSTRUCT {
#   DWORD     vkCode;
#   DWORD     scanCode;
#   DWORD     flags;
#   DWORD     time;
#   ULONG_PTR dwExtraInfo;
# } KBDLLHOOKSTRUCT, *LPKBDLLHOOKSTRUCT, *PKBDLLHOOKSTRUCT;


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
class KBDLLHOOKSTRUCT(c.Structure):
    _fields_ = [
        ("vkCode", w.DWORD),
        ("scanCode", w.DWORD),
        ("flags", w.DWORD),
        ("time", w.DWORD),
        ("dwExtraInfo", w.ULONG) # pointer
    ]


#  https://learn.microsoft.com/en-ca/windows/win32/api/winuser/nf-winuser-setwindowshookexa?redirectedfrom=MSDN
#  https://learn.microsoft.com/en-us/windows/win32/winmsg/keyboardproc
# TODO:  CallNextHookEx at end of callback
# TODO:  UnhookWindowsHookEx before program exits
"""
WH_KEYBOARD_LL handles low level keyboard events, without attaching dll to all processes
hookcallback is c function pointer of a python call back with the same signiture
GetModuleHandle is used to get current exe handle, used to identify context with the callback is executed in
thread 0 means this callback is associated with all threads/processes.
"""
class Stuff(QWidget):
    def __init__(self,):
        super().__init__(None)
        self.show()


        def LowLevelKeyboardProc(code: int, wParam: int, lParam: int):
            '''
            wParam, lParam are converted to python int type automatically.
            '''
            dataStrt = c.cast(lParam, c.POINTER(KBDLLHOOKSTRUCT)).contents
            print("received callback: ", code, wParam, dataStrt.vkCode, dataStrt.dwExtraInfo)
            return user32.CallNextHookEx(0, code, w.WPARAM(wParam), w.LPARAM(lParam))
        WIN_FUN_FAC = c.WINFUNCTYPE(c.c_long, w.INT, w.WPARAM, w.LPARAM)
        self.hookCallback = WIN_FUN_FAC(LowLevelKeyboardProc)

        res = user32.SetWindowsHookExW(const.WH_KEYBOARD_LL, self.hookCallback, None, 0)
        if (res == 0):
            errorCode = kernel32.GetLastError()
            print("error code: ", errorCode)

if __name__ == "__main__":
    a = QApplication()
    s = Stuff()

    sys.exit(a.exec())