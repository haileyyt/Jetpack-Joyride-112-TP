# This is the camera game mode
from cmu_graphics import *
from character import Character
from obstacleGeneration import DiagonalLaser, VerticalLaser
from obstacleGeneration import HorizontalLaser, RotatingLaser
from background import Queue
import random
import cv2
import os
import copy
from PIL import Image as PILImage
from nosetracker import NoseTracker
from fingerCounter import FingerCounter
from coins import *
import json
from boss import *
from bossCollision import *

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

def absPathScore():
    baseDir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(baseDir, 'highscore.json'))

def loadScores():
    try:
        with open('highscore.json', 'r') as f:
            content = f.read().strip()
            if not content: return {}  # File is empty
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def saveScores(scores):
    with open('highscore.json', 'w') as f:
        json.dump(scores, f, indent=4)

def checkOrCreateUser(username):
    scores = loadScores()
    if username not in scores:
        scores[username] = 0
        saveScores(scores)
    return username

def camera_onAppStart(app):
    app.width = 800
    app.height = 600
    app.diffScale = 1 # note the difficulty increases every second
# to change speed of rotating/ moving lasers go to obstacle generation
    app.baseStepsPerSecond = 30
    app.playingGame = True
    app.onPlayButton = False
    app.gameOver = False
    app.gamePaused = False
    app.swapToClassicMode = False
    app.cameraShutdown = False
    app.scores = loadScores()
    app.username = getattr(app, 'username', '').strip().lower()
    app.highScore = app.scores.get(app.username, 0)
    app.queue = Queue()
    app.userFingerMoves = []
    app.attackSequence = [1, 2, 3, 4, 5] # shuffle the attack sequence
    app.currentSequence = shuffleSequence(app.attackSequence) 
    app.coinCol = CoinCollection()
    app.char = Character(0, app.height - 100, 20, 10)
    app.Barry = ((app.char.x, app.char.y), 
                 (app.char.x+app.char.width, app.char.y),
                 (app.char.x+app.char.width, app.char.y+app.char.height),
                 (app.char.x,app.char.y+app.char.height))
    app.pictureFingers = [absPath('finger1.png'), absPath('finger2.png'),
                         absPath('finger3.png'), absPath('finger4.png'),
                         absPath('finger5.png')]
    resetGame(app)

def resetGame(app):
    loadBoss(app)
    app.coinCol = CoinCollection()
    app.char = Character(0, app.height - 100, 20, 10)
    app.gameOver = False
    app.lasers = []
    app.steps = 0
    app.stepsPerSecond = 30
    app.userFingerMoves = []
    app.gamePaused = False
    app.scores = loadScores()
    app.attackSequence = [1, 2, 3, 4, 5] # shuffle the attack sequence
    app.pictureFingers = [absPath('finger1.png'), absPath('finger2.png'),
                         absPath('finger3.png'), absPath('finger4.png'),
                         absPath('finger5.png')]

def loadBoss(app):
    app.boss = Boss()
    app.laser = LaserAttack(app.boss)
    app.lightning = LightningAttack(app.boss)
    app.charge = ChargeAttack(app.boss)
    app.bossSpawn = False
    app.boss.health = 100
    app.boss.cx = 600
    app.boss.cy = 300
    if not(app.bossSpawn):
        app.warningFrames = [absPath("warning0Degrees.png"), 
            absPath("warning45Degrees.png"), absPath("warning90Degrees.png"), 
            absPath("warning135Degrees.png")]
        app.warningSign = absPath("warningSign.png")
        app.showSign = True
        app.spinIndex = -1
        app.spinTimer = 0
        app.text1 = 'SCOTTY BOSS INCOMING!' 
        app.text2 = ('Take control of Barry with your nose and '
                      'match the incoming sequences')
        app.displayedText1 = ''
        app.displayedText2 = ''
        app.characterIdx1 = 0
        app.characterIdx2 = 0
    app.bossSpawnTimer = 0

def camera_onScreenActivate(app):
    if not app.cameraShutdown:
        initializeCamera(app)

