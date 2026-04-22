from cmu_graphics import * 
import random
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

class Fruit:
    def __init__(self, name, image,x, y, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.rotate = random.randint(-30, 30)
        self.dx = random.randint(-4,4) 
        self.dy = random.choice(list(range(-22, -10, 2))) 
        self.gravity = 0.5 
        self.sliced = False
        self.rightImage = f'{name}Right.png'
        self.leftImage = f'{name}Left.png'
        self.rightHalf = {'image': self.rightImage, 'x': self.x, 'y': self.y, 
                          'width': self.width/2, 'height': self.height, 'dx': 3, 'dy': 1, 'opacity': 100, 'rotate': self.rotate}
        self.leftHalf = {'image': self.leftImage, 'x': self.x, 'y': self.y, 
                         'width': self.width/2, 'height': self.height, 'dx': -3, 'dy': 1, 'opacity': 100, 'rotate': self.rotate}

    def draw(self):
        drawImage(self.image, self.x, self.y, width=self.width, height=self.height, 
                  rotateAngle=self.rotate, align='center')
    
    def updatePosition(self,app):
        self.x += self.dx  * app.sloMoFactor
        self.y += self.dy * (app.sloMoFactor)
        self.dy += self.gravity * app.sloMoFactor
    
    def isLegal(self,app):
        return self.y<app.height+75

def onAppStart(app):
    app.showFontWarnings = False
    # CV AND MEDIAPIPE SETUP (USED AI - GEMINI) - Lines 44-47
    setupHandTracker(app)
    app.cap = cv2.VideoCapture(0)
    app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    restart(app)
    app.stepsPerSecond = 60
    app.steps = 0
    app.highScore = 0
    app.soundIsPlaying = True
    app.beach = 'FULL BG.png'
    app.playBG = 'Play BG.png'
    app.sound = Sound('Beach Song.mp3')
    app.woodSign = 'Wood Sign.png'
    app.surfboards = 'Surfboards.png'
    app.sliceSound = Sound('SliceSound.mp3')
    app.torchSound = Sound('TorchSound.mp3')
    app.flowerSound = Sound('FlowerSound.mp3')
    app.width = 950
    app.height = 535
    app.spawnRate = 0.07
    app.sloMo = False
    app.sloMoTimer = 0  
    app.sloMoFactor = 1
    app.controller = 'hand'
    app.gameMode = 'classic'
    app.hitTorch = False
    app.hitTorchTimer = 0
    app.sound.play(loop=True)
    app.challengeStepCounter = 0

def restart(app):
    app.cx, app.cy = app.width/2, app.height/2
    app.targetHandCoords = [app.width/2, app.height/2]
    app.trail = []
    app.score = 0   
    app.gameOver = False
    app.livesLeft = 3
    app.unslicedFruits = []
    app.slicedFruits = []

# Following function used AI (Gemini)
def setupHandTracker(app):
    model_path = 'hand_landmarker.task'
    base_options = python.BaseOptions(model_asset_path=model_path)
    def update_hand_position(result, output_image, timestamp_ms):
        if result.hand_landmarks:
            tip = result.hand_landmarks[0][8]
            app.targetHandCoords[0] = tip.x * app.width
            app.targetHandCoords[1] = tip.y * app.height
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=update_hand_position
        )
    app.detector = vision.HandLandmarker.create_from_options(options)

def inBounds(mouseX,mouseY,x,y,width,height):
    return (x<=mouseX<=x+width) and (y<=mouseY<=y+height)

def toggleSound(app):
    app.soundIsPlaying = not app.soundIsPlaying
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()

def updateSlicedFruits(app):
    for fruit in app.slicedFruits:
        fruit.rightHalf['dy'] += 0.5
        fruit.leftHalf['dy'] += 0.5
        fruit.rightHalf['x'] += fruit.rightHalf['dx']
        fruit.rightHalf['y'] += fruit.rightHalf['dy']
        fruit.leftHalf['x'] += fruit.leftHalf['dx']
        fruit.leftHalf['y'] += fruit.leftHalf['dy']
        fruit.rightHalf['opacity'] = max(0, fruit.rightHalf['opacity'] - 2)
        fruit.leftHalf['opacity'] = max(0, fruit.leftHalf['opacity'] - 2)
    app.slicedFruits = [fruit for fruit in app.slicedFruits if fruit.rightHalf['opacity'] > 0]

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5

