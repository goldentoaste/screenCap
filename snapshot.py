import os
from tkinter import (
    BooleanVar,
    Canvas,
    Checkbutton,
    Frame,
    Menu,
    Toplevel,
    filedialog,
)
import tkinter
from colorPicker import ColorChooser
from tkinter.constants import BOTH, NW, TOP, YES
from PIL import Image, ImageGrab, ImageTk
import sys
from os import path
from PIL.ImageFilter import GaussianBlur
import gc
import io
import win32clipboard as clipboard
from desktopmagic.screengrab_win32 import getDisplayRects, getRectAsImage
import time
import ctypes
import tkinter.simpledialog
import win32gui


shcore = ctypes.windll.shcore
# auto dpi aware scalings
shcore.SetProcessDpiAwareness(2)


class Snapshot(Toplevel):
    def __init__(self, mainWindow, *args, **kwargs):
        self.mainWindow = mainWindow

    """ 
    __initialize is to be called after self.image has been set(keeping the reference is neccessary)
    """

    def __initialize(self, size=(400, 400), *args, **kwargs):
        # canvas stuff
        self.canvas = Canvas(
            self, width=size[0], height=size[1], highlightthickness=1
        )  # highlightthickness=0 for no border
        self.canvas.pack(expand=YES, fill=BOTH)
        self.canvasImageRef = self.canvas.create_image(0, 0, anchor=NW, image=self.image, tags="image")
        # init to None for now since canvas.delete(None) is okay.
        self.rectangle = None

        # window stuff
        self.attributes("-topmost", True)

        self.update_idletasks()
        self.overrideredirect(True)

        self.resizable(True, True)

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

        self.drawing = False
        self.colorPoint = None
        self.lineCords = []
        self.lineRefs = []
        self.tempLineSegments = []
        self.drawingColor = self.mainWindow.lastColor.get()

        self.modDown = False

        self.opacity = 1
        self.scale = 1

        # press esc to close the snap or to quit cropping
        self.bind("<Escape>", lambda event: self.__exit())

        self.bind("<KeyPress>", self.keyDown)
        self.bind("<KeyRelease>", self.keyUp)

        # settings up mouse event listener
        self.bind("<Motion>", self.__mouseMove)
        self.bind("<B1-Motion>", self.__mouseDrag)
        self.bind("<Button-1>", self.__mouseDown)
        self.bind("<ButtonRelease-1>", self.__mouseUp)
        self.bind("<ButtonRelease-3>", self.__mouseRight)
        self.bind("<Double-Button-1>", self.__mouseDouble)

        # keyboard short bindings
        self.bind("<Control-c>", lambda event: self.__copy())
        self.bind("<Control-C>", lambda event: self.__copy())
        self.bind("<Control-x>", lambda event: self.__cut())
        self.bind("<Control-X>", lambda event: self.__cut())
        self.bind("<Control-s>", lambda event: self.__save())
        self.bind("<Control-S>", lambda event: self.__save())
        self.bind(
            "<Control-D>",
            lambda event: self.__draw() if not self.drawing else self.__stopDraw(),
        )
        self.bind(
            "<Control-d>",
            lambda event: self.__draw() if not self.drawing else self.__stopDraw(),
        )
        self.bind("<Control-R>", lambda event: self.__resetSize())
        self.bind("<Control-r>", lambda event: self.__resetSize())
        self.bind("<Control-v>", lambda event: self.__paste())
        self.bind("<Control-V>", lambda event: self.__paste())
        # # size Control
        self.bind("0", lambda event: self.__resetSize())
        self.bind("=", lambda event: self.__enlarge())
        self.bind("-", lambda event: self.__shrink())
        # opacity control
        self.bind("<Control-=>", lambda event: self.__opacityUp())
        self.bind("<Control-minus>", lambda event: self.__opacityDown())
        # setup right click menuItem
        self.rightMenu = Menu(self, tearoff=0)
        self.rightMenu.add_command(label="Close (Esc)", font=("", 11), command=self.__exit)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(label="Save (Ctrl S)", font=("", 11), command=self.__save)
        self.rightMenu.add_command(label="Copy (Ctrl C)", font=("", 11), command=self.__copy)
        self.rightMenu.add_command(label="Cut (Ctrl X)", font=("", 11), command=self.__cut)
        self.rightMenu.add_command(label="Paste (Ctrl V)", font=("", 11), command=self.__paste)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(label="Opacity up (Ctrl +)", font=("", 11), command=self.__opacityUp)
        self.rightMenu.add_command(label="Opacity down (Ctrl -)", font=("", 11), command=self.__opacityDown)

        self.rightMenu.add_separator()
        self.rightMenu.add_command(label="Enlarge (+)", font=("", 11), command=self.__enlarge)
        self.rightMenu.add_command(label="Shrink (-)", font=("", 11), command=self.__shrink)
        self.rightMenu.add_command(label="Reset (0)", font=("", 11), command=self.__resetSize)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(label="Crop", font=("", 11), command=self.__crop)
        self.rightMenu.add_separator()
        self.rightMenu.add_command(
            label="Recycling Bin",
            font=("", 11),
            command=lambda: self.mainWindow.bin.show(),
        )
        self.rightMenu.add_separator()
        self.rightMenu.add_command(label="Draw (Ctrl D)", font=("", 11), command=self.__draw)

    def keyDown(self, event):
        if event.keycode in (17, 16):
            self.modDown = True

    def keyUp(self, event):
        if event.keycode in (17, 16):
            self.modDown = False

    def __opacityUp(self):
        self.opacity = min(1, self.opacity + 0.1)
        self.attributes("-alpha", self.opacity)

    def __opacityDown(self):
        self.opacity = max(0.1, self.opacity - 0.1)
        self.attributes("-alpha", self.opacity)

    def __paste(self):
        image = ImageGrab.grabclipboard()
        if image:
            self.mainWindow.addSnap(Snapshot(mainWindow=self.mainWindow).fromImage(image=image))

    def __resetSize(self):
        self.scale = 1
        self.__resize()

    def __shrink(self):
        self.scale = max(0.2, self.scale - 0.25)
        self.__resize()

    def __enlarge(self):
        self.scale = min(2, self.scale + 0.25)
        self.__resize()

    def __updateImage(self, image):
        self.canvas.configure(width=image.width, height=image.height)
        self.image = ImageTk.PhotoImage(image)
        self.canvas.itemconfig(self.canvasImageRef, image=self.image)

    def __resize(self, override=False):
        image = self.pilImage.copy().resize(
            (
                int(self.pilImage.width * self.scale),
                int(self.pilImage.height * self.scale),
            ),
            Image.Resampling.LANCZOS,
        )

        if override:
            self.pilImage = image
        self.__updateImage(image)

        for line, coordGroup in zip(self.lineRefs, self.lineCords):
            iniScale = coordGroup[0]
            for seg, coords in zip(
                line,
                [
                    (
                        int(coordGroup[i] * self.scale / iniScale),
                        int(coordGroup[i + 1] * self.scale / iniScale),
                        int(coordGroup[i + 2] * self.scale / iniScale),
                        int(coordGroup[i + 3] * self.scale / iniScale),
                    )
                    for i in range(2, len(coordGroup) - 2, 2)
                ],
            ):
                self.canvas.coords(seg, *coords)

    def __cut(self):
        self.__copy()
        self.__exit()

    def __save(self):
        result = None
        if self.scale == 1 and len(self.lineCords) == 0:  # type: ignore
            result = (False, False)
        else:
            dialog = SaveDialog(
                self,
                title="Save options",
                scaled=self.scale != 1,
                drawing=len(self.lineCords) != 0,  # type: ignore
            )
            if not (result := dialog.result):
                return None

        file = filedialog.asksaveasfilename(
            initialdir=self.mainWindow.lastPath.get(),
            initialfile=time.strftime("%d%m%y_%H-%M-%S", time.localtime()),
            title="Save image",
            defaultextension="*.png",
            filetypes=(
                ("png image", "*.png"),
                ("jpeg image", "*.jpg"),
                ("bmp image", "*.bmp"),
            ),
            parent=self,
        )
        image = None

        if result[1]:
            image = getRectAsImage(win32gui.GetWindowRect(self.canvas.winfo_id()))
            if not result[0]:
                image = image.copy().resize(
                    (
                        int(self.pilImage.width / self.scale),
                        int(self.pilImage.height / self.scale),
                    ),
                    Image.Resampling.LANCZOS,
                )

        else:
            if result[0]:
                image = self.pilImage.copy().resize(
                    (
                        int(self.pilImage.width * self.scale),
                        int(self.pilImage.height * self.scale),
                    ),
                    Image.Resampling.LANCZOS,
                )
            else:
                image = self.pilImage

        if file != "":
            path = str(file)
            # file type check
            fType = path[-4:]
            if fType == ".jpg":
                image.save(path, format="JPEG", quality=100, subsampling=0)
            elif fType == ".png":
                image.save(path, format="PNG")
            elif fType == ".bmp":
                image.save(path, format="BMP")
            self.mainWindow.lastPath.set(path)
            self.mainWindow.update("lastpath")

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
        super(Snapshot, self).__init__(*args, **kwargs)
        self.firstCrop = False
        self.pilImage = image
        self.image = ImageTk.PhotoImage(self.pilImage)
        self.__initialize((self.pilImage.width, self.pilImage.height), *args, **kwargs)
        return self

    def __getBoundBox(self):
        bounds: list = getDisplayRects()
        x = self.mainWindow.main.winfo_pointerx()
        y = self.mainWindow.main.winfo_pointery()

        for bound in bounds:
            if x >= bound[0] and y >= bound[1] and x <= bound[2] and y <= bound[3]:
                return bound
        return bounds[0]

    def fromFullScreen(self, *args, **kwargs):
        self.pilImage = getRectAsImage(self.__getBoundBox())
        self.image = ImageTk.PhotoImage(self.pilImage)
        self.firstCrop = True
        super(Snapshot, self).__init__(*args, **kwargs)
        self.__initialize((self.winfo_screenwidth(), self.winfo_screenheight()), *args, **kwargs)
        bound = self.__getBoundBox()
        self.geometry(f"+{bound[0]}+{bound[1]}")
        self.__crop()

        return self

    def __exit(self):
        if (self.firstCrop and self.cropping) or (not self.firstCrop and not self.cropping):
            if self.firstCrop and self.cropping:
                if self in self.mainWindow.snaps:
                    self.mainWindow.snaps.remove(self)
            self.destroy()
            self.mainWindow.removeSnap(self)
            self.pilImage.close()
            del self
            gc.collect()
        else:
            self.__stopCrop()

    def __draw(self):
        self.drawing = True
        self["cursor"] = "tcross"
        self.rightMenu.delete("Draw")
        self.rightMenu.add_command(label="Stop drawing", font=("", 11), command=self.__stopDraw)
        self.rightMenu.add_command(label="Pick color", font=("", 11), command=self.__pickColor)
        self.rightMenu.add_command(label="Clear drawing", font=("", 11), command=self.__clearDrawing)

        def undoLine():
            if len(self.lineRefs) == 0:
                return 0
            self.lineCords.pop(-1)
            if len(self.lineRefs) > 0:
                for line in self.lineRefs.pop(-1):
                    self.canvas.delete(line)

        self.bind("<Control-Z>", lambda event: undoLine())
        self.bind("<Control-z>", lambda event: undoLine())

    def __stopDraw(self):
        self.drawing = False
        self.rightMenu.add_command(label="Draw", font=("", 11), command=self.__draw)
        self["cursor"] = ""
        self.rightMenu.delete("Stop drawing")
        self.rightMenu.delete("Pick color")
        self.rightMenu.delete("Clear drawing")
        self.unbind("<Control-Z>")
        self.unbind("<Control-z>")

    def __clearDrawing(self):
        for line in self.lineRefs:
            for seg in line:
                self.canvas.delete(seg)

        self.lineRefs.clear()
        self.lineCords.clear()

    def __pickColor(self):
        colorchooser = ColorChooser()
        colors = self.mainWindow.custColors.get().split(",")
        colors = colors if colors != [""] else []
        colorCode, custColors = colorchooser.askcolor(
            self.winfo_id(),
            hexToRgb(self.mainWindow.lastColor.get()),
            [hexToRgb(color) for color in colors],
        )

        self.mainWindow.custColors.set(",".join([rgbToHex(rgb) for rgb in custColors]))
        self.mainWindow.update("custColors")

        if not colorCode == None:
            self.drawingColor = rgbToHex(colorCode)
            self.mainWindow.lastColor.set(self.drawingColor)
            self.mainWindow.update("lastColor")

    def __crop(self):
        self.cropping = True
        self.__resetSize()
        self.configure(cursor='"@' + self.resource_path("bread.cur").replace("\\", "/") + '"')

    def __stopCrop(self):
        self.cropping = False
        self.firstCrop = False
        self["cursor"] = ""
        if self.pilImage.width < 20 or self.pilImage.height < 20:
            self.mainWindow.snaps.remove(self)
            self.destroy()

    def __mouseMove(self, event):
        if self.drawing:
            if self.colorPoint != None:
                self.canvas.delete(self.colorPoint)
            self.colorPoint = self.canvas.create_oval(
                event.x - 5,
                event.y - 5,
                event.x + 5,
                event.y + 5,
                fill=self.drawingColor,
            )
        else:
            if self.colorPoint != None:
                self.canvas.delete(self.colorPoint)
                self.colorPoint = None

    def __mouseDown(self, event):
        self.mousePos = (event.x, event.y)
        self.windowPos = (self.winfo_x(), self.winfo_y())
        if self.cropping:
            self.startPos = (event.x, event.y)
        elif self.drawing:
            self.lineCords.append([self.scale, self.drawingColor, event.x, event.y])
            self.lineRefs.append([])

    def __mouseDrag(self, event):
        if self.cropping:
            if not self.rectangle:
                self.rectangle = self.canvas.create_rectangle(
                    self.startPos[0],
                    self.startPos[1],
                    event.x,
                    event.y,
                    outline="white",
                    fill="black",
                    stipple="gray50",
                )
            else:
                x: int = event.x
                y: int = event.y

                if self.modDown:
                    diff = max(abs(x - self.startPos[0]), abs(y - self.startPos[1]))
                    x = self.startPos[0] + diff * (-1 if x < self.startPos[0] else 1)
                    y = self.startPos[1] + diff * (-1 if y < self.startPos[1] else 1)
                self.canvas.coords(
                    self.rectangle,
                    self.startPos[0],
                    self.startPos[1],
                    x,
                    y,
                )
                self.mousePos = (x, y)
        elif self.drawing:
            if self.colorPoint != None:
                self.canvas.delete(self.colorPoint)
            self.lineRefs[-1].append(
                self.canvas.create_line(
                    event.x,
                    event.y,
                    self.mousePos[0],
                    self.mousePos[1],
                    width=2,
                    fill=self.drawingColor,
                )
            )
            self.lineCords[-1].extend(
                [
                    event.x,
                    event.y,
                ]
            )
            self.mousePos = (event.x, event.y)
        elif not self.moveLock:
            dx = event.x - self.mousePos[0]
            dy = event.y - self.mousePos[1]
            self.windowPos = (self.windowPos[0] + dx, self.windowPos[1] + dy)
            self.prevPos = (self.prevPos[0] + dx, self.prevPos[1] + dy)
            self.geometry(f"+{self.windowPos[0]}+{self.windowPos[1]}")

    def __mouseUp(self, event):
        def getCorrectCoord(x1, y1, x2, y2):
            dx = x2 - x1
            dy = y2 - y1
            # true for pos
            table = {
                (True, True): (x1, y1, x2, y2),
                (True, False): (x1, y2, x2, y1),
                (False, True): (x2, y1, x1, y2),
                (False, False): (x2, y2, x1, y1),
            }
            return table[(dx > 0, dy > 0)]

        self.moveLock = False
        if self.cropping:
            self.canvas.delete(self.rectangle)  # type: ignore

            coord = getCorrectCoord(
                self.startPos[0],
                self.startPos[1],
                min(max(self.mousePos[0], 0), self.pilImage.width),
                min(max(self.mousePos[1], 0), self.pilImage.height),
            )

            self.pilImage = self.pilImage.crop(coord)  # using min max to keep coord in bound
            self.image = ImageTk.PhotoImage(self.pilImage)
            self.canvas.configure(width=self.pilImage.width, height=self.pilImage.height)
            self.canvas.itemconfig(self.canvasImageRef, image=self.image)
            self.geometry(f"+{coord[0]+ self.winfo_x()}+{coord[1] + self.winfo_y()}")
            self.__stopCrop()

    def __mouseRight(self, event):
        self.rightMenu.tk_popup(event.x_root, event.y_root, 0)
        self.rightMenu.grab_release()

    def __mouseDouble(self, event):
        self.moveLock = True
        if not self.mini:
            cropSize = min(
                min(self.winfo_screenheight() / 10, self.pilImage.width),
                min(self.winfo_screenheight() / 10, self.pilImage.height),
            )
            halfCrop = cropSize / 2

            x = int(min(max(0, event.x - halfCrop), self.pilImage.width - cropSize))
            y = int(min(max(0, event.y - halfCrop), self.pilImage.height - cropSize))

            tempImage = self.pilImage if self.scale == 1 else ImageTk.getimage(self.image)  # type: ignore
            tempImage = tempImage.filter(GaussianBlur(3)).crop(
                [
                    x,
                    y,
                    min(self.pilImage.width, x + cropSize),
                    min(self.pilImage.height, y + cropSize),  # type: ignore
                ]
            )  # type: ignore
            self.prevPos = (self.winfo_x(), self.winfo_y())
            self.__updateImage(tempImage)
            self.geometry(f"+{self.prevPos[0] + x }+{self.prevPos[1] + y}")
            self.mini = True

        else:
            if self.scale == 1:
                self.__updateImage(self.pilImage)
            else:
                self.__resize()
            self.geometry(f"+{self.prevPos[0]}+{self.prevPos[1]}")
            self.mini = False
            # self.__resize()

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""

        if "__compiled__" in globals():
            base_path = path.join(str(os.getenv("TEMP")), "ONEFILE_SCREENCAP")
        else:
            base_path = path.abspath(".")
        return path.join(str(base_path), relative_path)


def hexToRgb(h: str):
    return (
        int("0x" + h[1:3], base=16),
        int("0x" + h[3:5], base=16),
        int("0x" + h[5:7], base=16),
    )


def rgbToHex(rgb):
    return "#%02x%02x%02x" % rgb


class SaveDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent, title=None, scaled=False, drawing=False):
        self.scaled = scaled
        self.drawing = drawing
        Toplevel.__init__(self, parent)

        self.withdraw()  # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.deiconify()  # become visible now

        self.initial_focus.focus_set()
        self.wm_resizable(False, False)
        self.wait_window(self)

    def body(self, master):
        self.scaleBool = BooleanVar()
        self.drawingBool = BooleanVar()
        self.drawingBool.set(True)
        self.scaleBool.set(True)

        if self.scaled:
            Checkbutton(master, variable=self.scaleBool, text="Save scaled image?").pack(side=TOP, anchor="w", padx=10)

        if self.drawing:
            Checkbutton(master, variable=self.drawingBool, text="Save drawing to image?").pack(
                side=TOP, anchor="w", padx=10
            )

    def apply(self):
        self.result = (self.scaleBool.get(), self.drawingBool.get())
