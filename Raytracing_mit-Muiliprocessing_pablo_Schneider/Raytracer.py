import math
import multiprocessing
import time

import numpy as np
from PIL import Image

# ----Diese File ist mit MultiProzessing----#

##---Hier sind Werte zum Einstellen---##
##
##
#Numbers of Processes
nop = 4
##
##
imgWidth, imgHeight = 400, 400
##
##
maxlevel = 2
##
##
##-Hier kann man Einstellen ob man das Eichhörnchen rendern will, oder die Kugeln--##
##---0---Für Squirrel
##---1---Für Normal
##
##
mode = 0
##
##
##--------------------------------------##



##-----globale Variablen---------------##
##
##
aspactratio = imgWidth / imgHeight
BACKGROUND_COLOR = np.array([20, 20, 20])
a = np.deg2rad(45) / 2
height = 2 * math.tan(a)
width = aspactratio * height
pixelWidth = width / imgWidth
pixelHeight = height / imgHeight
data = "squirrel_aligned_lowres.obj.txt"
##
##
##---------------------------------------##

def normalized(vector):
    return vector / np.linalg.norm(vector)


#Klassen
class Material(object):
    def __init__(self, am, di, sp, color, reflection):
        self.reflection = reflection
        self.color = color
        self.ambientCoefficient = am
        self.diffuseCoefficient = di
        self.specularCoefficient = sp


class CheckerboardMaterial(Material):
    def __init__(self, am, di, sp, color, otherColor, size, reflection):
        super().__init__(am, di, sp, color, reflection)
        self.otherColor = otherColor
        self.checkSize = size

    def baseColorAt(self, p):
        v = p
        v = v * (1.0 / self.checkSize)
        if (int(abs(v[0]) + 0.5) + int(abs(v[1]) + 0.5) + int(abs(v[2]) + 0.5)) % 2:
            return self.otherColor
        return self.color


class Triangle(object):
    def __init__(self, a, b, c, material):
        self.a = a  # point
        self.b = b  # point
        self.c = c  # point
        self.u = self.b - self.a  # direction vector
        self.v = self.c - self.a  # direction vector
        self.material = material

        '''
        self.color = color
        self.ambientCoefficient = 0.5
        self.diffuseCoefficient = 0.5
        self.specularCoefficient = 0.5
        '''

    def __repr__(self):
        return 'Triangle(%s,%s,%s)' % (repr(self.a), repr(self.b), repr(self.c))

    def intersectionParameter(self, ray):
        w = ray.origin - self.a
        dv = np.cross(ray.direction, self.v)
        dvu = dv.dot(self.u)
        if dvu == 0.0:
            return None

        wu = np.cross(w, self.u)
        r = dv.dot(w) / dvu
        s = wu.dot(ray.direction) / dvu
        if 0 <= r and r <= 1 and 0 <= s and s <= 1 and r + s <= 1:
            return wu.dot(self.v) / dvu
        else:
            return None

    def normalAt(self, p):
        return normalized(np.cross(self.u, self.v))


class Plane(object):

    def __init__(self, point, normal, material):
        self.point = point  # point
        self.normal = normalized(normal)  # vector
        self.material = material
        '''
        self.color = color
        self.ambientCoefficient = 0.5
        self.diffuseCoefficient = 0.5
        self.specularCoefficient = 0.5
        '''

    def __repr__(self):
        return 'Plane(%s,%s)' % (repr(self.point), repr(self.normal))

    def intersectionParameter(self, ray):
        op = ray.origin - self.point
        a = op.dot(self.normal)
        b = ray.direction.dot(self.normal)
        if b < 0:
            return -a / b
        else:
            return None

    def normalAt(self, p):
        return self.normal


