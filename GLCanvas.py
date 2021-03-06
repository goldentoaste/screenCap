import tkinter
from OpenGL import GL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from pyopengltk import OpenGLFrame
from PIL import Image


class GLCanvas(OpenGLFrame):
    def __init__(self, image, *args, **kwargs):
        super(OpenGLFrame, self).__init__(*args, **kwargs)

        self.image: Image.Image = image

        # self.bind("<B1-Motion>", self.drag)
        # self.bind("<Button-1>", self.click)
        # self.bind("<ButtonRelease-1>", self.release)
        self.lines = []
        # self.bind("<Button-3>", lambda event: (self.lines.pop(-1), print(self.lines)))
        self.texture = None
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.configure(width=self.image.width, height=self.image.height)
        self.scale = 1

    def initgl(self):
        """Initalize gl states when the frame is created"""
        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(1, 1, 1, 0.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.width, 0.0, self.height, -1, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glLineWidth(2.0)
        
        self.setBackGround(self.image)

    def setScale(self, scale):
        self.scale = scale
        self._display()
        
    def setBackGround(self, image: Image.Image):
        self.configure(width=self.image.width, height=self.image.height)
        self.image = image.convert("RGBA")

        imageBytes = self.image.tobytes()

        texture = glGenTextures(1)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, texture)



        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            self.image.width,
            self.image.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            imageBytes,
        )
        self.texture = texture
        self._display()

    def drawBox(self, start, end, color:str):
        pass

    def newLine(self, firstPos, color: str):
        self.lines.append([color, (firstPos[0], self.height - firstPos[1])])
        self._display()

    def addLineSeg(self, pos):
        self.lines[-1].append((pos[0], self.height - pos[1]))
        self._display()

    def undo(self):
        if len(self.lines) > 0:
            self.lines.pop(-1)
            self._display()

    def click(self, event):
        self.newLine((event.x, event.y), "#FF0000")

    def drag(self, event):
        self.addLineSeg((event.x, event.y))

    def redraw(self):
        """Render a single frame"""
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if self.texture is not None:

            glColor3f(1, 1, 1)
            glEnable(GL_TEXTURE_2D)

            glBindTexture(GL_TEXTURE_2D, self.texture)

            glBegin(GL_QUADS)
            glTexCoord(0, 1)
            glVertex2f(0, 0)
            glTexCoord(0, 0)
            glVertex2f(0, self.height)
            glTexCoord(1, 0)
            glVertex2f(self.width, self.height)
            glTexCoord(1, 1)
            glVertex2f(self.width, 0)

            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        for line in self.lines:
            glColor3f(*hexToFloatRgb(line[0]))
            glBegin(GL_LINE_STRIP)
            for point in line[1:]:
                glVertex2f(point[0] * self.scale, point[1] * self.scale)
            glEnd()


def hexToFloatRgb(hex: str):
    return (
        int(f"0x{hex[1:3]}", 16) / 256.0,
        int(f"0x{hex[3:5]}", 16) / 256.0,
        int(f"0x{hex[5:7]}", 16) / 256.0,
    )


if __name__ == "__main__":
    root = tkinter.Tk()
    root.bind("<Control-z>", lambda event: print("stuff"))
    app = GLCanvas(Image.open("devineInspiration.png"), root)
    app.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    app.animate = 0
    app.mainloop()
    


