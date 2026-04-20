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
        self.slicedPiecces = []

    def draw(self):
        drawImage(self.image, self.x, self.y, width=self.width, height=self.height, 
                  rotateAngle=self.rotate, align='center')
    
    def updatePosition(self,app):
        self.x += self.dx  * app.sloMoFactor
        self.y += self.dy * (app.sloMoFactor)
        self.dy += self.gravity * app.sloMoFactor
    
    def isLegal(self,app):
        return self.y<app.height+75 and not self.sliced

def onAppStart(app):
    app.showFontWarnings = False
    # CV AND MEDIAPIPE SETUP (USED AI - GEMINI)
    setupHandTracker(app)
    app.cap = cv2.VideoCapture(0)
    app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    restart(app)

    app.stepsPerSecond = 60
    app.steps = 0
    app.highScore = 0
    app.soundIsPlaying = True
    app.showHomeScreen = True

    app.beach = 'FULL BG.png'
    app.playBG = 'Play BG.png'
    app.sound = Sound('Beach Song.mp3')
    app.woodSign = 'Wood Sign.png'
    app.surfboards = 'Surfboards.png'
    app.sliceSound = Sound('SliceSound.mp3')

    app.width = 950
    app.height = 535
    app.spawnRate = 0.07
    app.sloMo = False
    app.sloMoTimer = 0  
    app.sloMoFactor = 1

def restart(app):
    app.handX, app.handY = app.width/2, app.height/2
    app.targetHandCoords = [app.width/2, app.height/2]
    app.trail = []
    app.score = 0   
    app.gameStarted = True
    app.showInstructions = False
    app.gameOver = False
    app.livesLeft = 3
    app.unslicedFruits = []
    app.showGameModes = False

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

def onMousePress(app,mouseX,mouseY):
    if inBounds(mouseX,mouseY,830,10,100,35):
        app.soundIsPlaying = not app.soundIsPlaying
    elif inBounds(mouseX,mouseY,20,10,100,35):
        app.gameStarted = False
        app.showInstructions = False
        app.showHomeScreen = True
    elif app.showHomeScreen:
        if inBounds(mouseX,mouseY,260,400,175,75):
            app.showGameModes = True
            app.gameStarted = True
            app.showHomeScreen = False
        elif inBounds(mouseX,mouseY,500,400,175,75):
            app.showInstructions = True
            app.showHomeScreen = False

def inBounds(mouseX,mouseY,x,y,width,height):
    return (x<=mouseX<=x+width) and (y<=mouseY<=y+height)

def onKeyPress(app,key):
    if app.gameOver:
        if key == 'space' and not app.showHomeScreen:
            restart(app)
        elif key == 'h':
            app.gameStarted = False
            app.showInstructions = False
            app.showHomeScreen = True

def onStep(app):
    app.steps += 1
    app.handX += (app.targetHandCoords[0] - app.handX) * 0.5
    app.handY += (app.targetHandCoords[1] - app.handY) * 0.5
    app.trail.append((app.handX, app.handY))
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

    if app.gameStarted and not app.showInstructions and not app.gameOver:
        if random.random() < app.spawnRate:
            loadNextFruit(app)
        for fruit in app.unslicedFruits:
            fruit.updatePosition(app)
            if distance(app.handX, app.handY, fruit.x, fruit.y) < max(fruit.width, fruit.height)/2:
                if not fruit.sliced:
                    fruit.sliced = True
                    if fruit.name == 'torch':
                        app.livesLeft -= 1
                        if app.livesLeft == 0:
                            app.gameOver = True
                    elif fruit.name == 'flower':
                        app.sloMo = True
                        app.sloMoFactor = 0.5
                    else:
                        app.score += 10
                        app.sliceSound.play()
                    if app.score > app.highScore:
                        app.highScore = app.score
        remaining = []
        for fruit in app.unslicedFruits:
            if fruit.isLegal(app):
                remaining.append(fruit)
            else:
                if not fruit.sliced and fruit.name not in ['torch', 'flower']:
                    app.score = max(0, app.score - 5)
        app.unslicedFruits = remaining
    if (app.steps%app.stepsPerSecond == 0) and app.sloMo:
        app.sloMoTimer += 1
        if app.sloMoTimer == 3:
            app.sloMo = False
            app.sloMoTimer = 0
            app.sloMoFactor = 1

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
    flowerChance = 0.03
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

def drawButtons(app):
    drawRect(830,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('SOUND',880,26,font='caveat',fill='lemonChiffon',
              size=22,border='lemonChiffon',borderWidth=1)
    if app.gameStarted or app.showInstructions:
        drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel('HOME',70,26,font='caveat',fill='lemonChiffon',
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
    drawButtons(app)

def drawLives(app):
    for i in range(app.livesLeft):
        drawImage('Heart.png', 675 + i*40, 7, width=30, height=30)

def drawGameOverScreen(app):
    drawRect(0,0,app.width,app.height,fill='orange',opacity=75)
    drawImage('flames.png', 0, 0, width=app.width, height=app.height,opacity=50)
    drawLabel('GAME OVER',app.width/2,app.height/2,size=175,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=2)
    drawLabel(f'HIGH: {app.highScore}',app.width/2 - app.width/6,app.height/2+120,size=50,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawLabel(f'SCORE: {app.score}',app.width/2 + app.width/6,app.height/2+120,size=50,font='caveat',fill='saddleBrown',
                border='saddleBrown',borderWidth=1)
    drawLabel("PRESS 'SPACE' TO RESTART OR 'H' TO RETURN HOME",app.width/2,app.height/2+190,
              size=25,font='caveat',fill='saddleBrown', border='saddleBrown',borderWidth=1)
    
def drawSloMoEffect(app):
    drawRect(0, 0, app.width, app.height, fill='hotPink', opacity=25)
    drawImage('sloMoBG.jpg', 0, 0, width=app.width, height=app.height, opacity=40)

def redrawAll(app):
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()
    if app.showHomeScreen:
        drawImage(app.beach,0,0,width=950,height=535)
        drawImage(app.woodSign,60,60,width=800,height=580)
        drawLabel('SANDBOX',475,200,size=145,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
        drawLabel('- SLICER -',475,325,size=120,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
        drawRect(260,400,175,75,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        drawRect(500,400,175,75,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        drawLabel('PLAY!',345,433,font='caveat',fill='lemonChiffon',size=45,border='lemonChiffon',borderWidth=2)
        drawLabel('INSTRUCTIONS',590,433,font='caveat',fill='lemonChiffon',size=25,border='lemonChiffon',borderWidth=2)
        drawImage(app.surfboards,720,200,width=260,height=420)
    elif app.showInstructions:
        drawInstructions(app)
    else:
        drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
        for fruit in app.unslicedFruits:
            fruit.draw()

        drawRect(200,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'HIGH: {app.highScore}',275,26,font='caveat',fill='lemonChiffon',
                  size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawRect(450,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'{app.score}',525,26,font='caveat',fill='lemonChiffon',
                  size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawLives(app)
        drawTrail(app)
        drawCircle(app.handX, app.handY, 8, fill=gradient('pink','mediumVioletRed', 'fuchsia'),
                   border='pink',borderWidth=2)
        if app.gameOver:
            drawGameOverScreen(app)
        drawButtons(app)
        if app.sloMo:
            drawSloMoEffect(app)

def main():
    runApp(width=950,height=535)
main()