class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center  # point
        self.radius = radius  # scalar
        self.material = material
        '''
        self.color = color
        self.ambientCoefficient = 0.5
        self.diffuseCoefficient = 0.5
        self.specularCoefficient = 0.5
        '''

    def __repr__(self):
        return 'Sphere(%s,%s)' % (repr(self.center), self.radius)

    def intersectionParameter(self, ray):
        co = self.center - ray.origin
        v = co.dot(ray.direction)
        discriminant = v * v - co.dot(co) + self.radius * self.radius

        if discriminant < 0:
            return None
        else:
            return v - math.sqrt(discriminant)

    def normalAt(self, p):
        return normalized((p - self.center))


class Lichtquelle(object):

    def __init__(self, pos, color):
        self.pos = pos
        self.color = color


class Camera(object):

    def __init__(self, center, e, up):

        self.center = center
        self.e = e
        self.up = up
        self.f = normalized(center - self.e)
        self.s = normalized(np.cross(self.f, self.up))
        self.u = np.cross(self.s, self.f)


class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin  # point
        self.direction = normalized(direction)  # vector

    def __repr__(self):
        return 'Ray(%s,%s)' % (repr(self.origin), repr(self.direction))

    def pointAtParameter(self, t):
        return self.origin + self.direction * t


# Methoden
def intersect(level, ray, maxlevel, object_list):
    if level == maxlevel:
        return None

    maxdist = float('inf')

    hitobject = None
    for object in object_list:
        hitdist = object.intersectionParameter(ray)
        if hitdist:
            if 0.03 < hitdist < maxdist:
                maxdist = hitdist
                hitobject = object
    if hitobject is None:
        return None

    return maxdist, hitobject, ray



def computeDirectLight(dist, hitobject, ray, object_list, licht):
    ka = hitobject.material.ambientCoefficient
    ks = hitobject.material.specularCoefficient
    kd = hitobject.material.diffuseCoefficient

    #das hoch n aus der Vorlesung
    speku = 2

    schnittpunkt = ray.pointAtParameter(hitobject.intersectionParameter(ray))
    normal = hitobject.normalAt(schnittpunkt)
    lightvec = hitobject.normalAt(licht.pos - schnittpunkt)
    invertL = normalized(np.array([lightvec[0], -lightvec[2], lightvec[1]]))

    if isinstance(hitobject.material, CheckerboardMaterial):
        ambient = hitobject.material.baseColorAt(schnittpunkt) * ka
    else:
        ambient = hitobject.material.color * ka

    diffuser = licht.color * kd * np.dot(lightvec, normal)
    spekularer = licht.color * ks * np.dot(invertL, -ray.direction) ** speku

    color = ambient + spekularer + diffuser
    schadowRay = Ray(schnittpunkt, schnittpunkt - licht.pos)

    for objectInScene in object_list:
        # schatten
        shadowintersection = objectInScene.intersectionParameter(schadowRay)
        # 0.2 ist dafür, dass das object sich nicht selbst
        if shadowintersection and shadowintersection > 0.2:
            return color / 6

    return color


def computeReflectedRay(dist, hitobject, ray):
    schnittpunkt = ray.pointAtParameter(hitobject.intersectionParameter(ray))
    normal = hitobject.normalAt(schnittpunkt)
    return Ray(schnittpunkt, (ray.direction - 2 * np.dot(normal, ray.direction) * normal))


def shade(level, hitPointData, object_list, licht):
    directColor = computeDirectLight(hitPointData[0], hitPointData[1], hitPointData[2], object_list, licht)
    reflectedRay = computeReflectedRay(hitPointData[0], hitPointData[1], hitPointData[2])
    reflectColor = traceRay(level + 1, reflectedRay, object_list, licht)
    return directColor + reflectColor * hitPointData[1].material.reflection


def traceRay(level, ray, object_list, licht):

    hitPointData = intersect(level, ray, maxlevel, object_list)  # maxLevel = maximale RekursionsTiefe
    if hitPointData:
        return shade(level, hitPointData, object_list, licht)

    return BACKGROUND_COLOR



