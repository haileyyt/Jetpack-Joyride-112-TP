from cmu_graphics import *
from Collision import *
import random, os, hitBoxTest

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

class Laser(HitBox):
    laserFrames = [absPath("Zapper1.png"), absPath("Zapper2.png"), 
                   absPath("Zapper3.png"), absPath("Zapper4.png")]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.len = random.randrange(150, 200)
        self.hitBox = None
        self.imageIndex = random.choice([0,1,2,3])
        self.polygon = None
    
    def move(self):
        self.x -= 10
        for i in range(len(self.hitBox)):
            x, y = self.hitBox[i]
            self.hitBox[i] = x - 10, y
        self.polygon = self.hitBox

 
class HorizontalLaser(Laser):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hitBox = (hitBoxTest.getConvexHull("Zapper1.png", (self.x, self.y), 
                                                self.len*2/5, self.len, 90))
        self.polygon = self.hitBox

    def draw(self):
        drawImage(Laser.laserFrames[self.imageIndex], self.x, self.y, 
                  width = self.len * 2 / 5, height = self.len, rotateAngle = 90)
        # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(self.hitBox))

class DiagonalLaser(Laser):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.hitBox = (hitBoxTest.getConvexHull("Zapper1.png", (self.x, self.y), 
                                                self.len*2/5, self.len, 45))
        self.polygon = self.hitBox

    def draw(self):
        drawImage(Laser.laserFrames[self.imageIndex], self.x, self.y, 
                  width = self.len * 2 / 5, height = self.len, rotateAngle = 45)
        # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(self.hitBox))

class VerticalLaser(Laser):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.hitBox = (hitBoxTest.getConvexHull("Zapper1.png", (self.x, self.y), 
                                                self.len*2/5, self.len, 0))
        self.polygon = self.hitBox
    
    def draw(self):
        drawImage(Laser.laserFrames[self.imageIndex], self.x, self.y, 
                  width = self.len * 2 / 5, height = self.len)
        # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(self.hitBox))

class RotatingLaser(Laser):
    def __init__(self, x, y, angle):
        super().__init__(x,y)
        self.angle = random.randrange(0, 180)
        self.hitBox = (hitBoxTest.getConvexHull("Zapper1.png", (self.x, self.y), 
                                                self.len*2/5, self.len, 
                                                self.angle))
        self.polygon = self.hitBox
    
    def move(self):
        self.angle = (self.angle + 2.5) % 360
        self.x -= 10
        self.hitBox = (hitBoxTest.getConvexHull("Zapper1.png", (self.x, self.y), 
                                               self.len*2/5, 
                                               self.len, self.angle))
        self.polygon = self.hitBox
    
    def draw(self):
        drawImage(Laser.laserFrames[self.imageIndex], self.x, self.y, 
                  width = self.len * 2 / 5, height = self.len, 
                  rotateAngle = self.angle)
        # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(self.hitBox))

