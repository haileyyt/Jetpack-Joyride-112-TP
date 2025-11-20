from cmu_graphics import *
import random, math, os
from bossAttackPattern import generateAttackSequence, shuffle

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

# def onAppStart(app):
#     app.width = 800
#     app.height = 600
#     app.stepsPerSecond = 30
#     app.boss = Boss()
#     app.laser = LaserAttack(app.boss)
#     app.lightning = LightningAttack(app.boss)
#     app.charge = ChargeAttack(app.boss)

class Boss:
    def __init__(self):
        self.health = 100
        self.spriteClose = absPath("bossClose.png")
        self.spriteOpen = absPath("bossOpen.png")
        self.spriteCharge = absPath("bossChargeNew.png")
        self.icon = absPath("scottyBossIcon.png")
        #All boss images above generated using chatgpt
        self.mouthOpen = False
        self.state = 'move'
        self.cx = 600
        self.cy = 300
        self.targetY = 300
        self.timer = 0
        self.attacks = ['laser', 'lightning', 'charge']
        self.attackIndex = -1
        self.phase = 1
        self.updateAttackPattern()
    def updateAttackPattern(self):
        if self.health >= 80 and self.phase != 1:
            self.attackPattern = shuffle(self.attacks)
            self.phase = 1
        elif self.health >= 40 and self.phase != 2:
            self.attackPattern = generateAttackSequence(self.attacks)
            self.phase = 2
        elif self.health < 40 and self.phase != 3:
            self.attackPattern = shuffle(self.attacks * 3)
            self.phase = 3
    def updatePosition(self):
        self.mouthOpen = False
        dy = self.targetY - self.cy
        if abs(dy) <= 5:
            self.cy = self.targetY
            self.targetY = random.randint(150, 450)
            self.attackIndex += 1
            attackIdx = self.attackIndex % len(self.attackPattern)
            attack = self.attackPattern[attackIdx]
            if attack == 'laser':
                self.state = 'laserAttack'
            elif attack == 'lightning':
                self.state = 'lightningAttack'
            else:
                self.state = 'chargeAttack'
        else:
            self.cy += (dy/abs(dy))*5
    def draw(self):
        if self.mouthOpen:
            sprite = self.spriteOpen
        else:
            sprite = self.spriteClose
        if self.state == 'chargeAttack' or self.state == 'return':
            sprite = self.spriteCharge
        imageWidth, imageHeight = getImageSize(sprite)
        self.height = imageHeight*0.7
        self.width = imageWidth*0.7
        drawImage(sprite, self.cx, self.cy, align='center', width = self.width, 
                  height = self.height)

class LaserAttack:
    def __init__(self, Boss):
        self.lasers = None
    def generateLaserPath(self, Boss, charY):
        y0 = charY
        y1 = Boss.cy
        x0 = -10
        x1 = Boss.cx - 90
        self.lasers = (x0, y0, x1, y1)
    def draw(self, Boss):
        x0, y0, x1, y1 = self.lasers
        if Boss.timer >= 2:
            drawLine(x0, y0, x1, y1, lineWidth = 25, fill = 'red')
            drawLine(x0, y0, x1, y1, lineWidth = 15, fill = 'orange')
            drawLine(x0, y0, x1, y1, lineWidth = 5, fill = 'white')
        else:
            drawLine(x0, y0, x1, y1, opacity = 50, lineWidth = 10, 
                     fill = 'red')
    def trigger(self, Boss):
        Boss.timer += 1/30
        Boss.mouthOpen = True
        if Boss.timer >= 4:
            Boss.timer = 0
            self.lasers = None
            Boss.state = 'move'

