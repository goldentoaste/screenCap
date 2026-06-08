
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QKeySequenceEdit
from PySide6.QtCore import Signal, QKeyCombination

class HotkeyEdit(QKeySequenceEdit):
    comboChangeSignal = Signal((QKeyCombination))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = 0

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)

        keyCombo = e.keyCombination()
        key = keyCombo.key()
        keyMod = keyCombo.keyboardModifiers()

        if key in QT_MODIFIERS:
            return

        if keyMod & Qt.KeyboardModifier.ShiftModifier:
            if key in QT_SHIFT_WIN_CASE:
                keyCombo = QKeyCombination(keyMod, QT_SHIFT_WIN_CASE[key])
            if key in QT_SHIFT_NUMPAD_WIN_CASE and not (
                keyMod & Qt.KeyboardModifier.KeypadModifier
            ):
                keyCombo = QKeyCombination(keyMod, QT_SHIFT_NUMPAD_WIN_CASE[key])

        self.setKeySequence(QKeySequence(keyCombo))
        self.comboChangeSignal.emit(keyCombo)

    def getHotkey(self):
        seq = self.keySequence()
        if seq.count() > 0:
            return seq[0]  # pyright: ignore[reportIndexIssue]
        return None

    def setId(self, id: int):
        self.id = id

    def getId(self):
        return self.id


#####################################


from PySide6.QtCore import Qt, Signal

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey
modifiers = [16, 17, 18, 91]

