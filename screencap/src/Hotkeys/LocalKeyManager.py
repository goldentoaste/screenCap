


from collections import defaultdict
from operator import truediv
import sys
from typing import Callable, Dict, List, Tuple

from PySide6.QtCore import QKeyCombination, QObject, QTime, QTimer, Qt
from PySide6.QtGui import  QShortcut
from PySide6.QtWidgets import QApplication, QWidget


class LocalKeyManager:

    __instance : "LocalKeyManager | None" = None

    def __init__(self) -> None:
        "dict, pagename -> dict {keyname -> QtKeyCombo, Callback}"
        self.hotKeys : Dict[str, Dict[str, Tuple[QKeyCombination, bool, Callable]]] = defaultdict(dict)
        self.contexts : Dict[str, Dict[QWidget, Dict[str, QShortcut]] ] = defaultdict(dict)



    @classmethod
    def getManager(cls):
        if not LocalKeyManager.__instance:
            LocalKeyManager.__instance = cls()

        return LocalKeyManager.__instance


    def registerShortCut(self, contextName:str, actionName:str, keyCombo : QKeyCombination, callback: Callable | None = None, autoRepeat:bool | None = None):
        '''
        Note callback provided be a function from the class, not instance
        '''

        if self.hotKeys[contextName].get(actionName, False):
            E_combo, E_repeat, E_callback = self.hotKeys[contextName][actionName]
            if not callback:
                callback = E_callback

            if autoRepeat is None:
                autoRepeat =  E_repeat

            # if this action is already registered, update existing connections
            for widget, scMap in self.contexts[contextName].items():
                sc = scMap[actionName]
                sc.setKey(keyCombo)

                sc.activated.disconnect()
                sc.activated.connect(lambda _callback = callback, _widget = widget: _callback(_widget))

                sc.setAutoRepeat(autoRepeat)

        if not callback:
            raise RuntimeError("callback must be provided when registering new callback")
        self.hotKeys[contextName][actionName] = (keyCombo, autoRepeat or False, callback)



    def registerContext(self, contextName:str, widget:QWidget):
        shortCuts : Dict[str, QShortcut]= dict()
        for actionName, (combo, autoRepeat, callback) in self.hotKeys[contextName].items():
            sc = QShortcut(combo, widget)
            sc.setAutoRepeat(autoRepeat)
            sc.activated.connect(lambda _callback = callback: _callback(widget) )
            shortCuts[actionName] = sc

            sc.destroyed.connect(lambda: print('test'))

        widget.destroyed.connect(lambda: self.contexts[contextName].pop(widget))

        self.contexts[contextName][widget] = shortCuts




class Test(QWidget):
    mgr = LocalKeyManager.getManager()
    mgr.registerShortCut("test", "A", QKeyCombination(Qt.Key.Key_A), lambda obj: print(obj.id, 'A'), False)
    mgr.registerShortCut("test", "B", QKeyCombination(Qt.Key.Key_B), lambda obj: print(obj.id, 'B'), False)

    def __init__(self, id:int):
        super().__init__()
        self.id = id

        self.mgr.registerContext("test", self)

        self.show()


if __name__ == "__main__":

    app = QApplication()
    t1 = Test(1)
    t2 = Test(2)

    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: (print("trigger!"), LocalKeyManager.getManager().registerShortCut("test", "A", QKeyCombination(Qt.Key.Key_X))))
    timer.start(1000)

    sys.exit(app.exec())







