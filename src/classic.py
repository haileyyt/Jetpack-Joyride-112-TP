# This is the classic game mode
from cmu_graphics import *
from character import Character
from obstacleGeneration import DiagonalLaser, VerticalLaser
from obstacleGeneration import HorizontalLaser, RotatingLaser
import os
import random
from background import Queue
from coins import *
import json

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

def absPathScore():
    baseDir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(baseDir, 'highscore.json'))

def loadScores():
    try:
        with open(absPathScore(), 'r') as f:
            content = f.read().strip()
            if not content: return {}  # File is empty
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def saveScores(scores):
    with open(absPathScore(), 'w') as f:
        json.dump(scores, f, indent=4)

def checkOrCreateUser(username):
    scores = loadScores()
    if username not in scores:
        scores[username] = 0
        saveScores(scores)
    return username

def classic_onAppStart(app):
    app.width = 800
    app.height = 600
    app.diffScale = 1 # note the difficulty increases every second
# to change speed of rotating/ moving lasers go to obstacle generation
    app.username = getattr(app, 'username', '').strip().lower()
    app.baseStepsPerSecond = 30
    app.scores = loadScores()
    app.highScore = app.scores.get(app.username, 0)
    app.playingGame = True
    app.onPlayButton = False
    app.gameOver = False
    app.gamePaused = False
    app.queue = Queue()
    app.fallTime = 0
    app.flyTime = 0
    app.coinCol = CoinCollection()
    app.char = Character(0, app.height-100, 20, 10)
    app.Barry = ((app.char.x, app.char.y),
                 (app.char.x + app.char.width, app.char.y),
                 (app.char.x + app.char.width, app.char.y + app.char.height),
                 (app.char.x, app.char.y + app.char.height))
    resetGame(app)
def updateBarry(app):
    app.Barry = ((app.char.x, app.char.y),
                 (app.char.x + app.char.width, app.char.y),
                 (app.char.x + app.char.width, app.char.y + app.char.height),
                 (app.char.x, app.char.y + app.char.height))
def resetGame(app):
    app.coinCol = CoinCollection()
    app.char = Character(0, app.height-100, 20, 10)
    app.gameOver = False
    app.lasers = []
    app.steps = 0
    app.stepsPerSecond = 30
    app.gamePaused = False
    app.scores = loadScores()