QT_KEY_TO_WIN_VK = {
    # Special keys
    Qt.Key.Key_Backspace: 0x08,  # VK_BACK
    Qt.Key.Key_Tab: 0x09,  # VK_TAB
    Qt.Key.Key_Clear: 0x0C,  # VK_CLEAR
    Qt.Key.Key_Return: 0x0D,  # VK_RETURN
    Qt.Key.Key_Enter: 0x0D,  # VK_RETURN (same as Return)
    # Qt.Key.Key_Shift: 0x10,          # VK_SHIFT
    # Qt.Key.Key_Control: 0x11,        # VK_CONTROL
    # Qt.Key.Key_Alt: 0x12,            # VK_MENU
    Qt.Key.Key_Pause: 0x13,  # VK_PAUSE
    Qt.Key.Key_CapsLock: 0x14,  # VK_CAPITAL
    # IME keys
    Qt.Key.Key_Kanji: 0x19,  # VK_KANJI
    Qt.Key.Key_Hangul: 0x15,  # VK_HANGUL
    Qt.Key.Key_Hangul_Hanja: 0x19,  # VK_HANJA
    # Navigation keys
    Qt.Key.Key_Escape: 0x1B,  # VK_ESCAPE
    Qt.Key.Key_Space: 0x20,  # VK_SPACE
    Qt.Key.Key_PageUp: 0x21,  # VK_PRIOR
    Qt.Key.Key_PageDown: 0x22,  # VK_NEXT
    Qt.Key.Key_End: 0x23,  # VK_END
    Qt.Key.Key_Home: 0x24,  # VK_HOME
    Qt.Key.Key_Left: 0x25,  # VK_LEFT
    Qt.Key.Key_Up: 0x26,  # VK_UP
    Qt.Key.Key_Right: 0x27,  # VK_RIGHT
    Qt.Key.Key_Down: 0x28,  # VK_DOWN
    Qt.Key.Key_Select: 0x29,  # VK_SELECT
    Qt.Key.Key_Print: 0x2A,  # VK_PRINT
    Qt.Key.Key_Execute: 0x2B,  # VK_EXECUTE
    Qt.Key.Key_SysReq: 0x2C,  # VK_SNAPSHOT (Print Screen)
    Qt.Key.Key_Insert: 0x2D,  # VK_INSERT
    Qt.Key.Key_Delete: 0x2E,  # VK_DELETE
    Qt.Key.Key_Help: 0x2F,  # VK_HELP
    # Number keys (0-9)
    Qt.Key.Key_0: 0x30,  # 0 key
    Qt.Key.Key_1: 0x31,  # 1 key
    Qt.Key.Key_2: 0x32,  # 2 key
    Qt.Key.Key_3: 0x33,  # 3 key
    Qt.Key.Key_4: 0x34,  # 4 key
    Qt.Key.Key_5: 0x35,  # 5 key
    Qt.Key.Key_6: 0x36,  # 6 key
    Qt.Key.Key_7: 0x37,  # 7 key
    Qt.Key.Key_8: 0x38,  # 8 key
    Qt.Key.Key_9: 0x39,  # 9 key
    # Letter keys (A-Z)
    Qt.Key.Key_A: 0x41,  # A key
    Qt.Key.Key_B: 0x42,  # B key
    Qt.Key.Key_C: 0x43,  # C key
    Qt.Key.Key_D: 0x44,  # D key
    Qt.Key.Key_E: 0x45,  # E key
    Qt.Key.Key_F: 0x46,  # F key
    Qt.Key.Key_G: 0x47,  # G key
    Qt.Key.Key_H: 0x48,  # H key
    Qt.Key.Key_I: 0x49,  # I key
    Qt.Key.Key_J: 0x4A,  # J key
    Qt.Key.Key_K: 0x4B,  # K key
    Qt.Key.Key_L: 0x4C,  # L key
    Qt.Key.Key_M: 0x4D,  # M key
    Qt.Key.Key_N: 0x4E,  # N key
    Qt.Key.Key_O: 0x4F,  # O key
    Qt.Key.Key_P: 0x50,  # P key
    Qt.Key.Key_Q: 0x51,  # Q key
    Qt.Key.Key_R: 0x52,  # R key
    Qt.Key.Key_S: 0x53,  # S key
    Qt.Key.Key_T: 0x54,  # T key
    Qt.Key.Key_U: 0x55,  # U key
    Qt.Key.Key_V: 0x56,  # V key
    Qt.Key.Key_W: 0x57,  # W key
    Qt.Key.Key_X: 0x58,  # X key
    Qt.Key.Key_Y: 0x59,  # Y key
    Qt.Key.Key_Z: 0x5A,  # Z key
    # Windows keys
    # Qt.Key.Key_Super_L: 0x5B,        # VK_LWIN (Left Windows key)
    # Qt.Key.Key_Super_R: 0x5C,        # VK_RWIN (Right Windows key)
    Qt.Key.Key_Menu: 0x5D,  # VK_APPS (Application/Context menu key)
    Qt.Key.Key_Sleep: 0x5F,  # VK_SLEEP
    # Numpad keys
    # Note: Qt doesn't distinguish numpad numbers from regular numbers by default
    # These would need KeypadModifier to be properly identified
    Qt.Key.Key_Asterisk: 0x6A,
    Qt.Key.Key_Plus: 0x6B,
    Qt.Key.Key_Period: 0x6E,
    # Function keys (F1-F24)
    Qt.Key.Key_F1: 0x70,  # VK_F1
    Qt.Key.Key_F2: 0x71,  # VK_F2
    Qt.Key.Key_F3: 0x72,  # VK_F3
    Qt.Key.Key_F4: 0x73,  # VK_F4
    Qt.Key.Key_F5: 0x74,  # VK_F5
    Qt.Key.Key_F6: 0x75,  # VK_F6
    Qt.Key.Key_F7: 0x76,  # VK_F7
    Qt.Key.Key_F8: 0x77,  # VK_F8
    Qt.Key.Key_F9: 0x78,  # VK_F9
    Qt.Key.Key_F10: 0x79,  # VK_F10
    Qt.Key.Key_F11: 0x7A,  # VK_F11
    Qt.Key.Key_F12: 0x7B,  # VK_F12
    Qt.Key.Key_F13: 0x7C,  # VK_F13
    Qt.Key.Key_F14: 0x7D,  # VK_F14
    Qt.Key.Key_F15: 0x7E,  # VK_F15
    Qt.Key.Key_F16: 0x7F,  # VK_F16
    Qt.Key.Key_F17: 0x80,  # VK_F17
    Qt.Key.Key_F18: 0x81,  # VK_F18
    Qt.Key.Key_F19: 0x82,  # VK_F19
    Qt.Key.Key_F20: 0x83,  # VK_F20
    Qt.Key.Key_F21: 0x84,  # VK_F21
    Qt.Key.Key_F22: 0x85,  # VK_F22
    Qt.Key.Key_F23: 0x86,  # VK_F23
    Qt.Key.Key_F24: 0x87,  # VK_F24
    # Lock keys
    Qt.Key.Key_NumLock: 0x90,  # VK_NUMLOCK
    Qt.Key.Key_ScrollLock: 0x91,  # VK_SCROLL
    # Browser keys
    Qt.Key.Key_Back: 0xA6,  # VK_BROWSER_BACK
    Qt.Key.Key_Forward: 0xA7,  # VK_BROWSER_FORWARD
    Qt.Key.Key_Refresh: 0xA8,  # VK_BROWSER_REFRESH
    Qt.Key.Key_Stop: 0xA9,  # VK_BROWSER_STOP
    Qt.Key.Key_Search: 0xAA,  # VK_BROWSER_SEARCH
    Qt.Key.Key_Favorites: 0xAB,  # VK_BROWSER_FAVORITES
    Qt.Key.Key_HomePage: 0xAC,  # VK_BROWSER_HOME
    # Volume keys
    Qt.Key.Key_VolumeMute: 0xAD,  # VK_VOLUME_MUTE
    Qt.Key.Key_VolumeDown: 0xAE,  # VK_VOLUME_DOWN
    Qt.Key.Key_VolumeUp: 0xAF,  # VK_VOLUME_UP
    # Media keys
    Qt.Key.Key_MediaNext: 0xB0,  # VK_MEDIA_NEXT_TRACK
    Qt.Key.Key_MediaPrevious: 0xB1,  # VK_MEDIA_PREV_TRACK
    Qt.Key.Key_MediaStop: 0xB2,  # VK_MEDIA_STOP
    Qt.Key.Key_MediaTogglePlayPause: 0xB3,  # VK_MEDIA_PLAY_PAUSE
    Qt.Key.Key_LaunchMail: 0xB4,  # VK_LAUNCH_MAIL
    Qt.Key.Key_LaunchMedia: 0xB5,  # VK_LAUNCH_MEDIA_SELECT
    Qt.Key.Key_Launch0: 0xB6,  # VK_LAUNCH_APP1
    Qt.Key.Key_Launch1: 0xB7,  # VK_LAUNCH_APP2
    # OEM keys (US keyboard layout)
    Qt.Key.Key_Semicolon: 0xBA,  # VK_OEM_1 (;:)
    Qt.Key.Key_Equal: 0xBB,  # VK_OEM_PLUS (=+)
    Qt.Key.Key_Comma: 0xBC,  # VK_OEM_COMMA (,<)
    Qt.Key.Key_Minus: 0xBD,  # VK_OEM_MINUS (-_)
    Qt.Key.Key_Period: 0xBE,  # VK_OEM_PERIOD (.>)
    Qt.Key.Key_Slash: 0xBF,  # VK_OEM_2 (/?)
    Qt.Key.Key_QuoteLeft: 0xC0,  # VK_OEM_3 (`~)
    Qt.Key.Key_BracketLeft: 0xDB,  # VK_OEM_4 ([{)
    Qt.Key.Key_Backslash: 0xDC,  # VK_OEM_5 (\|)
    Qt.Key.Key_BracketRight: 0xDD,  # VK_OEM_6 (]})
    Qt.Key.Key_Apostrophe: 0xDE,  # VK_OEM_7 ('")
    # Additional special keys
    Qt.Key.Key_Cancel: 0x03,  # VK_CANCEL
    Qt.Key.Key_Play: 0xFA,  # VK_PLAY
    Qt.Key.Key_Zoom: 0xFB,  # VK_ZOOM
}

