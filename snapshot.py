

from tkinter import Canvas, Label, Toplevel, PhotoImage
from tkinter.constants import BOTH, NW, YES
from PIL import Image, ImageGrab, ImageTk
import sys
from os import path
from PIL.ImageFilter import BoxBlur
from time import time
#ImageGrab.grab().save("stuff.jpg", format="JPEG", quality = 100, subsampling=0)
# use this when saving jpg!!!


class Snapshot(Toplevel):

    def __init__(self, *args, **kwargs):
        super(Snapshot, self).__init__(*args, **kwargs)

    ''' 
    __initialize is to be called after self.image has been set(keeping the reference is neccessary)
    '''

    def __initialize(self, size=(400, 400), *args, **kwargs):

        self.geometry("+0+0")
        # canvas stuff
        self.canvas = Canvas(
            self, width=size[0], height=size[1], highlightthickness=1)  # highlightthickness=0 for no border
        self.canvas.pack(expand=YES, fill=BOTH)
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        # init to None for now since canvas.delete(None) is okay.
        self.rectangle = None

        # window stuff
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.focus_force()

        # indicate if its the first crop from fullscreen, then esc should close the snapshot instead
        # of just stopping crop
        self.initialCrop = False
        self.cropping = False

        # pos variables for tracking mouse postions
        self.startPos = (0, 0)
        self.mousePos = (0, 0)
        self.windowPos = (0, 0)
        self.prevPos = (0, 0)
        self.mini = False
        # move lock is used to fix a behaviour when double clicking and drag is happening at the same time
        self.moveLock = False

        self.clickTime = 0
        # press esc to close the snap or to quit cropping

        self.bind("<Escape>", lambda event: self.__exit())

        # settings up mouse event listener
        self.bind("<B1-Motion>", self.__mouseDrag)
        self.bind("<Button-1>", self.__mouseDown)
        self.bind("<ButtonRelease-1>", self.__mouseUp)
        self.bind("<Button-3>", self.__mouseRight)
        self.bind("<Double-Button-1>", self.__mouseDouble)

        # setup right click menuItem

    def fromImage(self):
        self.firstCrop = False
        pass

    def fromFullScreen(self, *args, **kwargs):
        self.pilImage = ImageGrab.grab(())
        self.image = ImageTk.PhotoImage(self.pilImage)
        self.firstCrop = True
        self.__initialize(
            (self.winfo_screenwidth(), self.winfo_screenheight()), *args, **kwargs)
        self.__crop()

    def __exit(self):
        if (self.firstCrop and self.cropping) or (
                not self.firstCrop and not self.cropping):
            self.destroy()

        else:
            print("stopping")
            self.__stopCrop()

    def __crop(self):
        self.cropping = True
        self.configure(
            cursor='\"@'+self.resource_path('bread.cur').replace("\\", '/')+"\"")

    def __stopCrop(self):
        self.cropping = False
        self.firstCrop = False
        self['cursor'] = ""

    def __mouseDown(self, event):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        self.mousePos = (event.x, event.y)
        self.windowPos = (self.winfo_x(), self.winfo_y())
        if self.cropping:
            self.startPos = (event.x, event.y)

    def __mouseDrag(self, event):
        if self.cropping:
            self.canvas.delete(self.rectangle)
            self.rectangle = self.canvas.create_rectangle(
                self.startPos[0],
                self.startPos[1],
                event.x, event.y,
                outline="white",
                fill="black", stipple='gray50'
            )
        elif not self.moveLock:
            dx = event.x - self.mousePos[0]
            dy = event.y - self.mousePos[1]
            self.windowPos = (self.windowPos[0] + dx,
                              self.windowPos[1] + dy)
            self.prevPos = (self.prevPos[0] + dx,
                            self.prevPos[1] + dy)
            self.geometry(
                f"+{self.windowPos[0]}+{self.windowPos[1]}")

    def __mouseUp(self, event):
        self.moveLock = False
        if self.cropping:
            self.canvas.delete(self.rectangle)
            self.__stopCrop()
            self.pilImage = self.pilImage.crop(
                [self.startPos[0], self.startPos[1], event.x, event.y])
            self.image = ImageTk.PhotoImage(self.pilImage)
            self.canvas.delete('all')
            self.canvas.configure(width=self.pilImage.width,
                                  height=self.pilImage.height)
            self.canvas.create_image(0, 0, anchor=NW, image=self.image)
            self.geometry(f"+{self.startPos[0]}+{self.startPos[1]}")

    def __mouseRight(self, event):
        pass

    def __mouseDouble(self, event):
        self.moveLock = True

        def min(a, b):
            return a if a < b else b

        if not self.mini:

            x = max(0, event.x - 50)
            y = max(0, event.y - 50)

            tempImage = self.pilImage.filter(BoxBlur(4)).crop(
                [x,
                 y,
                 min(self.pilImage.width, x + 100),
                 min(self.pilImage.height, y + 100)])
            self.prevPos = (self.winfo_x(), self.winfo_y())
            self.__updateImage(tempImage)
            self.geometry(
                f"+{self.prevPos[0] + max(0, event.x - 50) }+{self.prevPos[1] + max(0, event.y - 50)}")
            self.mini = True

        else:
            self.__updateImage(self.pilImage)
            self.geometry(f"+{self.prevPos[0]}+{self.prevPos[1]}")
            self.mini = False

    def __updateImage(self, image):
        self.canvas.delete('all')
        self.canvas.configure(width=image.width, height=image.height)
        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")
        return path.join(base_path, relative_path)
