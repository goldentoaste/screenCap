


class x:
    
    def __int__(self):
        print('init obj')
        self.func = lambda: print('1')
        
    def stuff(self, s):
        print('obj', s)
        

o = x()

def mod(item):
    item.func = lambda: print('2')

o.func = lambda: print('3')
o.func()

mod(o)

o.func()
    

from PIL import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QPointF

def f1(a : int):
    print(a)
    
def f2(b:float):
    print(b, type(b))
    
f1(2); f2(2)

QtGui.QScreen