QT_NumPad_WIN_VK = {
    Qt.Key.Key_Minus: 0x6D,  # numpad subtract
    Qt.Key.Key_Period: 0x6E,  # VK_DECIMAL (.)
    Qt.Key.Key_Slash: 0x6F,  # numpad divide,
    Qt.Key.Key_0: 0x60,  # VK_NUMPAD0
    Qt.Key.Key_1: 0x61,  # VK_NUMPAD1
    Qt.Key.Key_2: 0x62,  # VK_NUMPAD2
    Qt.Key.Key_3: 0x63,  # VK_NUMPAD3
    Qt.Key.Key_4: 0x64,  # VK_NUMPAD4
    Qt.Key.Key_5: 0x65,  # VK_NUMPAD5
    Qt.Key.Key_6: 0x66,  # VK_NUMPAD6
    Qt.Key.Key_7: 0x67,  # VK_NUMPAD7
    Qt.Key.Key_8: 0x68,  # VK_NUMPAD8
    Qt.Key.Key_9: 0x69,  # VK_NUMPAD9
}


# TODO, allow alternate keyboard layouts? not big deal for now.
# maps from upper case to lower case, for example, ? -> /
# these keys are likely OEM, so depends on exact keyboard layout
QT_SHIFT_WIN_CASE = {
    Qt.Key.Key_AsciiTilde: Qt.Key.Key_QuoteLeft,
    Qt.Key.Key_Exclam: Qt.Key.Key_1,
    Qt.Key.Key_At: Qt.Key.Key_2,
    Qt.Key.Key_NumberSign: Qt.Key.Key_3,
    Qt.Key.Key_Dollar: Qt.Key.Key_4,
    Qt.Key.Key_Percent: Qt.Key.Key_5,
    Qt.Key.Key_AsciiCircum: Qt.Key.Key_6,
    Qt.Key.Key_Ampersand: Qt.Key.Key_7,
    Qt.Key.Key_ParenLeft: Qt.Key.Key_9,
    Qt.Key.Key_ParenRight: Qt.Key.Key_0,
    Qt.Key.Key_Underscore: Qt.Key.Key_Minus,
    Qt.Key.Key_BraceLeft: Qt.Key.Key_BracketLeft,
    Qt.Key.Key_BraceRight: Qt.Key.Key_BracketRight,
    Qt.Key.Key_Colon: Qt.Key.Key_Semicolon,
    Qt.Key.Key_QuoteDbl: Qt.Key.Key_Apostrophe,
    Qt.Key.Key_Bar: Qt.Key.Key_Backslash,
    Qt.Key.Key_Less: Qt.Key.Key_Comma,
    Qt.Key.Key_Greater: Qt.Key.Key_Period,
    Qt.Key.Key_Question: Qt.Key.Key_Slash,
}

QT_SHIFT_NUMPAD_WIN_CASE = {
    Qt.Key.Key_Asterisk: Qt.Key.Key_8,  # NOTE: this is not the same as numpad asterisk. Numpad should have higher prio
    Qt.Key.Key_Plus: Qt.Key.Key_Equal,  # NOTE: shared with numpad plus sign.
}

QT_MODIFIERS = {Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta}