def loadNextFruit(app):
    fruits = {'pineapple': ('Pineapple.png',100, 170), 
              'dragonfruit': ('Dragonfruit.png', 80, 80), 
              'kiwi': ('Kiwi.png', 70, 70),
              'coconut': ('Coconut.png', 60, 60),
              'orange': ('Orange.png', 70, 70),
              'mango': ('Mango.png', 60, 80),
              'banana': ('Banana.png',80, 80),
              'flower': ('Flower.png', 90, 90),
              'torch': ('Torch.png', 150, 150)}
    flowerChance = 0.02
    torchChance = min(0.03 + app.score/100 * 0.03, 0.40)
    chance = random.random()
    if chance < flowerChance:
        name = 'flower'
    elif chance < flowerChance + torchChance:
        name = 'torch'
    else:
        normalFruits = [fruit for fruit in fruits if fruit not in ['flower', 'torch']]
        name = random.choice(normalFruits)
    image, width, height = fruits[name]
    x0 = random.randint(100, 800)
    y0 = app.height 
    newFruit = Fruit(name, image, x0, y0, width, height)
    app.unslicedFruits.append(newFruit)

def drawSoundButton(app):
    drawRect(830,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('SOUND',880,26,font='caveat',fill='lemonChiffon',
              size=22,border='lemonChiffon',borderWidth=1)

def drawHomeButton(app):
    drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('HOME',70,26,font='caveat',fill='lemonChiffon',
               size=22,border='lemonChiffon',borderWidth=1)
    
def drawMenuButton(app):
    drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('MENU',70,26,font='caveat',fill='lemonChiffon',
               size=22,border='lemonChiffon',borderWidth=1)

def drawTrail(app):
    for i in range(len(app.trail)-1):
        opacityFactor = i / len(app.trail)
        opacity = int(100 * (opacityFactor))
        drawCircle(app.trail[i][0], app.trail[i][1], 5, 
                 fill=gradient('yellow', 'orange','fuchsia'), 
                 opacity=opacity, border='pink', borderWidth=2)
        
def drawInstructions(app):
    drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
    drawLabel('HOW TO PLAY:',470,95,font='caveat',size = 70,fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawSoundButton(app)
    drawHomeButton(app) 

def drawLives(app):
    for i in range(app.livesLeft):
        drawImage('Heart.png', 675 + i*40, 7, width=30, height=30)

def drawSlicedFruits(app):
    for fruit in app.slicedFruits:
        drawImage(fruit.rightHalf['image'], fruit.rightHalf['x'], fruit.rightHalf['y'], 
                  width=fruit.rightHalf['width'], height=fruit.rightHalf['height'], 
                  opacity=fruit.rightHalf['opacity'], align='center', rotateAngle=fruit.rightHalf['rotate'])
        drawImage(fruit.leftHalf['image'], fruit.leftHalf['x'], fruit.leftHalf['y'], 
                  width=fruit.leftHalf['width'], height=fruit.leftHalf['height'], 
                  opacity=fruit.leftHalf['opacity'], align='center', rotateAngle=fruit.leftHalf['rotate'])

def drawGameOverScreen(app):
    drawRect(0,0,app.width,app.height,fill='orange',opacity=75)
    drawImage('flames.png', 0, 0, width=app.width, height=app.height,opacity=50)
    drawLabel('GAME OVER',app.width/2,app.height/2,size=175,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=2)
    drawLabel(f'HIGH: {app.highScore}',app.width/2 - app.width/6,app.height/2+120,size=50,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawLabel(f'SCORE: {app.score}',app.width/2 + app.width/6,app.height/2+120,size=50,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawLabel("PRESS 'SPACE' TO RESTART",app.width/2,app.height/2+190,
              size=30,font='caveat',fill='saddleBrown', border='saddleBrown',borderWidth=1)
    
def drawSloMoEffect(app):
    drawRect(0, 0, app.width, app.height, fill='hotPink', opacity=25)
    drawImage('sloMoBG.jpg', 0, 0, width=app.width, height=app.height, opacity=20)


def home_redrawAll(app):
    drawImage(app.beach,0,0,width=950,height=535)
    drawImage(app.beach,0,0,width=950,height=535)
    drawImage(app.woodSign,60,60,width=800,height=580)
    drawLabel('SANDBOX',475,200,size=145,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
    drawLabel('- SLICE -',475,325,size=120,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
    drawRect(260,400,175,75,fill='burlyWood',border='lemonChiffon',borderWidth=5)
    drawRect(500,400,175,75,fill='burlyWood',border='lemonChiffon',borderWidth=5)
    drawLabel('PLAY!',345,433,font='caveat',fill='lemonChiffon',size=45,border='lemonChiffon',borderWidth=2)
    drawLabel('INSTRUCTIONS',590,433,font='caveat',fill='lemonChiffon',size=25,border='lemonChiffon',borderWidth=2)
    drawImage(app.surfboards,720,200,width=260,height=420)       
    drawSoundButton(app)

def home_onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        toggleSound(app)
    elif inBounds(mouseX,mouseY,260,400,175,75):
        setActiveScreen('selectModes')
    elif inBounds(mouseX,mouseY,500,400,175,75):
        setActiveScreen('instructions')

def home_onMouseRelease(app,mouseX,mouseY):
    pass

def instructions_redrawAll(app):
    drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
    drawLine(75, 90,75, 50, arrowEnd=True,fill = 'mediumVioletRed')
    drawLine(75,90,115,90,fill='mediumVioletRed')
    drawLabel('CLICK TO', 175,75,size = 18,fill='mediumVioletRed',font='caveat',bold=True)
    drawLabel('RETURN HOME', 175,100,size = 18,fill='mediumVioletRed',font='caveat',bold=True)
    drawLabel('CLICK TO', 775,50,size = 18,fill='mediumVioletRed',font='caveat',bold=True)
    drawLabel('PAUSE/UNPAUSE', 775,75,size = 18,fill='mediumVioletRed',font='caveat',bold=True)
    drawLabel('MUSIC', 775,100,size = 18,fill='mediumVioletRed',font='caveat',bold=True)
    drawLine(875, 90,875, 50, arrowEnd=True,fill = 'mediumVioletRed')
    drawLine(875,90,835,90,fill='mediumVioletRed')
    drawLabel('HOW TO PLAY:',470,80,font='caveat',size = 80,fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawLabel('CONTROLLERS:',245,150,font='caveat',fill='saddleBrown',size=40,border='saddleBrown',borderWidth=1)
    drawLabel('GAME MODES:',695,150,font='caveat',fill='saddleBrown',size=40,border='saddleBrown',borderWidth=1)
    drawImage('HandModeInstructions.png', 300,185,width=100,height = 115)
    drawImage('MouseModeInstructions.png',300,315,width = 100,height = 115)
    drawImage('ClassicModeInstructions.png',540,185,width = 100,height=115)
    drawImage('ChallengeModeInstructions.png',540,315,width = 100,height = 115)
    drawPolygon(640,242,690,185,690,300,fill='mediumVioletRed')
    drawRect(690,185,200,115,fill='mediumVioletRed')
    drawLabel('SLICE FRUITS TO SCORE',
              780,215, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('HIT A TORCH, LOSE A LIFE',
              780,240, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('PLAY UNTIL NO LIVES LEFT',
              780,265, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawPolygon(640,372,690,315,690,430,fill='mediumVioletRed')
    drawRect(690,315,200,115,fill='mediumVioletRed')
    drawLabel('CUT THE NUMBER',
              780,345, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('OF FRUITS BEFORE',
              780,370, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('THE TIMER RUNS OUT',
              780,395, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawPolygon(300,242,250,185,250,300,fill='mediumVioletRed')
    drawRect(50,185,200,115,fill='mediumVioletRed')
    drawLabel('WITH ONE HAND, MOVE',
              155,215, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('INDEX FINGER IN FRONT OF',
              155,240, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('CAMERA TO CONTROL SLICER',
              155,265, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawPolygon(300,372,250,315,250,430,fill='mediumVioletRed')
    drawRect(50,315,200,115,fill='mediumVioletRed')
    drawLabel('USE MOUSEPAD',
              155,360, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawLabel('TO CONTROL SLICER',
              155,385, fill='lemonChiffon',size = 17, font='caveat',border = 'lemonChiffon', borderWidth = 1)
    drawSoundButton(app)
    drawHomeButton(app)

def instructions_onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        toggleSound(app)
    elif inBounds(mouseX,mouseY,20,10,100,35):
        setActiveScreen('home')

def instructions_onMouseRelease(app,mouseX,mouseY):
    pass

def selectModes_redrawAll(app):
    drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
    drawLabel('CLICK TO SELECT:',470,80,font='caveat',size = 75,fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawSoundButton(app)
    drawHomeButton(app)
    cameraModeColor = 'lemonChiffon' if app.controller != 'hand' else 'mediumVioletRed'
    classicModeColor = 'lemonChiffon' if app.gameMode != 'classic' else 'mediumVioletRed'
    mouseModeColor = 'lemonChiffon' if app.controller != 'mouse' else 'mediumVioletRed'
    challengeModeColor = 'lemonChiffon' if app.gameMode != 'challenge' else 'mediumVioletRed'
    drawLabel('1. CONTROLLER',245,150,font='caveat',fill='saddleBrown',size=40,border='saddleBrown',borderWidth=1)
    drawLabel('2. GAME MODE',695,150,font='caveat',fill='saddleBrown',size=40,border='saddleBrown',borderWidth=1)
    drawRect(70,200, 160,180,fill='burlyWood',border=cameraModeColor,borderWidth=5)
    drawRect(255,200, 160,180,fill='burlyWood',border=mouseModeColor,borderWidth=5)
    drawRect(515,200, 160,180,fill='burlyWood',border=classicModeColor,borderWidth=5)
    drawRect(700,200, 160,180,fill='burlyWood',border=challengeModeColor,borderWidth=5)
    drawRect(85,215,130,130,fill='lemonChiffon')
    drawImage('Laptop.png',110,235,width=100,height=100)
    drawImage('HandDemo.png',90,265,width=40,height=65)
    drawLine(110,270,175,245,dashes=True,fill='mediumVioletRed')
    drawLine(180,230,175,240,arrowEnd=True,fill='mediumVioletRed')
    drawCircle(180, 275, 3.5, fill=gradient('pink','mediumVioletRed', 'fuchsia'),
                border='pink',borderWidth=1)
    drawRect(270,215,130,130,fill='lemonChiffon')
    drawCircle(335, 260, 10, fill=gradient('pink','mediumVioletRed', 'fuchsia'),
                border='pink',borderWidth=2)
    drawImage('Cursor.png',325,260,width=60,height=60)
    drawRect(530,215,130,130,fill='lemonChiffon')
    drawImage('ClassicModeSelect.png',530,215,width=130,height=130)
    drawImage('Heart.png',620,325,width=15,height=15)
    drawImage('Heart.png',640,325,width=15,height=15)
    drawImage('Torch.png',620,260,width=40,height=60,rotateAngle = 45)
    drawRect(715,215,130,130,fill='lemonChiffon')
    drawImage('ChallengeModeSelect.png',715,215,width=130,height=130)
    drawImage('Stopwatch.png',810,250,width=30,height=30)
    drawLabel("PRESS 'S' TO START!",470,430,font='caveat',size=40,fill='saddleBrown',border='saddleBrown',borderWidth=1)
    drawLabel('FINGER-TRACKING',150,360,font='caveat',fill=cameraModeColor,size=18, border=cameraModeColor,borderWidth=1)
    drawLabel('MOUSE',330,360,font='caveat',fill=mouseModeColor,size=23, border=mouseModeColor,borderWidth=1)
    drawLabel('CLASSIC',595,360,font='caveat',fill=classicModeColor,size=23, border=classicModeColor,borderWidth=1)
    drawLabel('CHALLENGE',780,360,font='caveat',fill=challengeModeColor,size=23, border=challengeModeColor,borderWidth=1)

def selectModes_onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        toggleSound(app)
    elif inBounds(mouseX,mouseY,20,10,100,35):
        setActiveScreen('home')
    elif inBounds(mouseX,mouseY,515,200,160,180):
        restart(app)
        app.gameMode = 'classic'
    elif inBounds(mouseX,mouseY,700,200,160,180):
        app.gameMode = 'challenge'
    elif inBounds(mouseX,mouseY,70,200, 160,180):
        app.controller = 'hand'
    elif inBounds(mouseX,mouseY,255,200, 160,180):
        app.controller = 'mouse'

def selectModes_onMouseRelease(app,mouseX,mouseY):
    pass

def selectModes_onKeyPress(app,key):
    if key == 's':
        gameMode = app.gameMode+'Mode'
        if app.gameMode == 'challenge':
            app.challengeWin = False
            challengeRestart(app)
        setActiveScreen(gameMode)

def classicMode_redrawAll(app):
    drawImage(app.playBG,0,0,width=app.width,height=app.height)
    for fruit in app.unslicedFruits:
        fruit.draw()
    drawSlicedFruits(app)
    drawRect(200,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel(f'HIGH: {app.highScore}',275,26,font='caveat',fill='lemonChiffon', size=22,border='lemonChiffon',borderWidth=1,align='center')
    drawRect(450,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel(f'{app.score}',525,26,font='caveat',fill='lemonChiffon', size=22,border='lemonChiffon',borderWidth=1,align='center')              
    drawLives(app)
    drawTrail(app)
    drawCircle(app.cx, app.cy, 8, fill=gradient('pink','mediumVioletRed', 'fuchsia'),
                border='pink',borderWidth=2)
    if app.gameOver:
        drawGameOverScreen(app)
    if app.sloMo:
        drawSloMoEffect(app)
    if app.hitTorch:
        drawImage('flames.png', 0, 0, width=app.width, height=app.height, opacity=20)
    drawSoundButton(app)
    drawMenuButton(app)

def classicMode_onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        toggleSound(app)
    elif inBounds(mouseX,mouseY,20,10,100,35):
        setActiveScreen('selectModes')

def classicMode_onMouseRelease(app,mouseX,mouseY):
    pass

def classicMode_onKeyPress(app,key):
    if app.gameOver:
        if key == 'space':
            restart(app)

def classicMode_onStep(app):
    app.steps += 1
    if app.controller == 'hand':
        app.cx += (app.targetHandCoords[0] - app.cx) * 0.5
        app.cy += (app.targetHandCoords[1] - app.cy) * 0.5
        app.trail.append((app.cx, app.cy))
        if len(app.trail) > 10:
            app.trail.pop(0)
        # lines 103-109 used AI (Gemini)
        success, frame = app.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)
            app.detector.detect_async(mp_image, timestamp_ms)

    updateSlicedFruits(app)
    if not app.gameOver:
        if random.random() < app.spawnRate:
            loadNextFruit(app)
        for fruit in app.unslicedFruits:
            fruit.updatePosition(app)
            if distance(app.cx, app.cy, fruit.x, fruit.y) < max(fruit.width, fruit.height)/2:
                if not fruit.sliced:
                    fruit.sliced = True
                    if fruit.name == 'torch':
                        app.livesLeft -= 1
                        app.hitTorch = True
                        app.torchSound.play()
                        if app.livesLeft == 0:
                            app.gameOver = True
                    elif fruit.name == 'flower':
                        app.flowerSound.play()
                        app.sloMo = True
                        app.sloMoFactor = 0.5
                    else:
                        fruit.rightHalf['x'] = fruit.x
                        fruit.rightHalf['y'] = fruit.y
                        fruit.leftHalf['x'] = fruit.x   
                        fruit.leftHalf['y'] = fruit.y
                        fruit.rightHalf['dy'] = fruit.dy + 5
                        fruit.leftHalf['dy'] = fruit.dy + 5
                        app.slicedFruits.append(fruit)
                        app.score += 10
                        app.sliceSound.play()
                    if app.score > app.highScore:
                        app.highScore = app.score
        remaining = []
        for fruit in app.unslicedFruits:
            if fruit.isLegal(app) and not fruit.sliced:
                remaining.append(fruit)
            else:
                if not fruit.sliced and fruit.name not in ['torch', 'flower']:
                    app.score = max(0, app.score - 5)
        app.unslicedFruits = remaining
    if (app.steps%app.stepsPerSecond == 0) and app.sloMo:
        app.sloMoTimer += 1
        if app.sloMoTimer == 2:
            app.sloMo = False
            app.sloMoTimer = 0
            app.sloMoFactor = 1
    if app.hitTorch:
        app.hitTorchTimer += 1
        if app.hitTorchTimer > 8:
            app.hitTorch = False
            app.hitTorchTimer = 0

def classicMode_onMouseMove(app,mouseX,mouseY):
    if app.controller == 'mouse':
        app.cx = mouseX
        app.cy = mouseY
        app.trail.append((mouseX,mouseY))
        if len(app.trail) > 10:
            app.trail.pop(0)

def challengeMode_redrawAll(app):
    drawImage(app.playBG,0,0,width=app.width,height=app.height)
    drawImage('Stopwatch.png',835,50,width=95,height=95)
    drawLabel(str(app.challengeTimer),882,118,font='caveat',fill='deepPink',size=30,bold=True)
    drawSoundButton(app)
    drawMenuButton(app)
    for fruit in app.unslicedFruits:
        fruit.draw()
    drawSlicedFruits(app)
    drawTrail(app)
    drawCircle(app.cx, app.cy, 8, fill=gradient('pink', 'mediumVioletRed', 'fuchsia'),
               border='pink', borderWidth=2)
    drawChallengeLeft(app)
    if app.gameOver:
        drawChallengeGameOver(app)    

def challengeRestart(app):
    app.cx, app.cy = app.width/2,app.height/2
    app.targetHandCoords = [app.width/2,app.height/2]
    app.trail = []
    app.gameOver = False
    app.unslicedFruits = []
    app.slicedFruits = []
    app.challengeTimer = 20
    app.challengeStepCounter = 0
    items = ['pineapple','dragonfruit','kiwi','coconut',
             'orange','mango','banana']
    app.targets = {name: random.randint(1,11) for name in items}
    app.remaining = dict(app.targets)

def challengeMode_onStep(app):
    app.steps += 1
    if app.controller == 'hand':
        app.cx += (app.targetHandCoords[0] - app.cx) * 0.5
        app.cy += (app.targetHandCoords[1] - app.cy) * 0.5
        app.trail.append((app.cx,app.cy))
        if len(app.trail) > 10:
            app.trail.pop(0)
        success, frame = app.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)
            app.detector.detect_async(mp_image, timestamp_ms)
    updateSlicedFruits(app)
    if not app.gameOver:
        app.challengeStepCounter += 1
        if app.challengeStepCounter >= app.stepsPerSecond:
            app.challengeStepCounter = 0
            app.challengeTimer -= 1
            if app.challengeTimer <= 0:
                app.gameOver = True
    if random.random() < app.spawnRate:
        challengeLoadNextFruit(app)
    for fruit in app.unslicedFruits:
        fruit.updatePosition(app)
        if not fruit.sliced:
            if distance(app.cx,app.cy,fruit.x,fruit.y) < max(fruit.width,fruit.height)/2:
                fruit.sliced = True
                if app.remaining.get(fruit.name,0) > 0:
                    app.remaining[fruit.name] -= 1
                fruit.rightHalf['x'] = fruit.x
                fruit.rightHalf['y'] = fruit.y
                fruit.leftHalf['x'] = fruit.x
                fruit.leftHalf['y'] = fruit.y
                fruit.rightHalf['dy'] = fruit.dy + 5
                fruit.leftHalf['dy'] = fruit.dy + 5
                app.slicedFruits.append(fruit)
                app.score += 10
                app.sliceSound.play()
    app.unslicedFruits = [fruit for fruit in app.unslicedFruits
                          if fruit.isLegal(app) and not fruit.sliced]
    if all(v == 0 for v in app.remaining.values()):
        app.gameOver = True
        app.challengeWin = True

def challengeLoadNextFruit(app):
    fruits = {'pineapple': ('Pineapple.png',100, 170), 
              'dragonfruit': ('Dragonfruit.png', 80, 80), 
              'kiwi': ('Kiwi.png', 70, 70),
              'coconut': ('Coconut.png', 60, 60),
              'orange': ('Orange.png', 70, 70),
              'mango': ('Mango.png', 60, 80),
              'banana': ('Banana.png',80, 80),}
    name = random.choice(list(fruits.keys()))
    image, width, height = fruits[name]
    x0 = random.randint(100, 800)
    y0 = app.height 
    newFruit = Fruit(name, image, x0, y0, width, height)
    app.unslicedFruits.append(newFruit)

def drawChallengeLeft(app):
    fruits = ['pineapple', 'dragonfruit', 'kiwi', 'coconut', 
              'orange', 'mango', 'banana']
    images = {'pineapple': 'Pineapple.png', 'dragonfruit': 'Dragonfruit.png',
              'kiwi': 'Kiwi.png', 'coconut': 'Coconut.png', 'orange': 'Orange.png',
              'mango': 'Mango.png', 'banana': 'Banana.png',}
    startX = 190
    startY = 35
    spacing = 85
    for i, name in enumerate(fruits):
        x = startX + i * spacing
        remaining = app.remaining[name]
        done = remaining == 0
        opacity = 50 if done else 100
        drawImage(images[name], x, startY, width=40, height=40, 
                  align='center', opacity=opacity)
        color = 'limeGreen' if done else 'mediumVioletRed'
        label = '-' if done else str(remaining)
        drawLabel(label, x, startY + 30, font='caveat', size=30, 
                  fill=color, border=color, borderWidth=1)
        
def drawChallengeGameOver(app):
    drawRect(0, 0, app.width, app.height, fill='orange', opacity=75)
    win = getattr(app, 'challengeWin', False)
    if win:
        drawLabel('YOU WIN!', app.width/2, app.height/2 - 60, size=150, 
                  font='caveat', fill='lemonChiffon', border='lemonChiffon', borderWidth=2)
    else:
        drawLabel('TIME\'S UP!', app.width/2, app.height/2 - 60, size=150, 
                  font='caveat', fill='saddleBrown', border='saddleBrown', borderWidth=2)
    drawLabel("PRESS 'SPACE' TO RESTART", app.width/2, app.height/2 + 100,
              size=30, font='caveat', fill='saddleBrown', border='saddleBrown', borderWidth=1)
    
def challengeMode_onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        toggleSound(app)
    elif inBounds(mouseX,mouseY,20,10,100,35):
        setActiveScreen('selectModes')

def challengeMode_onMouseRelease(app,mouseX,mouseY):
    pass

def challengeMode_onMouseMove(app,mouseX,mouseY):
    if app.controller == 'mouse':
        app.cx = mouseX
        app.cy = mouseY
        app.trail.append((mouseX,mouseY))
        if len(app.trail) > 10:
            app.trail.pop(0)

def challengeMode_onKeyPress(app,key):
    if app.gameOver:
        if key == 'space':
            challengeRestart(app)
    pass
        
def challengeMode_onKeyRelease(app,keys):
    pass

def main():
    runAppWithScreens(initialScreen='home', width=950, height=535)
main()