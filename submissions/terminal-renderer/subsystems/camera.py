import numpy
from subsystems.display import DisplaySettings
from subsystems.debug import *

class Camera:
    def __init__(self, debug, x = 0, y = 0, z = 0, pitch = 0, yaw = 0):
        self.debug = debug
        self.x = x
        self.y = y
        self.z = z
        self.pitch = pitch
        self.yaw = yaw

        # not in inital for now
        self.fov = numpy.pi / 4
        self.nearPlane = 0.1
        self.farPlane = 100
    
    def applyMovement(self, controllerX, controllerY, controllerZ):
        self.x += controllerX #numpy.cos(self.yaw) * controllerX
        self.y += controllerY #numpy.sin(self.yaw) * controllerY
        self.z += controllerZ

    def applyRotation(self, controllerX, controllerY):
        self.yaw += controllerX
        self.yaw = (self.yaw + numpy.pi) % (2 * numpy.pi) - numpy.pi
        self.pitch += controllerY
        self.pitch = numpy.clip(self.pitch, -numpy.pi/2, numpy.pi/2)

    def getPosition(self):
        return [self.x,self.y,self.z]

    def getRotation(self):
        cosPitch =  numpy.cos(self.pitch)
        sinPitch =  numpy.sin(self.pitch)
        cosYaw =  numpy.cos(self.yaw)
        sinYaw =  numpy.sin(self.yaw)

        return numpy.array([
            [ cosYaw, -sinYaw*cosPitch,  sinYaw*sinPitch, 0],
            [ sinYaw,  cosYaw*cosPitch, -cosYaw*sinPitch, 0],
            [      0,         sinPitch,         cosPitch, 0],
            [      0,                0,                0, 1]
        ])


    def getProjection(self):
        f = 1/numpy.tan(self.fov/2)
        return numpy.array([
            [f/DisplaySettings.ASPECT_RATIO,  0,                                                                  0,  0],
            [                             0,  f,                                                                  0,  0],
            [                             0,  0,      (self.nearPlane+self.farPlane)/(self.nearPlane-self.farPlane), -1],
            [                             0,  0,    (2*self.farPlane*self.nearPlane)/(self.nearPlane-self.farPlane),  0]
        ])
    
    def update(self):
        self.latestRotation = self.getRotation()
        self.latestProjection = self.getProjection()
        
        self.debug.post(" | Camera: pos {}, rot {}".format([self.x, self.y, self.z], [self.yaw, self.pitch]))

    def project(self, point):
        homogeneous = numpy.append(point, 1)
        screenSpacePoint = numpy.dot(self.latestProjection, numpy.dot(self.latestRotation, homogeneous))
        if screenSpacePoint[3] != 0:
            screenSpacePoint /= screenSpacePoint[3]
        return screenSpacePoint[:2]