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
 *                @date:   03.06.2019
 ******************************************************************************/
/**         RenderWindow.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display some 2D animation.
 ****
"""
import math

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from OpenGL.arrays import vbo

tMat = np.eye(4)
sMat = np.eye(4)
rMat = np.eye(4)

myVBO = None

#for rotate Objcet
actOri = np.identity(4)
angle = 0.0
axis = np.array([0, 1, 0])
startP = np.array([0, 0, 0])
doRotation = False

#for moving Object
doMove = False
move = np.array([0, 0])
moveX = 0
moveY = 0

#for zoom
doScale = False
scalemove = np.array([0, 0])

#for orthocamera
isOrtho = True

#schatten
shadowOn = False
light = np.array([6000,2500,2500])

class Scene:
    """ OpenGL 2D scene class """
    # initialization
    def __init__(self, width, height, 
                vertices,
                scenetitle="2D Scene"):
        # time
        self.t = 0
        self.dt = 0.001
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 3
        self.width = width
        self.height = height
        self.vertices = vertices
        self.animate = False
        self.alpha = 0 # rotation angle around x-axis
        self.beta = 0  # rotation angle around y-axis
        self.gamma = 0 # rotation angle around z-axis
        self.boundingBox = [np.array(list(map(min, list(zip(*self.vertices))))), np.array(list(map(max, list(zip(*self.vertices)))))]
        self.center = np.array((self.boundingBox[0] + self.boundingBox[1])/2)
        self.scalefactor = 2/max(self.boundingBox[1]-self.boundingBox[0])

    # set scene dependent OpenGL states
    def setOpenGLStates(self):

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)


class RenderWindow:
    """GLFW Rendering window class"""
    def __init__(self, scene):
        # save current working directory
        cwd = os.getcwd()
        
        # Initialize the library
        if not glfw.init():
            return
        
        # restore cwd
        os.chdir(cwd)
        
        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width/float(self.height)
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)
        self.color = (0.5, 0.5, 0.5, 1)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)
    
        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glColor(0.5, 0.5, 0.5, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.width <= self.height:
            glOrtho(-1.5, 1.5, -1.5 * self.height / self.width, 1.5 * self.height / self.width, -10, 10)
        else:
            glOrtho(-1.5 * self.width / self.height, 1.5 * self.width / self.height, -1.5, 1.5, -10, 10)

        glMatrixMode(GL_MODELVIEW)

        # set window callbacks

        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_cursor_pos_callback(self.window, self.mouseMoved)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_scroll_callback(self.window, self.scroll)

        ######################----Shadow---########################
        '''
        self.shadowWidth, self.shadowHeight = 1024, 1024
        self.depthMapFBO = 0
        self.depthMap = 0
        self.lightPos = (-2.0, 4.0, -1.0)

        glGenFramebuffers(1, self.depthMapFBO)
        glGenTextures(1, self.depthMap)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.shadowWidth, self.shadowHeight, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthMapFBO, 0);
        glDrawBuffer(GL_NONE);
        glReadBuffer(GL_NONE);
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        '''
        ######################----Shadow---########################


        # create scene
        self.scene = scene #Scene(self.width, self.height)
        self.scene.setOpenGLStates()

        # exit flag
        self.exitNow = False


        # animation flags
        self.forward_animation = False
        self.backward_animation = False

    # Hier geschieht die ganze Magie
    def display(self):
        myVBO.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, myVBO)
        glNormalPointer(GL_FLOAT, 24, myVBO + 12)
        #glColorPointer(3, GL_FLOAT, 0, self.color)

        ###########-----Shadow-----###########
        '''
        # 1.first render to depth map
        glViewport(0, 0, self.shadowWidth, self.shadowHeight);
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO);
        glClear(GL_DEPTH_BUFFER_BIT);
        self.configureShaderAndMatrices();
        RenderScene();

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        #2.then render scene as normal with shadow mapping (using depth map)
        glViewport(0, 0, self.width, self.height);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        self.configureShaderAndMatrices();
        glBindTexture(GL_TEXTURE_2D, self.depthMap);
        RenderScene();
        '''
        ###########-----Shadow-----###########


        self.schatten()
        glColor(self.color)
        glLoadIdentity()

        self.orthoOrFrustum()
        glTranslate(+moveX, moveY, 0)
        glMultMatrixf(np.dot(actOri, self.rotate(angle, axis)))
        glScale(self.scene.scalefactor, self.scene.scalefactor, self.scene.scalefactor)
        glTranslate(-scene.center[0], -scene.center[1], -scene.center[2])

        glDrawArrays(GL_TRIANGLES, 0, len(data))
        myVBO.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        #glfw.swap_buffers(self.window)

    # Eine Vereinfachte SchattenMethode, so wie diese auf dem Aufgaben Blatt vom letzten Semenster war.

    def configureShaderAndMatrices(self):
        near_plane = 1.0
        far_plane = 7.5
        glOrtho(-10.0, 10.0, -10.0, 10.0, near_plane, far_plane)
        gluLookAt(-2.0, 4.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def schatten(self):
        if shadowOn:
            p = np.array([[1.0, 0, 0, 0],
                          [0, 1.0, 0, 0],
                          [0, 0, 1.0, 0],
                          [0, 1.0 / -light[1], 0, 0]]).transpose()

            glPushMatrix()

            glTranslatef(0, self.scene.boundingBox[0][1], 0)

            glTranslatef(light[0], light[1], light[2])

            glMultMatrixf(p)
            glTranslatef(-light[0], -light[1], -light[2])
            glTranslatef(0, -self.scene.boundingBox[0][1], 0)

            glColor(0.2, 0.2, 0.2)

            glDisable(GL_LIGHTING)

            glDrawArrays(GL_TRIANGLES, 0, len(data))

            glEnable(GL_LIGHTING)

            glPopMatrix()

            glColor(0.5, 0.5, 0.5, 1)

    # Methode um von der Othogonalen Projektion zur Zentralen zu wechseln.
    def orthoOrFrustum(self):
        global isOrtho
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if not isOrtho:
            if self.width <= self.height:
                glFrustum(-1.5, 1.5, -1.5 * self.height / self.width, 1.5 * self.height / self.width, 1.0, 10)
            else:
                glFrustum(-1.5 * self.width / self.height, 1.5 * self.width / self.height, -1.5, 1.5, 1.0, 10)
            gluLookAt(0,0,4, 0,0,0, 0,1,0)
        else:
            if self.width <= self.height:
                glOrtho(-1.5, 1.5, -1.5 * self.height / self.width, 1.5 * self.height / self.width, -10, 10)
            else:
                glOrtho(-1.5 * self.width / self.height, 1.5 * self.width / self.height, -1.5, 1.5, -10, 10)
        glMatrixMode(GL_MODELVIEW)

    #Hier ist noch ne Zoommethode mit dem Mausrads
    def scroll(self, ac, xos, yos):
        if yos > 0:
            self.scene.scalefactor *= 1.2
        if yos < 0:
            self.scene.scalefactor /= 1.2

    #Scroll Methode mit der Mittleren MouseTaste
    def scrollMid(self, x, y):
        global scalemove, doScale
        if doScale:
            scale = scalemove[1] / (scalemove[1] + y) * 2
            self.scene.scalefactor = self.scene.scalefactor * scale

    #Methode um das Objekt in einer Kugel zu rotieren
    def projectOnSphere(self,x,y,r):
        x, y = x - self.width/2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y**2)
        z = math.sqrt(r*r - a)
        l = math.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l

    #methode die die roation berechnet
    def rotate(self, angle, axis):
        c, mc = math.cos(angle), 1 - math.cos(angle)
        s = math.sin(angle)
        l = math.sqrt(np.dot(np.array(axis), np.array(axis)))
        if l == 0:
            return np.identity(4)
        x, y, z = np.array(axis)/l
        r = np.array([[x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
                      [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
                      [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
                      [0, 0, 0, 1]])
        return np.transpose(r)

    # methode um das Object zu bewegen
    def objectMove(self, x, y):
        global move, moveY, moveX
        x, y = x / self.width, 1 - y / self.height
        if doMove:
            moveX = x - move[0]
            moveY = y - move[1]
            print("x", move)
            print("x ", moveX,"y", moveY)

    # methode die die Rotation anstößt
    def mouserotate(self, x, y):
        global angle, axis, scaleFactor
        if doRotation:
            r = min(self.width, self.height) / 2.0
            moveP = self.projectOnSphere(x, y, r)
            if -1 <= np.dot(startP, moveP) <= 1: # da arccos zwischen den Wertebereich [-1, 1]
                angle = np.arccos(np.dot(startP, moveP))
            axis = np.cross(startP, moveP)

    # methode die die ganzen MouseMethoden anstößt
    def mouseMoved(self, win, x, y):
        #global angle, axis, scaleFactor
        self.mouserotate(x, y)
        self.objectMove(x, y)
        self.scrollMid(x, y)


    # Eventhandler für die Maus
    def onMouseButton(self, win, button, action, mods):
        global startP, actOri, angle, doRotation, doMove, move, doScale, scalemove
        #print("mouse button: ", win, button, action, mods)
        if button == glfw.MOUSE_BUTTON_LEFT:
            x, y = glfw.get_cursor_pos(win)
            r = min(self.width, self.height) / 2.0
            if action == glfw.PRESS:
                doRotation = True
                startP = self.projectOnSphere(x, y, r)
            if action == glfw.RELEASE:
                doRotation = False
                actOri = np.dot(actOri, self.rotate(angle, axis))
                angle = 0
        if button == glfw.MOUSE_BUTTON_RIGHT:
            x, y = glfw.get_cursor_pos(win)
            if action == glfw.PRESS:
                doMove = True
                move = np.array([(x/self.width) - moveX, (1-y/self.height) - moveY])
            if action == glfw.RELEASE:
                doMove = False
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            x, y = glfw.get_cursor_pos(win)
            scalemove = x, y
            if action == glfw.PRESS:
                doScale = True
            if action == glfw.RELEASE:
                doScale = False

    # Eventhandler für die Tastaur
    def onKeyboard(self, win, key, scancode, action, mods):
        global isOrtho, shadowOn
        #print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # press ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            if mods == glfw.MOD_SHIFT:
                if key == glfw.KEY_R:
                    self.color = (1, 0, 0, 1)
                if key == glfw.KEY_G:
                    self.color = (1, 1, 0, 1)
                if key == glfw.KEY_B:
                    self.color = (0, 0, 1, 1)
                if key == glfw.KEY_S:
                    self.color = (0.05, 0.05, 0.05, 1)
                if key == glfw.KEY_W:
                    self.color = (1, 1, 1, 1)
            else:
                if key == glfw.KEY_R:
                    glClearColor(1, 0, 0, 1)
                if key == glfw.KEY_G:
                    glClearColor(1, 1, 0, 1)
                if key == glfw.KEY_B:
                    glClearColor(0, 0, 1, 1)
                if key == glfw.KEY_S:
                    glClearColor(0.05, 0.05, 0.05, 1)
                if key == glfw.KEY_W:
                    glClearColor(1, 1, 1, 1)
                if key == glfw.KEY_P:

                    isOrtho = False

                if key == glfw.KEY_O:
                    isOrtho = True
                if key == glfw.KEY_F:
                    if shadowOn:
                        shadowOn = False
                    else:
                        shadowOn = True


    def onSize(self, win, width, height):
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
                self.display()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()


#Methode die die dien aus den daten der obj datei die verticies, faces und normals machen.
def redobj(path):
    vertices, faces, normals = [],[],[]
    with open(path,"r") as file:
        for line in file:
            if line.startswith('vn'):

                split = line.split()
                split = (split[1:])
                normal = [float(split[0]), float(split[1]), float(split[2])]
                split.append(normal)

            elif line.startswith('v'):
                split = line.split()
                split = split[1:]
                vertex = [float(split[0]),float(split[1]), float(split[2])]
                vertices.append(vertex)

            elif line.startswith('f'):
                split = line.split()
                face = split[1:]
                face = [f.split('/') for f in face]
                faces.append(face)

    vertices = np.array(vertices)
    #wenn es keine normalen gibt, werden die hier berechnet und in calcNormal reingeschrieben, sodass ich mir das umschreiben von
    #den Faces sparen kann
    if len(normals) == 0:
        calcNormals = [0] * len(vertices)
        for face in faces:
            v1 = vertices[int(face[0][0])-1]-vertices[int(face[1][0])-1]
            v2 = vertices[int(face[0][0])-1]-vertices[int(face[2][0])-1]
            normal = np.cross(v1, v2)
            calcNormals[int(face[0][0])-1] = normal
            calcNormals[int(face[1][0])-1] = normal
            calcNormals[int(face[2][0])-1] = normal

    return vertices, faces, normals, calcNormals


# call main


if __name__ == '__main__':
    if len(sys.argv) != 2:
       print("pointViewer.py pointset.raw")
       sys.exit(-1)

    # set size of render viewport
    width, height = 640, 480
    readdata = redobj(sys.argv[1])
    vertices, faces, normals, calcNormals = readdata[0], readdata[1], readdata[2], readdata[3]
    data = []

    #das erstellen von den Data einmal, wenn die Normals gegeben waren und einmal nicht.
    if len(normals) != 0:
        for face in faces:
            for vertex in face:
                vn = int(vertex[0])-1
                nn = int(vertex[2])-1
                data.append(vertices[vn])
                data.append(normals[nn])

    else:
        for face in faces:
            for vertex in face:
                vn = int(vertex[0])-1
                data.append(vertices[vn])
                data.append(calcNormals[vn])




    myVBO = vbo.VBO(np.array(data, 'f'))
    print("Folgene EingabeMöglichkeiten sind vorhanden:")
    print("S, W, R, G oder B um den Hintergrung zu verändern.")
    print("mit SHIFT und S, W, R, G oder B verändert man die Farbe von dem Object.")
    print("mit P und O kann man die KameraArt verändern")
    print("und mit F kann man schatten ein und aus machen.")

    print("Linke Maustaste : Rotation")
    print("rechte Maustaste : Verschiebung")
    print("Mittlere, und Mausrad: Zoomen")


    # instantiate a scene
    scene = Scene(width, height, vertices, "pointViewer Template")

    rw = RenderWindow(scene)
    rw.run()
