import os
import pathlib
import tkinter
from tkinter import Canvas, Frame, PhotoImage, Toplevel, Label
from tkinter.constants import BOTH, LEFT, TOP, X
from PIL import Image, ImageTk
from datetime import datetime
from snapshot import Snapshot
folder = configDir = os.path.join(os.getenv("appdata"),
                                  "screenCap")


class Recylcer:

    size = 0
    thumbnails = []
    filePaths = []
    main = None
    frameSize = (0, 0)

    def initialize(cls, size, main: tkinter.Tk):
        cls.size = size
        cls.main = main
        cls.frameSize = (cls.main.winfo_screenwidth()/7,
                         cls.main.winfo_screenheight()/7)
        cls.loadThumbs()

    # returns PhotoImage
    def loadThumbs(cls):

        paths = sorted(pathlib.Path().iterdir(), key=os.path.getmtime)

        # remove any non image paths
        for path in paths:
            if paths[-4:] != ".png":
                paths.remove(path)

        if set(cls.filePaths) != set(paths):
            # remove extra images
            if len(cls.filePaths) > cls.size:
                for i in range(len(cls.filePaths)-1, cls.size - 1, -1):
                    os.remove(cls.filePaths[i])
                    cls.filePaths.pop(i)

            for path in cls.filePaths:
                image = Image.open(path)
                scale = max(cls.frameSize[0]/image.width,
                            cls.frameSize[1]/image.height)
                image = image.resize(
                    [image.width * scale, image.height * scale])
                cls.thumbnails.append(ImageTk.PhotoImage(image))

    # expecting pillow image
    def addImage(cls, image: Image):
        path = os.path.join(folder, datetime.now().strftime(
            "%d-%m-%y_%-H-%-M-%-S"+".png"))
        image.save(path)
        cls.filePaths.insert(0, path)
        cls.thumbnails.insert(0, ImageTk.PhotoImage(
            image.resize(cls.frameSize[0], cls.frameSize[1])))

        if len(path) > cls.size:
            os.remove(path[-1])
            cls.filePaths.pop(-1)
            cls.thumbnails.pop(-1)

    def show(cls):
        window = Toplevel(cls.main)
        canvas = Canvas(window)
        canvas.pack(side=TOP, expand=True, fill=X)
        window.geometry()
        pass

    def max(a, b):
        return a if a > b else b


class ImageFrame(Frame):

    def __init__(self, image: PhotoImage, main, filePath, *args, **kwargs):
        super(ImageFrame, self).__init__(*args, **kwargs)
        self.image = image
        self.filePath = filePath
        self.main = main
        Label(self, image=self.image).pack(side=LEFT, padx=(5,0), pady=(5,0))
        Label(self, text=f'''{os.path.basename(self.filePath)}
              \n{self.image.width()}x{self.image.height()}
              \n{os.path.getsize(self.filePath)}''').pack(side=LEFT, padx=(5,5), pady=(0,5))
        self.pack(fill=BOTH, expand=True)
        
        def show(image, main):
            Snapshot(master=main).fromImage(image)
        self.bind("<Button-1>", lambda event:show(self.image, self.main))