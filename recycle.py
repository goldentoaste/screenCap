import os
import pathlib
from pathlib import Path
from tkinter import Canvas, Frame, PhotoImage, Toplevel, Label

from tkinter.constants import BOTH, END, LEFT, TOP, X
from PIL import Image, ImageTk
from datetime import datetime
from snapshot import Snapshot
import gc

folder = configDir = os.path.join(os.getenv("appdata"), "screenCap")
kbCons = 1024


class RecycleBin:
    def __init__(self, size, mainWindow):
        self.size = size
        self.mainWindow = mainWindow
        self.main = mainWindow.main
        self.windowOpen = False
        self.frameSize = (
            int(self.main.winfo_screenwidth() / 6),
            int(self.main.winfo_screenheight() / 5),
        )
        self.filePaths = []
        self.thumbnails = []
        self.hashes = set()

        self.loadThumbs(loadImage=False)

    # returns PhotoImage

    def loadThumbs(self, loadImage=True):
        paths = sorted(pathlib.Path(folder).glob("*.png"), key=lambda x: -os.path.getmtime(x))

        # remove extra images
        if len(paths) > self.size:
            for i in range(len(paths) - 1, self.size - 1, -1):
                os.remove(paths[i])
                paths.pop(i)

        self.filePaths = paths
        self.hashes = {p.name for p in paths}
        self.thumbnails.clear()
        if loadImage:
            for path in self.filePaths:
                image = Image.open(path)
                scale = min(self.frameSize[0] / image.width, self.frameSize[1] / image.height)
                pimage = ImageTk.PhotoImage(image.resize([int(image.width * scale), int(image.height * scale)]))
                self.thumbnails.append(pimage)
                image.close()
        else:
            self.thumbnails = [None for _ in range(len(self.filePaths))]

    # expecting pillow image
    def addImage(self, image: Image, name=None):

        index = 0
        oldPath = None
        for i, p in enumerate(self.filePaths):
            if p.name == name:
                index = i
                oldPath = p
                break
        if oldPath is not None and name != None and name in self.hashes:
            self.hashes.remove(name)
            oldPath = oldPath.rename(oldPath.with_name(datetime.now().strftime("%d%m%y_%H-%M-%S-%f") + ".png"))
            self.filePaths.pop(index)
            self.thumbnails.pop(index)
            scale = min(self.frameSize[0] / image.width, self.frameSize[1] / image.height)
            self.filePaths.insert(0, oldPath)
            self.thumbnails.insert(
                0, ImageTk.PhotoImage(image.resize([int(image.width * scale), int(image.height * scale)]))
            )
            self.hashes.add(oldPath.name)
        else:
            path = os.path.join(folder, datetime.now().strftime("%d%m%y_%H-%M-%S-%f") + ".png")
            image.save(path)
            self.filePaths.insert(0, Path(path))
            self.hashes.add(os.path.basename(path))
            scale = min(self.frameSize[0] / image.width, self.frameSize[1] / image.height)
            pImage = ImageTk.PhotoImage(image.resize([int(image.width * scale), int(image.height * scale)]))

            self.thumbnails.insert(0, pImage)

            if len(self.filePaths) > self.size:
                self.thumbnails.pop(-1)
                os.remove(self.filePaths[-1])
                self.hashes.remove(self.filePaths[-1].name)
                self.filePaths.pop(-1)

        if self.windowOpen:
            for f in self.mainFrame.winfo_children():
                f.destroy()
                del f
            self.mainFrame.update()
            self.populate()

    def show(self):
        self.loadThumbs(loadImage=True)
        self.windowOpen = True
        self.window = Toplevel(self.mainWindow.main)
        self.window.title("Recycling Bin")

        def exit():
            self.windowOpen = False
            self.window.destroy()
            self.filePaths.clear()
            self.thumbnails.clear()
            gc.collect()

        self.window.protocol("WM_DELETE_WINDOW", lambda: exit())
        self.canvas = Canvas(
            self.window,
            width=self.frameSize[0],
            height=(4 * self.frameSize[1]),
            borderwidth=0,
        )
        self.mainFrame = Frame(self.canvas)
        self.window.bind(
            "<MouseWheel>",
            lambda event: self.canvas.yview_scroll(-1 * (event.delta // 120), "units"),
        )

        # self.window.resizable(False, False)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.mainFrame, anchor="nw")

        self.mainFrame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.populate()

    def populate(self):
        maxWidth = 0
        for i in range(len(self.filePaths)):
            f = ImageFrame(self.thumbnails[i], self.mainWindow, self.filePaths[i], self.mainFrame)
            f.pack(side="top")
            temp = f.img.winfo_reqwidth() + f.text.winfo_reqwidth() + 20
            if temp > maxWidth:
                maxWidth = temp
        self.mainFrame.update()
        self.canvas.configure(width=maxWidth)
        self.canvas.update()
        self.window.focus_force()


class ImageFrame(Frame):
    def __init__(self, image: PhotoImage, mainWindow, filePath: Path, *args, **kwargs):
        self.image = image
        self.filePath = filePath
        self.mainWindow = mainWindow
        self.pilImage = Image.open(self.filePath)
        super(ImageFrame, self).__init__(*args, **kwargs)
        self.img = Label(self, image=self.image)
        self.img.pack(side=LEFT)
        self.text = Label(
            self,
            text=f"""{datetime.fromtimestamp(os.path.getmtime(self.filePath)).strftime('%b.%d.%Y %I:%M|%p')}
            {self.pilImage.width}x{self.pilImage.height}
            {'%.2f' % (os.path.getsize(self.filePath)/kbCons)}kb""",
        )
        self.text.pack(side=LEFT, padx=10)
        self.pilImage.close()

        def show(path: Path):
            
            Snapshot(mainWindow=self.mainWindow).fromImage(Image.open(path), path.name)

        self.img.bind("<Button-1>", lambda event: show(self.filePath))
        self.text.bind("<Button-1>", lambda event: show(self.filePath))
        self.bind("<Button-1>", lambda event: show(self.filePath))
