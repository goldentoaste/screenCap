import tkinter
from OpenGL import GL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from pyopengltk import OpenGLFrame
from PIL import Image


class GLCanvas(OpenGLFrame):
    def __init__(self, image, highlight=False, *args, **kwargs):
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
        self.bind("<ButtonRelease-1>", self.release)
        


        self.animate = 0

        self.scale = 1
        self.rectPoints = []
        self.cursorPoint = None
        self.highlight = highlight

    def initgl(self):
        """Initalize gl states when the frame is created"""
        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(1, 1, 1, 0.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.width, 0.0, self.height, -1, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.setBackGround(self.image)

    def drawDot(self, pos, color):
        self.cursorPoint = (pos.x, self.height - pos.y, color)
        self._display()

    def clearDot(self):
        if self.cursorPoint is not None:
            self.cursorPoint = None
            self._display()

    def hasLines(self):
        return self.lines != []

    def clearLines(self):
        if self.lines:
            self.lines.clear()
            self._display()

    def setScale(self, scale):
        self.scale = scale

        for line in self.lines:
            iniScale = line[0]
            for point in line[2:]:
                point = (point[0] * scale / iniScale, point[1] * scale / iniScale)

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

    def setOffset(self, x, y):
        """
        sets offset for lines currently drawn in canvas
        """
        for line in self.lines:
            for point in line[1:]:
                point = (point[0] + x, point[1] + y)

    # start = upper left corner, end = lower right corner
    def drawRect(self, start, end):
        self.rectPoints.clear()
        self.rectPoints.extend([start, (end[0], start[1]), end, (start[0], end[1])])
        self._display()

    def clearRect(self):
        if self.rectPoints:
            self.rectPoints.clear()
            self._display()

    def newLine(self, firstPos, color: str):
        # iniScale, lineColor, then list of 2dVectors
        self.lines.append([self.scale, color, (firstPos[0], self.height - firstPos[1])])
        self._display()

    def addLineSeg(self, pos):
        self.lines[-1].append((pos[0], self.height - pos[1]))
        self._display()

    def undo(self):
        if len(self.lines) > 0:
            self.lines.pop(-1)
            self._display()

    def click(self, event):
        # self.newLine((event.x, event.y), "#FF0000")
        pass

    def drag(self, event):
        self.drawRect((200, 200), (event.x, event.y))

    def release(self, event):
        self.clearRect()

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
            glLineWidth(2.0)
            glColor3f(*hexToFloatRgb(line[0]))
            glBegin(GL_LINE_STRIP)
            for point in line[2:]:
                glVertex2f(point[0], point[1])
            glEnd()

        if self.rectPoints:
            glLineWidth(2.0)

            glColor4f(0, 0, 0, 0.5)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_QUADS)
            for point in self.rectPoints:
                glVertex2f(point[0], self.height - point[1])
            glEnd()
            glDisable(GL_BLEND)
            glColor3f(1, 1, 1)
            glBegin(GL_LINE_LOOP)
            for point in self.rectPoints:
                glVertex2f(point[0], self.height - point[1])
            glEnd()

        if self.highlight:
            glLineWidth(1)
            glColor3f(1, 1, 1)

            glBegin(GL_LINE_LOOP)

            glVertex2f(0, 0)
            glVertex2f(self.width, 0)
            glVertex2f(self.width, self.height)
            glVertex2f(0, self.height)

            glEnd()

        if self.cursorPoint is not None:

            glEnable(GL_POINT_SMOOTH)
            glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
            glColor3f(*hexToFloatRgb(self.cursorPoint[2]))
            glBegin(GL_POINT)
            glPointSize(2)
            glVertex2f(self.cursorPoint[0], self.cursorPoint[1])
            glEnd()
            glDisable(GL_POINT_SMOOTH)


def hexToFloatRgb(hex: str):
    return (
        int(f"0x{hex[1:3]}", 16) / 256.0,
        int(f"0x{hex[3:5]}", 16) / 256.0,
        int(f"0x{hex[5:7]}", 16) / 256.0,
    )


if __name__ == "__main__":
    root = tkinter.Tk()
    app = GLCanvas(Image.open("devineInspiration.png"), root)
    app.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    app.animate = 0
    
    other = GLCanvas(Image.open("devineInspiration.png"), root)
    other.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    other.animate = 0
    
    root.mainloop()
