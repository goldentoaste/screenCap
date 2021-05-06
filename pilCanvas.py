import tkinter as tk
from tkinter.constants import BOTH, YES

from PIL import ImageDraw, ImageTk, Image


class PilCanvas(tk.Frame):
    def __init__(self, borderThickness=0, *args, **kwargs):

        super(PilCanvas, self).__init__(*args, **kwargs)

        self.backgroundImage: Image.Image = None
        self.currentImage: Image.Image = None
        self.photoImage = None

        self.drawingRef = None
        self.borderThickness = borderThickness

        self.lines = []
        self.scale = 1
        self.rectPoints = []

        self.imageContainer = tk.Label(self)
        self.imageContainer.pack(fill=BOTH, expand=YES)

        self.imageContainer.bind(
            "<B1-Motion>", lambda event: self.drawRect((100, 100), (event.x, event.y))
        )

    def setBackground(self, newImage):
        self.backgroundImage = newImage
        self.currentImage = newImage.copy()
        self.drawingRef = ImageDraw.Draw(self.currentImage)
        self.redrawAll()

    def drawRect(self, start, end):
        
        rectLayer = Image.new("RGBA", self.currentImage.size)
        rectDraw = ImageDraw.Draw(rectLayer)
        rectDraw.rectangle([start, end], fill="#ffffff")
        displayImage = self.currentImage.copy()
        displayImage.paste(rectLayer, (0, 0), rectLayer)
        self.photoImage = ImageTk.PhotoImage(displayImage)
        self.imageContainer.configure(image=self.photoImage)
        

    def clearShapes(self):
        self.imageContainer.configure(image=ImageTk.PhotoImage(self.currentImage))

    def redrawAll(self):
        self.photoImage = ImageTk.PhotoImage(self.currentImage)
        self.imageContainer.configure(image=self.photoImage)


if __name__ == "__main__":
    root = tk.Tk()

    app = PilCanvas(master=root)
    app.pack(fill=BOTH, expand=YES)
    app.setBackground(Image.open("devineInspiration.png"))
    root.mainloop()