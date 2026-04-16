from cmu_graphics import * 
import random
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

class Fruit:
    def __init__(self, name, image,x, y, width, height,rotate=0):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.rotate = rotate
    
    def draw(self):
        drawImage(self.image, self.x, self.y, width=self.width, height=self.height, rotateAngle=self.rotate)

def onAppStart(app):
    # CV AND MEDIAPIPE SETUP
    setupHandTracker(app)
    app.cap = cv2.VideoCapture(0)
    app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # GAME STATE VARIABLES
    app.stepsPerSecond = 60
    app.handX, app.handY = 475, 260
    app.score = 0   
    app.highScore = 0
    app.gameStarted = False
    app.showInstructions = False
    app.gameOver = False
    app.soundIsPlaying = True

    # BG AND UI
    app.beach = 'FULL BG.png'
    app.playBG = 'Play BG.png'
    app.sound = Sound('Beach Song.mp3')

    # FRUITS AND DECOR
    app.fruits = [
        Fruit('pineapple', 'Pineapple.png', 200, 50, 100, 170),
        Fruit('dragonfruit', 'Dragonfruit.png', 40, 300, 80, 80),
        Fruit('kiwi', 'Kiwi.png', 550, 200, 70, 70),
        Fruit('coconut', 'Coconut.png', 400, 300, 60, 60),
        Fruit('orange', 'Orange.png', 500, 400, 70, 70),
        Fruit('mango', 'Mango.png', 250, 400, 60, 80),
        Fruit('banana', 'Banana.png', 350, 200, 80, 80),
        Fruit('flower', 'Flower.png', 425, 140, 90, 90),
        Fruit('torch', 'Torch.png', 780, 150, 150, 150, rotate=-45)
    ]

def setupHandTracker(app):
    model_path = 'hand_landmarker.task'
    base_options = python.BaseOptions(model_asset_path=model_path)
    def update_hand_position(result, output_image, timestamp_ms):
        if result.hand_landmarks:
            tip = result.hand_landmarks[0][8]
            targetX = tip.x * app.width
            targetY = tip.y * app.height
            app.handX += (targetX - app.handX) * 0.5
            app.handY += (targetY - app.handY) * 0.5
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
    success, frame = app.cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(time.time() * 1000)
        app.detector.detect_async(mp_image, timestamp_ms)

def drawButtons(app):
    drawRect(830,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('SOUND',880,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1)
    if app.gameStarted or app.showInstructions:
        drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel('HOME',70,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1)

def redrawAll(app):
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()
    if not app.gameStarted:
        drawImage(app.beach,0,0,width=950,height=535)
        if app.showInstructions:
            drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
            drawLabel('HOW TO PLAY:',470,95,font='caveat',size = 70,fill='saddleBrown',border='saddleBrown',borderWidth=1)
    else:
        drawImage(app.playBG, 0, 0, width=app.width, height=app.height)
        for fruit in app.fruits:
            fruit.draw()

        drawCircle(app.handX, app.handY, 8, fill=gradient('mediumVioletRed', 'fuchsia'),border='pink',borderWidth=1)

        drawRect(250,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'HIGH: {app.highScore}',295,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawRect(550,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'{app.score}',625,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawCircle(app.handX, app.handY, 8, fill=gradient('mediumVioletRed', 'fuchsia'),border='pink',borderWidth=1)
    drawButtons(app)

def main():
    runApp(width=950,height=535)
main()