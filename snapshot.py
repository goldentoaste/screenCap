

from tkinter import Canvas, Menu, Toplevel, PhotoImage, filedialog, messagebox
from tkinter.constants import BOTH, NW, YES
from PIL import Image, ImageGrab, ImageTk
import sys
from os import path
from PIL.ImageFilter import GaussianBlur
import gc
import io
import win32clipboard as clipboard
from desktopmagic.screengrab_win32 import getDisplayRects, getRectAsImage

#ImageGrab.grab().save("stuff.jpg", format="JPEG", quality = 100, subsampling=0)
# use this when saving jpg!!!


class Snapshot(Toplevel):

    def __init__(self, master, *args, **kwargs):
        self.master = master
        super(Snapshot, self).__init__(*args, **kwargs)

    ''' 
    __initialize is to be called after self.image has been set(keeping the reference is neccessary)
    '''

    def __initialize(self, size=(400, 400), *args, **kwargs):

        self.bread = ImageTk.PhotoImage(Image.open("bread.png"))
        bound = self.__getBoundBox()
        self.geometry(f"+{bound[0]}+{bound[1]}")
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

        # for resizing
        self.scale = 1

        # press esc to close the snap or to quit cropping

        self.bind("<Escape>", lambda event: self.__exit())

        # settings up mouse event listener
        self.bind("<B1-Motion>", self.__mouseDrag)
        self.bind("<Button-1>", self.__mouseDown)
        self.bind("<ButtonRelease-1>", self.__mouseUp)
        self.bind("<ButtonRelease-3>", self.__mouseRight)
        self.bind("<Double-Button-1>", self.__mouseDouble)

        # keyboard short bindings
        self.bind("<Control-c>", lambda event: self.__copy())
        self.bind("<Control-x>", lambda event: self.__cut())
        self.bind("<Control-s>", lambda event: self.__save())

        # size Control
        self.bind("<=>", lambda event: self.__enlarge())
        self.bind("-", lambda event: self.__shrink())
        # setup right click menuItem
        self.rightMenu = Menu(self, tearoff=0)
        self.rightMenu.add_command(
            label="Close", font=("", 11), command=self.__exit)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(
            label="Save", font=("", 11), command=self.__save)
        self.rightMenu.add_command(
            label="Copy", font=("", 11), command=self.__copy)
        self.rightMenu.add_command(
            label="Cut", font=("", 11), command=self.__cut)
        self.rightMenu.add_command(
            label="Paste", font=("", 11), command=self.__paste)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(
            label="Enlarge", font=("", 11), command=self.__enlarge)
        self.rightMenu.add_command(
            label="Shrink", font=("", 11), command=self.__shrink)
        self.rightMenu.add_command(
            label="Reset", font=("", 11), command=self.__resetSize)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(
            label="Crop", font=("", 11), command=self.__crop)

    def __paste(self):
        image = ImageGrab.grabclipboard()
        if image:
            Snapshot(master=self.master).fromImage(image=image)

    def __resetSize(self):
        self.scale = 1
        self.__resize()

    def __shrink(self):
        self.scale = max(0, self.scale - 0.20)
        self.__resize()

    def __enlarge(self):
        self.scale = min(2, self.scale + 0.20)
        self.__resize()

    def __resize(self):
        image = self.pilImage.copy().resize(
            (int(self.pilImage.width * self.scale), int(self.pilImage.height * self.scale)), Image.ANTIALIAS)
        self.__updateImage(image)

    def __cut(self):
        self.__copy()
        self.__exit()

    def __save(self):
        # do double click action to get image out of the way
        self.withdraw()
        file = filedialog.asksaveasfilename(initialdir="/", title="Save image", defaultextension="*.*", filetypes=(
            ("jpeg image", "*.jpg"), ("png image", "*.png")))

        if file is not None:
            path = str(file)
            # file type check
            fType = path[-4:]

            if fType == ".jpg":
                self.pilImage.save(path, format="JPEG",
                                   quality=100, subsampling=0)
            elif fType == ".png":
                self.pilImage.save(path, format="PNG")
            else:
                messagebox.showerror(title="File type not supported!",
                                     text="The requested file type is not supported, only jpg and png is supported")
        self.deiconify()

    def __copy(self):
        output = io.BytesIO()
        self.pilImage.save(output, "BMP")
        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(clipboard.CF_DIB, output.getvalue()[14:])
        clipboard.CloseClipboard()
        output.close()

    # this 'image' should be a pillow image
    def fromImage(self, image, *args, **kwargs):
        self.firstCrop = False
        self.pilImage = image
        self.image = ImageTk.PhotoImage(self.pilImage)
        self.__initialize((self.pilImage.width,
                           self.pilImage.height), *args, **kwargs)

    def __getBoundBox(self):
        bounds = getDisplayRects()
        x = self.winfo_pointerx()
        y = self.winfo_pointery()

        for bound in bounds:
            if x >= bound[0] and y >= bound[1] and x <= bound[2] and y <= bound[3]:
                return bound
        return bounds[0]

    def fromFullScreen(self, *args, **kwargs):

        self.pilImage = getRectAsImage(self.__getBoundBox())
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
            self.__stopCrop()
        gc.collect()

    def __crop(self):
        self.cropping = True
        self.__resetSize()
        self.configure(
            cursor='\"@'+self.resource_path('bread.cur').replace("\\", '/')+"\"")

    def __stopCrop(self):
        self.cropping = False
        self.firstCrop = False
        self['cursor'] = ""
        if self.pilImage.width < 5 or self.pilImage.height < 5:
            self.__exit()

    def __mouseDown(self, event):
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
            self.pilImage = self.pilImage.crop(
                [self.startPos[0], self.startPos[1], event.x, event.y])
            self.image = ImageTk.PhotoImage(self.pilImage)
            self.canvas.delete('all')
            self.canvas.configure(width=self.pilImage.width,
                                  height=self.pilImage.height)
            self.canvas.create_image(0, 0, anchor=NW, image=self.image)
            self.geometry(
                f"+{self.startPos[0] + self.winfo_x()}+{self.startPos[1] + self.winfo_y()}")
            self.__stopCrop()

    def __mouseRight(self, event):
        self.rightMenu.tk_popup(event.x_root, event.y_root, 0)
        self.rightMenu.grab_release()

    def __mouseDouble(self, event):
        self.moveLock = True
        if not self.mini:
            cropSize = min(min(self.winfo_screenheight()/10, self.pilImage.width),
                           min(self.winfo_screenheight()/10, self.pilImage.height))
            halfCrop = cropSize / 2

            x = int(min(max(0, event.x - halfCrop),
                        self.pilImage.width - cropSize))
            y = int(min(max(0, event.y - halfCrop),
                        self.pilImage.height - cropSize))

            tempImage = self.pilImage.filter(GaussianBlur(3)).crop(
                [x,
                 y,
                 min(self.pilImage.width, x + cropSize),
                 min(self.pilImage.height, y + cropSize)])
            self.prevPos = (self.winfo_x(), self.winfo_y())
            self.__updateImage(tempImage)
            self.geometry(
                f"+{self.prevPos[0] + x }+{self.prevPos[1] + y}")
            self.mini = True

        else:
            self.__updateImage(self.pilImage)
            self.geometry(f"+{self.prevPos[0]}+{self.prevPos[1]}")
            self.mini = False
            # self.__resize()

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

    def min(a, b):
        return a if a < b else b

    def max(a, b):
        return a if a > b else b
