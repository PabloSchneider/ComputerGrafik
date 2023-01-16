"""
/*******************************************************************************
 *
 *            #, #,         CCCCCC  VV    VV MM      MM RRRRRRR
 *           %  %(  #%%#   CC    CC VV    VV MMM    MMM RR    RR
 *           %    %## #    CC        V    V  MM M  M MM RR    RR
 *            ,%      %    CC        VV  VV  MM  MM  MM RRRRRR
 *            (%      %,   CC    CC   VVVV   MM      MM RR   RR
 *              #%    %*    CCCCCC     VV    MM      MM RR    RR
 *             .%    %/
 *                (%.      Computer Vision & Mixed Reality Group
 *
 ******************************************************************************/
/**          @copyright:   Hochschule RheinMain,
 *                         University of Applied Sciences
 *              @author:   Prof. Dr. Ulrich Schwanecke
 *             @version:   0.9
 *                @date:   23.05.2020
 ******************************************************************************/
/**         bezierTemplate.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display a Bezier curve.
 ****
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import copy



class Scene:
    """ OpenGL 2D scene class """
    # initialization
    def __init__(self, width, height,
                scenetitle="Bezier Curve Template"):
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 5
        self.width = width
        self.height = height
        self.points = []
        self.pointsW = []
        self.lines = []
        self.points_on_bezier_curve = []
        self.knotenvector = []
        self.degree = 3
        self.m = 10

    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)
        glEnable(GL_POINT_SMOOTH)


    # render
    def render(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # set foreground color to black
        glColor(0.0, 0.0, 0.0)

        # render all points
        glBegin(GL_POINTS)
        for p in self.points:
            glVertex2fv(p[:2])
        glEnd()

        if len(self.points) >= 2:
            # render polygon
            glLineWidth(self.linewidth)
            glBegin(GL_LINE_STRIP)
            for p in self.points:
                glVertex2fv(p[:2])
            glEnd()

            # render bezier curve
            glBegin(GL_LINE_STRIP)
            glColor(1, 0.0, 0.0)
            for p in self.points_on_bezier_curve:
                glVertex2fv(p[:2])
            glEnd()


    # set polygon
    def add_point(self, point):
        self.points.append(point)
        self.onChange()
        print("KnotenVector", self.knotenvector)


    #Methode die Aufgerufen wird, wenn es eine Veränderung gab
    def onChange(self):
        n = len(self.points)
        self.knotenvector = []

        self.knotenvector = [0] * self.degree
        for i in range(1, n - (self.degree - 2)): self.knotenvector += [i]
        self.knotenvector += [n - (self.degree - 1)] * (self.degree-1)

        if len(self.points) >= self.degree:
            self.determine_points_on_bezier_curve()

    # clear polygon
    def clear(self):
        self.points = []
        self.points_on_bezier_curve = []


    # determine line code
    def determine_points_on_bezier_curve(self):
        self.points_on_bezier_curve = []
        self.pointsW = []
        t = 0

        for p in self.points:
            punktX = p[0] * p[2]
            punktY = p[1] * p[2]

            self.pointsW.append((punktX, punktY, p[2]))


        while t < self.knotenvector[-1]:
            r = self.findeRmitT(t)

            #versuch1
            #p = self.deboorVersuch1(self.degree-1, self.pointsW, self.knotenvector, t)

            #Erfolg
            p = self.deboorErfolg(self.pointsW, self.knotenvector, t, r, self.degree-1)

            #wikipedia Algorithmus
            #p = self.deboorWiki(r, t, self.knotenvector, self.pointsW, self.degree-1)
            p = p / p[2]
            t += float(1 / self.m)
            self.points_on_bezier_curve.append(p)

        ##Damit die Kurve mit dem Letzen Punkt verbunden wird.

        p = self.deboorErfolg(self.pointsW, self.knotenvector, self.knotenvector[-1], r, self.degree - 1)
        #p = self.deboorVersuch1(self.degree-1, self.pointsW, self.knotenvector, self.knotenvector[-1])
        #p = self.deboorWiki(r, self.knotenvector[-1], self.knotenvector, self.pointsW, self.degree - 1)

        p = p / p[2]
        self.points_on_bezier_curve.append(p)


    # Erfolg
    def deboorErfolg(self, controllpoints, knotenvector, t, r, j):
        controllpoints = np.array(controllpoints)
        knotenvector = np.array(knotenvector)

        if j == 0:
            return controllpoints[r]

        alpha = (t - knotenvector[r]) / (knotenvector[r - j + self.degree] - knotenvector[r])
        deboorA = self.deboorErfolg(controllpoints, knotenvector, t, r - 1, j - 1)
        deboorB = self.deboorErfolg(controllpoints, knotenvector, t, r, j - 1)
        pointX = (1-alpha) * deboorA[0] + alpha * deboorB[0]
        pointY = (1-alpha) * deboorA[1] + alpha * deboorB[1]
        pointZ = (1-alpha) * deboorA[2] + alpha * deboorB[2]
        return [pointX, pointY, pointZ]

    #deboor wie es bei Wikipedia erklärt wurde
    def deboorWiki(self, r, t, knotenvector, controllpoints, p):
        knotenvector = np.array(knotenvector)
        controllpoints = np.array(controllpoints)
        newPoints = [controllpoints[j + r - p] for j in range(0, p + 1)]
        for i in range(1, p + 1):
            for j in range(p, i - 1, -1):
                alpha = (t - knotenvector[j + r - p]) / (knotenvector[j + 1 + r - i] - knotenvector[j + r - p])
                newPoints[j] = ((1.0 - alpha) * newPoints[j - 1] + alpha * newPoints[j])
        return newPoints[p]

    #deboorVersuch 1 Funktioniert nicht
    def deboorVersuch1(self, degree, controllpoints, knotenvector, t):
        r = self.findeRmitT(t)

        #print(degree)

        #print("r", r , "k", degree)
        #print("j in range 1 -", degree-1)

        for j in range(1, degree-1):
            #print(j, ": j")
            newPoints = []
            for i in range(r, r - degree + 1 + j):

                #print("i ", i)

                #print("halloefwew")
                #print("j ", j, "i ", i)
                alpha = (t - knotenvector[i])/(knotenvector[i-j+degree]-knotenvector[i])

                bX = (1-alpha)*controllpoints[i-1][0] + alpha * controllpoints[i][0]
                bY = (1-alpha)*controllpoints[i-1][1] + alpha * controllpoints[i][1]
                #print(bX, bY)
                newPoints.append([bX, bY, controllpoints[i][2]])
                print("newPoints", newPoints)
            controllpoints = newPoints

        print("controllpoints", controllpoints)
        return controllpoints[0]

    def findeRmitT(self, t):
        for i in range(len(self.knotenvector)-1):
            if self.knotenvector[i] > t:
                return i - 1


class RenderWindow:
    """GLFW Rendering window class"""
    def __init__(self, scene):
        self.pointindex = 0
        self.testX = 0
        self.testFinal = 1
        self.gedruckt = False
        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # version hints
        #glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        #glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        #glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        #glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width/float(self.height)
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)

        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0,  -2, 2)
        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_cursor_pos_callback(self.window, self.findGewicht)
        glfw.set_window_size_callback(self.window, self.onSize)

        # create scene
        self.scene = scene #Scene(self.width, self.height)
        self.scene.setOpenGLStates()

        # exit flag
        self.exitNow = False

    #Methode um wenn man das Gewicht verändern will.
    def findGewicht(self,win ,x, y):
        if self.gedruckt:

            #print(int(x-self.testX)/10)
            scene.points[self.pointindex][2] = int((x - self.testX)/10)
            if scene.points[self.pointindex][2] > 10:
                scene.points[self.pointindex][2] = 10
            if scene.points[self.pointindex][2] < 1:
                scene.points[self.pointindex][2] = 1

            scene.onChange()

            print("Punkt Index ", self.pointindex," gewichtung: ", scene.points[self.pointindex][2])


    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)

        if action == glfw.PRESS:
            if mods != glfw.MOD_SHIFT:
                x, y = glfw.get_cursor_pos(win)
                p = [int(x), int(y), 1]
                scene.add_point(p)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                if mods == glfw.MOD_SHIFT:
                    x, y = glfw.get_cursor_pos(win)
                    index = 0;
                    for point in scene.points:
                        if point[0] - 15 < x < point[0] + 15 and point[1] - 15 < y < point[1] + 15:
                            self.pointindex = index
                            self.testX = x
                            self.gedruckt = True
                            point[2] = self.testFinal

                        index += 1
            else:
                self.gedruckt = False


    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            # clear everything
            if key == glfw.KEY_C:
                self.scene.clear()

            if key == glfw.KEY_M:
                if mods == glfw.MOD_SHIFT:
                    scene.m = scene.m + 2

                else:
                    if scene.m > 3:
                        scene.m = scene.m - 2
                print("m ", scene.m)
                scene.onChange()
            if key == glfw.KEY_K:
                if mods == glfw.MOD_SHIFT:
                    if scene.degree < len(scene.points):
                        scene.degree = scene.degree + 1
                else:
                    if scene.degree -1 > 2:
                       scene.degree = scene.degree - 1
                print("k ", scene.degree)
                scene.onChange()


    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        self.width = width
        self.height = height
        self.aspect = width/float(height)
        glViewport(0, 0, self.width, self.height)


    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0/self.frame_rate:
                # update time
                t = currT
                # clear viewport
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                # render scene
                self.scene.render()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()




# call main
if __name__ == '__main__':
    print("bezierTemplate.py")
    print("pressing 'C' should clear the everything")
    print("auf m und shift m kann man die Anzahl der punkte beeinflussen")
    print("auf k und shift k kann man den Degree beeinflussen")
    print("wenn man auf ein Punkt drückt und dann nach rechts zieht, kann man diesen eine Gewichtung von 1 - 10 geben.")
    # set size of render viewport
    width, height = 640, 480

    # instantiate a scene
    scene = Scene(width, height, "Bezier Curve Template")

    rw = RenderWindow(scene)
    rw.run()