def classic_redrawAll(app):
    if not app.gameOver:
        app.queue.drawBG()
        app.char.draw()

        for laser in app.lasers: laser.draw()

        drawLabel(f'DISTANCE: {app.steps}', 10, 20, size = 20, align = 'left', 
                  bold = True)
        drawLabel(f'COINS: {app.coinCol.totalCoins}', 10, 50, size = 20, 
                  align = 'left',
                    bold = True, fill = 'orange')
        drawLabel(f'BEST: {app.highScore}',10,80,size=20,align='left', 
                            bold=True,fill='white') 
        
        app.coinCol.drawCoins(app.steps//2)

        if app.gamePaused:
            drawRect(0, 0, app.width, app.height, fill = 'black', opacity = 50)
            drawLabel('Paused', app.width/2, app.height/2 - 40, size = 36, 
                      bold = True, align = 'center', fill = 'white')
            drawLabel('Press "R" to restart', app.width/2, app.height/2, 
                      size = 20, align = 'center', fill = 'white')
            
            drawLabel('Press "H" to go back to home screen', app.width/2, 
                      app.height/2 + 30, align = 'center', size = 20, 
                      fill = 'white')
    if app.gameOver:
        if hasattr(app, 'username') and app.username:
            scores = loadScores()
            if app.username not in scores:
                scores[app.username] = 0
            if app.steps > scores[app.username]:
                scores[app.username] = app.steps
                saveScores(scores)
        drawEndScreen(app)

def drawEndScreen(app):
    drawImage(absPath('gameOver.png'), 0, 0, width = app.width, 
              height = app.height)
    drawLabel(f'{app.highScore+1}', 395, 127, align='left', size=30,
              bold = True, fill = 'white')

def classic_onMousePress(app, mouseX, mouseY):
    if app.gameOver:
        playAgainButtonX = 280
        playAgainButtonWidth = 235
        playAgainButtonHeight = 45
        playAgainButtonY = 375
        if (mouseX > playAgainButtonX and 
            mouseX < playAgainButtonX + playAgainButtonWidth):
            if (mouseY > playAgainButtonY and 
                mouseY < playAgainButtonY + playAgainButtonHeight):
                resetGame(app)
        
def classic_onKeyHold(app, keys):
    if not app.gameOver and not app.gamePaused:
        if 'space' in keys:
            app.char.isFlying = True
            app.char.fly(app.flyTime)
            app.fallTime = 0

def classic_onKeyRelease(app, key):
    if not app.gameOver and not app.gamePaused:
        if key == 'space':
            app.char.isFlying = False
            app.char.accel = 0
            app.flyTime = 0

def classic_onKeyPress(app, key):
    if key == 'p':
        app.gamePaused = not app.gamePaused
    if app.gamePaused and not app.gameOver:
        if key == 'r':
            resetGame(app)
        elif key == 'h':
            setActiveScreen('start')
            resetGame(app)

def classic_onStep(app):
    if app.playingGame and not app.gameOver and not app.gamePaused:
        app.highScore = max(app.scores.get(app.username, 0), app.steps)
        app.steps += 1
        app.queue.updateQueue()
        if app.char.isFlying:
            app.flyTime += 1
            app.char.accel += 0.5
        app.char.fall(app.fallTime)
        app.fallTime += 1
        app.coinCol.updateCoins(app.diffScale*9, app.Barry)
        if app.steps % 2 == 0 and app.char.hitFloor():
            app.char.walks = (app.char.walks + 1) % 3

        if app.steps % (app.baseStepsPerSecond*1.5//1) == 0:
            generateLaser(app)
            deleteOffscreen(app)
            app.stepsPerSecond += app.diffScale
        
        if app.steps % (app.baseStepsPerSecond*5) == 0:
            app.coinCol.addDesign(random.randint(1, 3), 900, 
                                  random.randint(0, 400), 
                                  random.randint(2, 5))
        
        for laser in app.lasers:
            laser.move()
            laser.check(app.char.hitBox)
            if app.steps % 2 == 0:
                laser.imageIndex = (laser.imageIndex + 1) % 4
        if app.steps % (app.baseStepsPerSecond) == 0:
            app.stepsPerSecond += app.diffScale
        
        #Update Barry's points
        updateBarry(app)
        # changing to boss mode
        if app.steps == 500:
            setActiveScreen('camera')

def checkCollision(app):
    # this is like projection stuff to check line collision
    for laser in app.lasers: 
        if ((((app.char.x - laser.x)**2 + 
              (app.char.y - laser.y)**2) <= app.char.r**2) or
            (((app.char.x - laser.x1)**2 + 
              (app.char.y - laser.y1)**2) <= app.char.r**2)):
            return True
        dx, dy = laser.x1 - laser.x, laser.y1 - laser.y
        t = ((app.char.x - laser.x) * dx + 
             (app.char.y - laser.y) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        closestX = laser.x + t * dx
        closestY = laser.y + t * dy
        distSq = (closestX - app.char.x)**2 + (closestY - app.char.y)**2
        if distSq <= app.char.r**2:
            app.lastMode = 'classic'
            return True
    return False

def generateLaser(app):
    laserType = random.choice([HorizontalLaser, 
                               VerticalLaser, 
                               DiagonalLaser, 
                               RotatingLaser])
    if laserType != RotatingLaser:
        app.lasers.append(laserType(800, random.randrange(10, 390)))
    else:
        app.lasers.append(laserType(800, random.randrange(10, 390), 45))

def deleteOffscreen(app):
    i = 0
    poppedSmth = True
    while i < len(app.lasers):
        currentLaser = app.lasers[i]
        if currentLaser.x < -200:
            app.lasers.pop(i)
            poppedSmth = True
        else:
            if poppedSmth:
                return

#runAppWithScreens(initialScreen = 'classic', width = width, height = height)