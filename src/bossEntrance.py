from cmu_graphics import *
import os

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

def onAppStart(app):
    app.stepsPerSecond = 30
    app.width = 800
    app.height = 600
    app.warningFrames = [
            absPath("warning0Degrees.png"), 
            absPath("warning45Degrees.png"), 
            absPath("warning90Degrees.png"), 
            absPath("warning135Degrees.png")
            ]
    app.warningSign = absPath("warningSign.png")
    #All warning images above generated with chatgpt
    app.showSign = True
    app.spinIndex = -1
    app.spinTimer = 0
    app.text1 = 'SCOTTY BOSS INCOMING!' 
    app.text2 = 'Take control of Barry with your nose and match the ' \
                'incoming sequences'
    app.displayedText1 = ''
    app.displayedText2 = ''
    app.characterIdx1 = 0
    app.characterIdx2 = 0

    
    
def onStep(app):
    app.spinTimer += 1
    if app.spinTimer % 20 == 0:
        app.showSign = not(app.showSign)
    if app.spinTimer % 4 == 0:  
        app.spinIndex = (app.spinIndex + 1) % len(app.warningFrames)
    if app.characterIdx1 < len(app.text1):
        app.characterIdx1 += 1
        app.displayedText1 = app.text1[:app.characterIdx1]
    elif app.characterIdx2 < len(app.text2):
        app.characterIdx2 += 1
        app.displayedText2 = app.text2[:app.characterIdx2]

def redrawAll(app):
    if app.showSign:
        drawImage(app.warningSign, app.width/2, app.height/2, align='center', 
                  width=850, height=300)
    currentImage = app.warningFrames[app.spinIndex]
    drawImage(currentImage, 50, 50, align='center', width = 100, height = 100)
    drawImage(currentImage, 50, app.height - 50, align='center', width = 100, 
              height = 100)
    drawImage(currentImage, app.width - 50, 50, align='center', width = 100, 
              height = 100)
    drawImage(currentImage, app.width - 50, app.height - 50, align='center', 
              width = 100, height = 100)
    drawLabel(app.displayedText1, app.width/2, app.height/2 + 150, size=32, 
              fill='red', bold=True, font = 'impact')
    drawLabel(app.displayedText2, app.width/2, app.height/2 + 180, size=24, 
              fill='red', bold=True, font = 'impact')

#runApp()