# https://docs.opencv.org/3.4/d8/dfe/
# classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80
def initializeCamera(app):
    app.capture = cv2.VideoCapture(0) # initialize webcam capture
    app.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # set the width of the frame
    app.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # set the height 
    app.capture.set(cv2.CAP_PROP_FPS, 30) # set the frames per second
    app.noseTracker = NoseTracker() # initialize the nose tracker
    app.fingerCounter = FingerCounter() # initialize the finger counter

def camera_redrawAll(app):
    drawLiveCamera(app)
    if not app.gameOver:
        app.char.draw()
        if app.gamePaused:
            drawPauseScreen(app)
        for laser in app.lasers:
            laser.draw()
        drawTopLabels(app)
        if not(app.bossSpawn):
            drawWarning(app)
        elif app.bossSpawn:
            drawBossAttacks(app)
            drawFingers(app)
    if app.gameOver:
        if hasattr(app, 'username') and app.username:
            scores = loadScores()
            if app.username not in scores:
                scores[app.username] = 0
            if app.steps > scores[app.username]:
                scores[app.username] = app.steps
                saveScores(scores)
        drawEndScreen(app)

def drawLiveCamera(app):
    if (hasattr(app, 'capture') and 
        app.capture is not None and app.capture.isOpened()):
        success, frame = app.capture.read()
        if success:   #changes frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            frame = cv2.flip(frame, 1)  # flip the frame horizontally
            # have to convert the frame to a format cmu_graphics can use
            pilImage = PILImage.fromarray(frame) # convert to PIL Image
            newImage = CMUImage(pilImage) 
            drawImage(newImage, 0, 0, width=app.width, height=app.height)

def drawWarning(app):
    if app.showSign:
        drawImage(app.warningSign, app.width/2, app.height/2, 
                  align='center', width=850, height=300)
    currentImage = app.warningFrames[app.spinIndex]
    drawImage(currentImage, 50, 50, align='center', 
                width = 100, height = 100)
    drawImage(currentImage, 50, app.height - 50, align='center', 
                width = 100, height = 100)
    drawImage(currentImage, app.width - 50, 50, align='center', 
                width = 100, height = 100)
    drawImage(currentImage, app.width - 50, app.height - 50, 
                align='center', width = 100, height = 100)
    drawLabel(app.displayedText1, app.width/2, 
                app.height/2 + 150, size=32, fill='red', bold=True, 
                font = 'impact')
    drawLabel(app.displayedText2, app.width/2, app.height/2 + 180, 
                size=24, fill='red', bold=True, font = 'impact')

def drawBossAttacks(app):
    if app.boss.state == 'laserAttack' and app.laser.lasers == None:
        app.laser.generateLaserPath(app.boss, app.char.y)
    if app.boss.state == 'laserAttack' and app.laser.lasers != None:
        app.laser.draw(app.boss)
    if (app.boss.state == 'lightningAttack' and 
        app.lightning.segments != []):
        app.lightning.draw(app.boss)
    app.charge.drawWarning(app.boss)
    app.boss.draw()
    if app.boss.health > 0:
        drawRect(350, 50, 400*(app.boss.health/100), 30, fill = 'red', 
                    align = 'left-top')
        drawRect(350, 50, 400, 30, fill = None, border = 'black', 
                    borderWidth = 5, align = 'left-top')
        drawImage(app.boss.icon, 750, 65, width = 70, height = 70, 
                    align = 'center')

def drawTopLabels(app):
    drawLabel(f'DISTANCE: {app.steps}', 10, 20, size = 20, align = 'left', 
              bold = True)
    drawLabel(f'COINS: {app.coinCol.totalCoins}', 10, 50, size = 20, 
              align = 'left', bold = True, fill = 'orange')
    drawLabel(f'BEST: {app.highScore}', 10, 80, size = 20, align = 'left', 
              bold = True, fill='white') 

