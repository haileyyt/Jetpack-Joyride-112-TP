from cmu_graphics import *
import hitBoxTest
from Collision import *
import os

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

class Character(HitBox):
    def __init__(self, x, y, vel, g):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 75
        self.g = g
        self.vel = vel
        self.accel = 0
        self.isFlying = False
        self.walks = 0
        self.hitBox = (hitBoxTest.getConvexHull("BarryRun1.png", 
                                                (self.x, self.y), 
                                                self.width, self.height, 0))
        self.barryWalk = [absPath("BarryRun1.png"),
                          absPath("BarryRun2.png"),
                          absPath("BarryRun3.png")]
    
    def fly(self, t):
        dy = self.vel + self.accel * t//10
        newY = self.y - dy
        if newY < 0:
            dy = self.y
        self.y -= dy
        for i in range(len(self.hitBox)):
            x, y = self.hitBox[i]
            self.hitBox[i] = x, y- dy
    
    def fall(self, t):
        if not self.hitFloor():
            self.y += self.g*t//10
            for i in range(len(self.hitBox)):
                x, y = self.hitBox[i]
                self.hitBox[i] = x, y + self.g*t//10

    def hitFloor(self): # this is so bad why do i pass in global height var
        return (self.y + self.g > 600 - self.height - 25)

    def hitCeiling(self):
        return (self.y + self.vel <= (self.height // 2 + self.vel))

    def draw(self):
        if self.hitFloor():
            drawImage(self.barryWalk[self.walks], self.x, self.y, 
                      width = self.width, height = self.height)
        else:
            drawImage(absPath("BarryFly.png"), self.x, self.y, 
                      width = self.width + 20, height = self.height)
        # drawPolygon(*hitBoxTest.fancyFlattenEdgeList(self.hitBox))
        # drawCircle(self.x, self.y, self.r, fill = 'red', border = 'black')

"""def onAppStart(app):
    app.width = width
    app.height = height
    app.char = Character(width // 10, height // 2, 25, 20, 10)
    app.stepsPerSecond = 30

def redrawAll(app):
    app.char.draw()

def onKeyHold(app, keys):
        if 'space' in keys:
            app.char.isFlying = True
            app.char.fly()

def onKeyRelease(app, key):
    if key == 'space':
        app.char.isFlying = False
        app.char.accel = 0

def onStep(app):
    if app.char.isFlying:
        app.char.accel += 0.5
    app.char.fall()

def main():
    runApp()

main()"""
