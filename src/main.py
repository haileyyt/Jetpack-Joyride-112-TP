from cmu_graphics import *
from classic import *
from camera import *
import os
from boss import *

def absPath(filename): 
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

def onAppStart(app):
    app.width = 800
    app.height = 600
    app.onInfoScreen = False

def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    
def start_onAppStart(app):
    app.user = ''
    app.onInfoScreen = False
    app.buttonX = 480
    app.buttonWidth = 265
    app.buttonHeight = 65
    #play button
    app.classicButtonY = 370

    # info button
    app.infoButtonX = 740
    app.infoButtonRadius = 30
    app.infoButtonY = 100

def start_redrawAll(app):
    if not app.onInfoScreen:
        drawImage(absPath('startScreen.png'), 0, 0, width = app.width, 
                  height = app.height)
    else:
        drawImage(absPath('infoScreen.png'), 0, 0, width = app.width, 
                  height = app.height)

def start_onKeyPress(app, key):
    if key == 'h' and app.onInfoScreen:
        app.onInfoScreen = False

def start_onMousePress(app, mouseX, mouseY):
    if mouseX > app.buttonX and mouseX < app.buttonX + app.buttonWidth:
        if (mouseY > app.classicButtonY and 
            mouseY < app.classicButtonY + app.buttonHeight):
            setActiveScreen('classic')
            resetGame(app)

    if (distance(mouseX, mouseY, app.infoButtonX, app.infoButtonY) < 
                app.infoButtonRadius):
        app.onInfoScreen = True
            
def username_onAppStart(app):
    app.username = ''
    app.typing = True
    app.inputBox = (app.width//2 - 150, app.height//2 - 25, 300, 50)
    app.continueButton = (app.width//2 - 75, app.height//2 + 50, 150, 40)

def username_onKeyPress(app, key):
    if app.typing and len(key) == 1 and len(app.username) < 16:
        app.username += key

def username_onKeyRelease(app, key):
    if app.typing:
        if key == 'backspace':
            app.username = app.username[:-1]
        elif key == 'enter':
            app.typing = False
            if app.username.strip():
                app.user = checkOrCreateUser(app.username.strip())
                setActiveScreen('start')

def username_onMousePress(app, x, y):
    bx, by, bw, bh = app.continueButton
    if bx <= x <= bx + bw and by <= y <= by + bh:
        app.typing = False
        setActiveScreen('start')

def username_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    drawLabel('Enter Your Username:', 
              app.width//2, app.height//2 - 60, size=28, 
              fill='white', bold=True)

    # Input box
    x, y, w, h = app.inputBox
    drawRect(x, y, w, h, fill='white')
    drawLabel(app.username or 'Type here...', 
              x + w//2, y + h//2, size=20, fill='black', 
              italic=(app.username == ''))

    # Continue button
    bx, by, bw, bh = app.continueButton
    drawRect(bx, by, bw, bh, fill='gold')
    drawLabel('Continue', bx + bw//2, by + bh//2, size=20, bold=True)

def main():
    runAppWithScreens(initialScreen='username', width=800, height=600)

main()