def drawPauseScreen(app):
    drawRect(0, 0, app.width, app.height, fill = 'black', opacity = 50)
    drawLabel('Paused', app.width/2, app.height/2 - 40, size = 36, 
              bold = True, align = 'center', fill = 'white')
    drawLabel('Press "R" to restart', app.width/2, app.height/2, 
              size = 20, align = 'center', fill = 'white')
    drawLabel('Press "H" to go back to home screen', app.width/2, 
              app.height/2 + 30, align = 'center', size = 20, fill = 'white')

def drawFingers(app):
    drawRect(400, 100, 170, 80, fill = 'white', border='black', 
             opacity = 80)
    for i in range(len(app.currentSequence)):
        fingerCount = app.currentSequence[i]
        if fingerCount == 1:
            drawImage(absPath('finger1.png'), 400 + i*50, 100, 
                              width=70, height=70)
        elif fingerCount == 2:
            drawImage(absPath('finger2.png'), 400 + i*50, 100, 
                              width=70, height=70)
        elif fingerCount == 3:
            drawImage(absPath('finger3.png'), 400 + i*50, 100, 
                              width=70, height=70)
        elif fingerCount == 4:
            drawImage(absPath('finger4.png'), 400 + i*50, 100, 
                              width=70, height=70)
        elif fingerCount == 5:
            drawImage(absPath('finger5.png'), 400 + i*50, 100, 
                              width=70, height=70)

def drawEndScreen(app):
    drawImage(absPath('gameOver.png'), 0, 0, width = app.width, 
              height = app.height)
    drawLabel(f'{app.steps}', 395, 127, align='left', size=30,
              bold = True, fill = 'white')

def camera_onMousePress(app, mouseX, mouseY):
    if app.gameOver:
        playAgainButtonX = 280
        playAgainButtonWidth = 235
        playAgainButtonHeight = 45
        playAgainButtonY = 375
        if (playAgainButtonX<=mouseX<=playAgainButtonX+playAgainButtonWidth 
            and (playAgainButtonY <= mouseY <= 
                 playAgainButtonY+playAgainButtonHeight)):
            # First ensure camera resources are released
            if hasattr(app, 'capture') and app.capture.isOpened():
                app.capture.release()
                app.capture = None
            if hasattr(app, 'noseTracker'):
                app.noseTracker.stop()
            if hasattr(app, 'fingerCounter'):
                app.fingerCounter.stop()
            # Then reset and switch screens
            setActiveScreen('classic')
            resetGame(app)

def camera_onKeyPress(app, key):
    if key == 'p':
        app.gamePaused = not app.gamePaused
    if app.gamePaused and not app.gameOver:
        if key == 'r':
            resetGame(app)
        elif key == 'h':
            setActiveScreen('start')
            resetGame(app)

def camera_onStep(app):
    if app.swapToClassicMode and not app.cameraShutdown:
        switchToClassicMode(app)
    if (app.playingGame and not app.gameOver and not app.gamePaused and
        app.boss.health > 0):
        app.steps += 1
        getFingerMoves(app)
        getNosePos(app)
        app.queue.updateQueue()
        if app.steps % (app.baseStepsPerSecond) == 0:
            generateLaser(app)
            deleteOffscreen(app)
            app.stepsPerSecond += app.diffScale
        
        for laser in app.lasers:
            laser.move()
            laser.check(app.char.hitBox)
            if app.steps % 2 == 0:
                laser.imageIndex = (laser.imageIndex + 1) % 4

        if app.steps % (app.baseStepsPerSecond) == 0:
            app.stepsPerSecond += app.diffScale

        #Update Barry's points
        updateBarry(app)

        if not(app.bossSpawn):
            triggerWarning(app)
        elif app.bossSpawn:
            triggerBoss(app)

def triggerWarning(app):
    app.bossSpawnTimer += 1
    if app.bossSpawnTimer % 20 == 0:
        app.showSign = not(app.showSign)
    if app.bossSpawnTimer % 4 == 0:  
        app.spinIndex = (app.spinIndex + 1) % len(app.warningFrames)
    if app.characterIdx1 < len(app.text1):
        app.characterIdx1 += 1
        app.displayedText1 = app.text1[:app.characterIdx1]
    elif app.characterIdx2 < len(app.text2):
        app.characterIdx2 += 1
        app.displayedText2 = app.text2[:app.characterIdx2]
    if app.bossSpawnTimer == 120:
        app.bossSpawn = True

