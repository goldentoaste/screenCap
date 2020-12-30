

from tkinter import Canvas, Label, Toplevel, PhotoImage
from tkinter.constants import BOTH, NW, YES
from PIL import Image, ImageGrab, ImageTk
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
            self, width=size[0], height=size[1], highlightthickness=0)
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
        # press esc to close the snap or to quit cropping

        self.bind("<Escape>", lambda event: self.__exit)

        # settings up mouse event listener
        self.bind("<B1-Motion>", self.__mouseDrag)
        self.bind("<Button-1>", self.__mouseDown)
        self.bind("<ButtonRelease-1>", self.__mouseUp)
        self.bind("<Button-3>", self.__mouseRight)
        self.bind("<Double-Button-1>", self.__mouseDouble)

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
            del self
        else:
            self.__stopCrop()

    def __crop(self):
        self.cropping = True
        self['cursor'] = "@bread.cur"

    def __stopCrop(self):
        self.cropping = False
        self.firstCrop = False
        self['cursor'] = ""

    def __mouseDown(self, event):
        if self.cropping:
            self.startPos = (event.x, event.y)

    def __mouseDrag(self, event):
        if self.cropping:
            self.canvas.delete(self.rectangle)
            self.rectangle = self.canvas.create_rectangle(
                self.startPos[0],
                self.startPos[1],
                event.x, event.y,
                outline="white"
            )

    def __mouseUp(self, event):
        if self.cropping:
            self.canvas.delete(self.rectangle)

    def __mouseRight(self, event):
        pass

    def __mouseDouble(self, event):
        pass