def calcRay(x, y, camera):
    s = camera.s
    u = camera.u
    e = camera.e
    f = camera.f
    xcomp = s * (x * pixelWidth - height / 2)
    ycomp = u * (y * pixelHeight - width / 2)
    return Ray(e, f + xcomp + ycomp)


def readData(data):

    with open(data) as datei:
        vertices = []
        faces = []
        for zeile in datei:
            if zeile.startswith("v"):
                vertex = list(map(float, zeile.split()[1:]))
                vertices.append(np.array(vertex))
            elif zeile.startswith("f"):
                face = list(map(int, zeile.split()[1:]))
                faces.append(face)
    return build_squirrel(vertices, faces)


def build_squirrel(vertices, faces):
    material = Material(0.5, 0.5, 0.5, np.array([255, 0, 0]), 0.5)
    object_list = []
    for face in faces:
        object_list.append(Triangle(vertices[face[0]-1], vertices[face[1]-1], vertices[face[2]-1], material))

    return object_list

#Methode die vom Muiltprocessing aufgerufen wird
def prozessing(begin, imgpartwidth, i, camera, object_list, licht):

    imgpartwidth = imgpartwidth
    print("start prozess:", i)
    image = Image.new(mode="RGB", size=(imgpartwidth, imgHeight))

    begin = begin
    end = begin + imgpartwidth

    for x in range(begin, end):
        for y in range(imgHeight):
            ray = calcRay(x, y, camera)
            color = traceRay(0, ray, object_list, licht)
            color = tuple(color.astype(int))
            image.putpixel((x - imgpartwidth * i, y), color)

    print("end prozess:", i)
    return (i, image)

#da man sich das Image für die Muliprozesses Aufteilt, werden die hier wieder zusammen gefügt.
def concat(img1, img2):
    image = Image.new(mode="RGB", size=(img1.width + img2.width, img1.height))
    image.paste(img1, (0, 0))
    image.paste(img2, (img1.width, 0))

    return image


if __name__ == '__main__':

    licht = Lichtquelle(np.array([3, -20, 0]), np.array([150, 150, 150]))

    if mode == 1:
        camera = Camera(np.array([0, 0, 1]), np.array([0, 0, 0]), np.array([0, -1, 0]))
        object_list = [
            Plane(np.array([0, -2.3, 4.5]), np.array([0, 550, -0.1]),
                CheckerboardMaterial(1, 0.3, 0.7, np.array([250, 250, 250]), np.array([10, 10, 10]), 1, 0.1)),
            Sphere(np.array([2, -0.5, 10]), 1.25, Material(0.5, 0.5, 0.5, np.array([255, 0, 0]), 0.5)),
            Sphere(np.array([0, 2.5, 10]), 1.25, Material(0.5, 0.5, 0.5, np.array([0, 255, 0]),0.5)),
            Sphere(np.array([-2, -0.5, 10]), 1.25, Material(0.5, 0.5, 0.5, np.array([0, 0, 255]),0.5)),
            Triangle(np.array([3.5, -0.5, 20]), np.array([0, 4, 15]),
                 np.array([-3.5, -0.5, 20]), Material(1, 0.3, 0.5, np.array([255, 255, 10]),0.5))]
    else:
        object_list = readData(data)
        camera = Camera(np.array([0, 3, 0]), np.array([0, 1.8, -10]), np.array([0, -1, 0]))


    s = camera.s
    u = camera.u
    e = camera.e
    f = camera.f

    start = time.time()

    processlist = []
    pool = multiprocessing.Pool(processes=nop)


    imgpartwidth = int(imgWidth / nop)

    res = [pool.apply_async(prozessing, (i * imgpartwidth, imgpartwidth, i, camera, object_list, licht, )) for i in range(nop)]

    res = [r.get() for r in res]

    oldImage = None

    for i in range(len(res)):
        if oldImage:
            oldImage = concat(oldImage, res[i][1])
        else:
            oldImage = res[i][1]

    oldImage.show()

    end = time.time()

    print("es hat", end - start, "gedauert")



    # img.save("Result.png", "PNG")