class LightningAttack:
    def __init__(self, Boss):
        self.segments = []
    def trigger(self, Boss):
        Boss.timer += 1/30
        Boss.mouthOpen = True
        if self.segments == []:
            spawnBranch(self.segments, Boss.cx - 80, Boss.cy, 180, 4, 150)
        if Boss.timer >= 4:
            Boss.timer = 0
            self.segments = []
            Boss.state = 'move'
    def draw(self, Boss):
        for i in range(len(self.segments)):
            cx0, cy0, cx1, cy1 = self.segments[i]
            if Boss.timer >= 2:
                drawLine(cx0, cy0, cx1, cy1, lineWidth = 10, fill = 'red')
                drawLine(cx0, cy0, cx1, cy1, lineWidth = 5, fill = 'orange')
                drawLine(cx0, cy0, cx1, cy1, lineWidth = 2, fill = 'white')
            else:
                drawLine(cx0, cy0, cx1, cy1, lineWidth = 5, fill = 'red')

def spawnBranch(segments, cx, cy, angle, depth, length):
    if depth == 0:
        return
    else:
        rad = math.radians(angle)
        cxEnd = cx + length * math.cos(rad)
        cyEnd = cy + length * math.sin(rad)
        segments.append((cx, cy, cxEnd, cyEnd))
        for delta in (-10, 10):
            newAngle = angle + delta
            spawnBranch(segments, cxEnd, cyEnd, newAngle, depth-1, length)

class ChargeAttack:
    def __init__(self, Boss):
        self.chargeTarget = None
        self.dx = 0
        self.dy = 0
        self.spinTimer = 0
        self.spinIndex = 0
        self.warningFrames = [
            absPath("warning0Degrees.png"), 
            absPath("warning45Degrees.png"), 
            absPath("warning90Degrees.png"), 
            absPath("warning135Degrees.png")
            ]
    def trigger(self, Boss):
        Boss.timer += 1/30
        if Boss.timer < 2:
            self.warn()
        elif Boss.timer >= 2:
            self.charge(Boss)
        if Boss.timer >= 4:
            Boss.state = 'return'
    def getTarget(self, Boss, charY):
        cy = charY
        if cy < 150:
            cy = 150
        elif cy > 450:
            cy = 450
        cx = 175
        self.chargeTarget = (cx, cy)
        self.dx = (Boss.cx - cx)/20
        self.dy = (Boss.cy - cy)/20
    def warn(self):
        self.spinTimer += 1
        if self.spinTimer % 4 == 0:  
            self.spinIndex = (self.spinIndex + 1) % len(self.warningFrames)
    def drawWarning(self, Boss):
        if (Boss.state == 'chargeAttack' and Boss.timer > 1/30 and 
            Boss.timer < 2):
            cy = self.chargeTarget[1]
            currentImage = self.warningFrames[self.spinIndex]
            drawImage(currentImage, 50, cy, align='center', width = 100, 
                      height = 100)
    def charge(self, Boss):
        targetX = self.chargeTarget[0]
        targetY = self.chargeTarget[1]
        Boss.cx -= self.dx
        Boss.cy -= self.dy
        if Boss.cx - targetX <= 20 and Boss.cy - targetY <= 20:
            Boss.cx = targetX
            Boss.cy = targetY
    def returnPosition(self, Boss):
        Boss.timer = 0
        self.chargeTarget = None
        dx = (600 - Boss.cx)/20
        Boss.cx += dx
        if 600-Boss.cx <= 20:
            Boss.cx = 600
            Boss.state = 'move'






# def onStep(app):
#     if app.boss.state == 'move':
#         app.boss.updatePosition()
#     elif app.boss.state == 'warn':
#         #app.laser.trigger(app.boss)
#         app.lightning.trigger(app.boss)
#     elif app.boss.state == 'charge':
#         app.charge.trigger(app.boss)
#     elif app.boss.state == 'return':
#         app.charge.returnPosition(app.boss)
# def redrawAll(app):
#     if app.boss.state == 'warn' and app.laser.lasers != None:
#         app.laser.draw(app.boss)
#     if app.boss.state == 'warn' and app.lightning.segments != []:
#         app.lightning.draw(app.boss)
#     app.charge.drawWarning(app.boss)
#     app.boss.draw()

# runApp()