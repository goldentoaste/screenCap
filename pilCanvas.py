import tkinter as tk
from tkinter.constants import BOTH, NONE, YES

from PIL import ImageDraw, ImageTk, Image
import sys
from os import path


class PilCanvas(tk.Frame):
    def __init__(self, borderThickness=0, *args, **kwargs):

        super(PilCanvas, self).__init__(*args, **kwargs)
        self.originalImage: Image.Image = None
        self.backgroundImage: Image.Image = None
        self.linesLayer: Image.Image = None
        self.photoImage = None
        self.tempLineLayer = None
        self.drawingRef = None
        self.tempDrawingRef = None
        self.borderThickness = borderThickness

        self.lines = []
        self.scale = 1

        self.imageContainer = tk.Label(self)
        self.imageContainer.pack(fill=BOTH, expand=YES)

        # self.imageContainer.bind(
        #     "<B1-Motion>", lambda event: self.drawRect((100, 100), (event.x, event.y))
        # )
        # self.imageContainer.bind("<ButtonRelease-1>", lambda event: self.redrawLine())

        self.imageContainer.bind(
            "<Button-1>", lambda event: self.newLine((event.x, event.y), "#ffffff")
        )
        self.imageContainer.bind(
            "<B1-Motion>", lambda event: self.addLineSeg((event.x, event.y))
        )
        self.imageContainer.bind(
            "<ButtonRelease-1>",
            lambda event: ("self.smoothLine(-1, 1)", self.drawAntiAliasLine(-1)),
        )

        self.imageContainer.bind(
            "<Button-3>", lambda event: self.setScale(self.scale + 0.2)
        )
        self.imageContainer.bind("<Button-3>", lambda event: self.undo())
        self.imageContainer.bind(
            "<Button-3>", lambda event: self.crop((100, 100), (200, 200))
        )

    def setBackground(self, newImage):
        self.backgroundImage = newImage
        self.originalImage = newImage
        self.linesLayer = Image.new("RGBA", newImage.size)
        self.drawingRef = ImageDraw.Draw(self.linesLayer)
        self.photoImage = ImageTk.PhotoImage(self.backgroundImage)
        self.imageContainer.configure(image=self.photoImage)

    def drawRect(self, start, end):

        rectLayer = Image.new("RGBA", self.linesLayer.size)
        rectDraw = ImageDraw.Draw(rectLayer)

        x1 = end[0]
        y1 = end[1]

        x0 = start[0]
        y0 = start[1]

        rectDraw.rectangle([start, end], fill="#00000080")

        rectDraw.line((x0, y0, x1, y0, x1, y1, x0, y1, x0, y0), fill="#ffffff", width=1)

        displayImage = self.backgroundImage.copy()
        displayImage = Image.alpha_composite(displayImage, self.linesLayer)
        displayImage = Image.alpha_composite(displayImage, rectLayer)
        self.photoImage = ImageTk.PhotoImage(displayImage)
        self.imageContainer.configure(image=self.photoImage)

    def drawLine(self):
        displayImage = self.backgroundImage.copy()
        displayImage = Image.alpha_composite(displayImage, self.linesLayer)
        if self.tempLineLayer is not None:
            displayImage = Image.alpha_composite(displayImage, self.tempLineLayer)
        self.photoImage = ImageTk.PhotoImage(displayImage)
        self.imageContainer.configure(image=self.photoImage)

    def newLine(self, start, color):
        self.lines.append([self.scale, color, start[0], start[1]])
        self.tempLineLayer = Image.new("RGBA", self.backgroundImage.size)
        self.tempDrawingRef = ImageDraw.Draw(self.tempLineLayer)

    def addLineSeg(self, pos):
        lastLine = self.lines[-1]
        lastPoint = (lastLine[-2], lastLine[-1])
        color = lastLine[1]
        lastLine.extend(pos)
        self.tempDrawingRef.line((pos, lastPoint), fill=color, width=2)
        self.drawLine()

    def smoothLine(self, index, amount):
        length = len(self.lines[index])
        line = self.lines[index]
        if length == 4:
            return None
        for i in range(2, length, 2):
            start = max(i - amount * 2, 2)
            end = min(i + amount * 2, length - 2)

            xSum = 0
            ySum = 0

            for j in range(start, end, 2):
                xSum += line[j]
                ySum += line[j + 1]

            line[i] = xSum * 2 / (end - start)
            line[i + 1] = ySum * 2 / (end - start)

    def drawAntiAliasLine(self, index):
        if self.tempLineLayer is not None:
            self.tempDrawingRef = None
            self.tempLineLayer.close()
            self.tempLineLayer = None

        superSample = Image.new(
            "RGBA", tuple([2 * dim for dim in self.linesLayer.size])
        )
        superSampleDraw = ImageDraw.Draw(superSample)

        r = [self.lines[index]] if index != "all" else self.lines

        for line in r:
            superSampleDraw.line(
                [2 * p for p in line[2:]],
                fill=line[1],
                width=4,
            )
        superSample = superSample.resize(self.linesLayer.size, resample=Image.ANTIALIAS)

        self.linesLayer.alpha_composite(superSample, (0, 0), (0, 0))

        self.drawLine()

    def setScale(self, newScale):
        if (
            self.linesLayer.size[0] * newScale > self.winfo_screenwidth()
            or self.linesLayer.size[1] * newScale > self.winfo_screenheight()
            or newScale < 0.2
        ):
            return None

        self.scale = newScale

        self.backgroundImage = self.originalImage.copy().resize(
            (
                int(self.originalImage.width * newScale),
                int(self.originalImage.height * newScale),
            ),
        )
        self.linesLayer = Image.new("RGBA", self.backgroundImage.size)

        for line in self.lines:
            oldScale = line[0]
            line[:] = [newScale, line[1]] + [
                point * newScale / oldScale for point in line[2:]
            ]

        self.drawAntiAliasLine("all")
        self.drawLine()

    def undo(self):
        if not self.lines:
            return None
        self.lines.pop()

        self.linesLayer = Image.new("RGBA", self.backgroundImage.size)
        self.drawAntiAliasLine("all")
        self.drawLine()

    def clear(self):

        self.linesLayer = Image.new("RGBA", self.linesLayer.size)
        self.drawingRef = ImageDraw.Draw(self.linesLayer)
        self.drawLine()

    def crop(self, start, end):
        """
        start is upper right corner
        """
        start = (start[0] / self.scale, start[1] / self.scale)
        end = (end[0] / self.scale, end[1] / self.scale)
        self.originalImage = self.originalImage.crop(list(start) + list(end))
        self.backgroundImage = self.originalImage.copy().resize(
            (
                self.originalImage.width * self.scale,
                self.originalImage.height * self.scale,
            ),
            resample=Image.ANTIALIAS,
        )

        startx = start[0]
        starty = start[1]
        dx = end[0] - startx
        dy = end[1] - starty

        for line in self.lines:
            line[:] = line[:2] + [
                p - startx if index % 2 == 0 else p - starty
                for index, p in enumerate(line[2:], start=0)
            ]

        # I give up trying to optimize
        # for line in self.lines:
        #     for i in range(len(line) - 4, 1, -2):
        #         x0 = line[i] - startx
        #         y0 = line[i + 1] - starty
        #         x1 = line[i + 2] - startx
        #         y1 = line[i + 3] - starty

        #         if all(
        #             (
        #                 x0 < 0 or x0 > dx,
        #                 y0 < 0 or y0 > dy,
        #                 x1 < 0 or x1 > dx,
        #                 y1 < 0 or y1 > dy,
        #             )
        #         ):
        #             line.pop()
        #             line.pop()
        #         else:
        #             line[i + 2] = x1
        #             line[i + 3] = y1

        #     if len(line) == 4:
        #         self.lines.remove(line)
        #     else:
        #         line[2] -= startx
        #         line[3] -= starty

        self.linesLayer = Image.new("RGBA", self.backgroundImage.size)
        self.drawAntiAliasLine("all")
        self.drawLine()

    def exit(self):
        if self.originalImage is not None:
            self.originalImage.close()

        if self.backgroundImage is not None:
            self.backgroundImage.close()

        if self.tempLineLayer is not None:
            self.tempLineLayer.close()

        if self.linesLayer is not None:
            self.linesLayer.close()

        self.destroy()


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = PilCanvas(master=root)
    app.pack(fill=BOTH, expand=YES)
    app.setBackground(Image.open(resource_path("devineInspiration.png")))
    root.mainloop()
