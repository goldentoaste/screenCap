

from tkinter import Canvas, Label, Toplevel, PhotoImage
from tkinter.constants import BOTH, NW
from PIL import Image, ImageGrab, ImageTk
#ImageGrab.grab().save("stuff.jpg", format="JPEG", quality = 100, subsampling=0)
# use this when saving jpg!!!


class Snapshot(Toplevel):

    def __init__(self, *args, **kwargs):
        super(Snapshot, self).__init__(*args, **kwargs)
        self.image = ImageGrab.grab((100, 100, 200, 200))

        self.geometry("400x400")
        self.testLabel = Label(
            self, image=ImageTk.PhotoImage(Image.open("bread.png")))
        # self.canvas = Canvas(self, width=300, height=300)
        # self.canvas.grid(row = 0, column = 0)

        # self.canvas.create_image(
        #     10, 10, image=ImageTk.PhotoImage(Image.open("stuff.jpg")), anchor=NW)
        # self.canvas.update()
