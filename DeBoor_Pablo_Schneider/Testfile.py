import glfw
import numpy as np
from OpenGL.GL import *

WIDTH = 500
HEIGHT = 500
M = 2
degree = 3
controlpoints = []
splinepoints = []
knotvector = []


def draw(mode, points, color):
    # draws objects
    glPointSize(4)
    glBegin(mode)
    glColor(color[0], color[1], color[2])
    for p in points:
        glVertex2f(p[0], p[1])
    glEnd()



def render():
    # draw black control polygon
    draw(GL_LINE_STRIP, controlpoints, [0.0, 0.0, 0.0])
    # draw red control points
    draw(GL_POINTS, controlpoints, [1.0, 0.0, 0.0])
    # draw red control points
    draw(GL_LINE_STRIP, splinepoints, [0.0, 0.0, 1.0])
    # recalculate spline curve
    calcSpline()
    # draw green bspline deboor points
    draw(GL_POINTS, splinepoints, [0.0, 1.0, 1.0])


def findR(t):
    for i in range(len(knotvector) - 1):
        if knotvector[i] > t:
            return i - 1


def calcKnotVector():
    # calculates knot vector
    global degree
    global M

    del knotvector[:]
    knotvector.extend([0 for n in range(degree)])  # n times first controllpoint
    knotvector.extend([n for n in range(1, len(controlpoints) - 1 - (degree - 2))])  # controlpoints
    knotvector.extend([len(controlpoints) - (degree - 1) for n in range(degree)])  # n times last controllpoint

    print(knotvector)

def calcSpline():
    # calculates spline curve with deboor
    calcKnotVector()
    del splinepoints[:]
    if len(controlpoints) >= degree:
        t = 0
        while t < knotvector[-1]:
            r = findR(t)
            b = deBoor(controlpoints, knotvector, t, r, degree - 1)
            splinepoints.append(b)
            t += 1 / float(M)

def deBoor(cps, knot, t, i, recursion):
    # deboor algorithm
    global degree
    global M

    if recursion == 0:
        return cps[i]
    alpha = (t - knot[i]) / (knot[i - recursion + degree] - knot[i])
    return (1 - alpha) * deBoor(cps, knot, t, i - 1, recursion - 1) + alpha * deBoor(cps, knot, t, i, recursion - 1)


def onMouseButton(win, button, action, mods):
    # mouseevents -> add new controlpoints
    global degree
    global M

    if button == 0:
        if action == 1:
            p = np.array(glfw.get_cursor_pos(win))
            p[0] = (p[0] - WIDTH / 2) / (WIDTH / 2)
            p[1] = 1 - (p[1] / (HEIGHT / 2))
            controlpoints.append(p)
            # print("Current cursor position:", p)
            # print("All controlpoints:", controlpoints)


def onKeyboard(win, key, scancode, action, mods):
    # change M or degree
    global degree
    global M

    if action == glfw.PRESS:
        if key == glfw.KEY_K:
            if mods == glfw.MOD_SHIFT:
                if degree < len(controlpoints):
                    degree += 1
            else:
                if degree - 1 > 2:
                    degree -= 1
                else:
                    degree = 2

        if key == glfw.KEY_M:
            if mods == glfw.MOD_SHIFT:
                M += 10
            else:
                if M - 10 < 10:
                    M = 10
                else:
                    M -= 10


def main():
    # initialize glfw
    if not glfw.init():
        return
    window = glfw.create_window(500, 500, "Jakob", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, onMouseButton)
    glfw.set_key_callback(window, onKeyboard)

    # opengl init
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glOrtho(0, 500, 0, 500, 0.01, 1)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glLoadIdentity()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        render()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == '__main__':
    main()