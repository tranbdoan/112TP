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

    def draw(self):
        drawImage(self.image, self.x, self.y, width=self.width, height=self.height, rotateAngle=self.rotate, align='center')
    
    def updatePosition(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
    
    def isLegal(self,app):
        return self.height<app.height+100 and not self.sliced

def onAppStart(app):
    # CV AND MEDIAPIPE SETUP
    setupHandTracker(app)
    app.cap = cv2.VideoCapture(0)
    app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # GAME STATE VARIABLES
    app.stepsPerSecond = 60
    app.handX, app.handY = 475, 260
    app.targetHandCoords = [475,260]
    app.trail = []
    app.score = 0   
    app.highScore = 0
    app.gameStarted = False
    app.showInstructions = False
    app.gameOver = False
    app.soundIsPlaying = True
    app.livesLeft = 3

    # BG AND UI
    app.beach = 'FULL BG.png'
    app.playBG = 'Play BG.png'
    app.sound = Sound('Beach Song.mp3')

    # FRUITS AND DECOR
    app.fruits = []

    app.width = 950
    app.height = 535
    app.spawnRate = 0.07

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
    elif not app.gameStarted:
        if inBounds(mouseX,mouseY,260,340,200,100):
            app.gameStarted = True
        elif inBounds(mouseX,mouseY,500,340,200,100):
            app.showInstructions = not app.showInstructions

def inBounds(mouseX,mouseY,x,y,width,height):
    return (x<=mouseX<=x+width) and (y<=mouseY<=y+height)

def onStep(app):
    app.handX += (app.targetHandCoords[0] - app.handX) * 0.5
    app.handY += (app.targetHandCoords[1] - app.handY) * 0.5
    app.trail.append((app.handX, app.handY))
    if len(app.trail) > 10:
        app.trail.pop(0)
    # lines 103-109 used AI
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
        for fruit in app.fruits:
            fruit.updatePosition()
            if distance(app.handX, app.handY, fruit.x, fruit.y) < max(fruit.width, fruit.height)/2:
                if not fruit.sliced:
                    app.score += 10
                    fruit.sliced = True
                if app.score > app.highScore:
                    app.highScore = app.score
        app.fruits = [fruit for fruit in app.fruits if fruit.isLegal(app)]

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
    name = random.choice(list(fruits.keys()))
    image, width, height = fruits[name]
    x0 = random.randint(100, 800)
    y0 = app.height 
    newFruit = Fruit(name, image, x0, y0, width, height)
    app.fruits.append(newFruit)

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

def redrawAll(app):
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()
    if not app.gameStarted:
        drawImage(app.beach,0,0,width=950,height=535)
        if app.showInstructions:
            drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
            drawLabel('HOW TO PLAY:',470,95,font='caveat',size = 70,fill='saddleBrown',
                      border='saddleBrown',borderWidth=1)
    else:
        drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
        for fruit in app.fruits:
            fruit.draw()

        drawRect(250,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'HIGH: {app.highScore}',295,26,font='caveat',fill='lemonChiffon',
                  size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawRect(550,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'{app.score}',625,26,font='caveat',fill='lemonChiffon',
                  size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawTrail(app)
        drawCircle(app.handX, app.handY, 8, fill=gradient('pink','mediumVioletRed', 'fuchsia'),
                   border='pink',borderWidth=2)
    drawButtons(app)

def main():
    runApp(width=950,height=535)
main()