def triggerBoss(app):
    if app.boss.state == 'move':
        app.boss.updatePosition()
    elif app.boss.state == 'laserAttack':
        app.laser.trigger(app.boss)
        if app.boss.timer >= 2:
            if checkBossCollision(app):
                app.gameOver = True
    elif app.boss.state == 'lightningAttack':
        app.lightning.trigger(app.boss)
        if app.boss.timer >= 2:
            if checkBossCollision(app):
                app.gameOver = True
    elif app.boss.state == 'chargeAttack':
        app.charge.trigger(app.boss)
        if checkBossCollision(app):
            app.gameOver = True
        if app.charge.chargeTarget == None:
            app.charge.getTarget(app.boss, app.char.y)
    elif app.boss.state == 'return':
        app.charge.returnPosition(app.boss)

def updateBarry(app):
    app.Barry = ((app.char.x, app.char.y), 
                 (app.char.x+app.char.width, app.char.y),
                 (app.char.x+app.char.width, 
                  app.char.y+app.char.height),
                  (app.char.x,app.char.y+app.char.height))

def getFingerMoves(app):
    handFingerCount = app.fingerCounter.getFingerCount() 
    if handFingerCount is not None:
        if (app.userFingerMoves == [] or 
            app.userFingerMoves[-1] != handFingerCount):
            app.userFingerMoves.append(handFingerCount)
            if len(app.userFingerMoves) > 3:
                if sequenceCompleted(app.userFingerMoves, 
                                     app.currentSequence):
                    app.boss.health -= 20
                    app.boss.updateAttackPattern()
                            # shuffle the attack sequence
                    app.currentSequence=shuffleSequence(app.attackSequence) 
                    if app.boss.health <= 0:
                        app.swapToClassicMode = True
                        return
                else:
                    app.userFingerMoves = []

def getNosePos(app):
    currentNoseY = app.noseTracker.getNoseY()
    if currentNoseY is not None:
        adjustedNoseY = currentNoseY
        floorY = app.height - app.char.height - 25
        ceilingY = 0
        clampedY = max(ceilingY, min(adjustedNoseY, floorY))
        app.char.y = clampedY
        for i in range(len(app.char.hitBox)):
            app.char.hitBox[i] = app.char.hitBox[i][0], app.char.y

        if app.char.hitFloor():
            app.char.isFlying = False
            if app.steps % 2 == 0:
                app.char.walks = (app.char.walks + 1) % 3
            else:
                app.char.isFlying = True

def switchToClassicMode(app):
    app.cameraShutdown = True
    try:
        app.noseTracker.stop()
        app.fingerCounter.stop()
        if (hasattr(app, 'capture') 
            and app.capture is not None and app.capture.isOpened()):
            app.capture.release()
    except Exception as e:
        print(f"Error during shutdown: {e}")
    finally:
        setActiveScreen('classic')
        app.bossSpawn = False
        return

def sequenceCompleted(userMoves, sequence):
    if len(userMoves) < len(sequence):
        return False
    for i in range(len(sequence)):
        if userMoves[i] != sequence[i]:
            return False
    return True

def shuffleSequence(sequence):
    sequence = copy.copy(sequence)
    return solveShuffleSequence(sequence, [])

def solveShuffleSequence(attacks, result):
    if len(attacks) == 2:
        return result
    else:
        firstIdx = random.randint(0, len(attacks)-1)
        first = attacks.pop(firstIdx)
        result.append(first)
        return solveShuffleSequence(attacks, result)

def generateLaser(app):
    laserType = random.choice([HorizontalLaser, VerticalLaser, 
                               DiagonalLaser, RotatingLaser])
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
# runAppWithScreens(initialScreen = 'camera', width = app.width, 
#                   height = app.height)
