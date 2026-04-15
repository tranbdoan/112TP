from cmu_graphics import * 
import random
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

def onAppStart(app):
    # --- MediaPipe Setup ---
    model_path = 'hand_landmarker.task'
    base_options = python.BaseOptions(model_asset_path=model_path)
    
    # 1. Define the Callback Function inside onAppStart
    def update_hand_position(result, output_image, timestamp_ms):
        if result.hand_landmarks:
            # We use app.group to allow the callback to talk to the app
            tip = result.hand_landmarks[0][8]
            app.handX = tip.x * app.width
            app.handY = tip.y * app.height

    # 2. Set mode to LIVE_STREAM
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        result_callback=update_hand_position # Tell it where to send the data
    )
    app.detector = vision.HandLandmarker.create_from_options(options)
    # app.stepsPerSecond = 100
    app.cap = cv2.VideoCapture(0)
    app.handX, app.handY = 475, 260
    songURL = 'Beach Song.mp3'
    app.sound = Sound(songURL)
    app.soundIsPlaying = True
    app.surfboards = 'Surfboards.png'
    app.palmTree = 'Palm Tree.png'
    app.drinks = 'Drinks.png'
    app.beach = 'FULL BG.png'
    app.sign = 'Wood Sign.png'
    app.backgroundURL= 'Play BG.png'
    app.fruitCenters = []
    app.pineapple = 'Pineapple.png'
    app.dragonfruit = 'Dragonfruit.png'
    app.kiwi = 'Kiwi.png'
    app.coconut = 'Coconut.png'
    app.orange = 'Orange.png'
    app.mango = 'Mango.png'
    app.banana = 'Banana.png'
    app.flower = 'Flower.png'
    app.torch = 'Torch.png'
    app.highScore = 0
    app.score = 0
    app.soundOn = True
    app.gameStarted = False
    app.showInstructions = False
    app.gameOver = False
    app.speed = None

def onMousePress(app,mouseX,mouseY):
    if (830<=mouseX<=930) and (10<=mouseY<=45):
        app.soundIsPlaying = not app.soundIsPlaying
    elif (20<=mouseX<=120) and (10<=mouseY<=45):
        app.gameStarted = False
        app.showInstructions = False
    elif app.gameStarted == False:
        if (260<=mouseX<=460) and (340<=mouseY<=440):
            app.gameStarted = True
        elif (500<=mouseX<=700) and (340<=mouseY<=440):
            app.showInstructions = not app.showInstructions


def onStep(app):
    success, frame = app.cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # 3. Use detect_async
        # This sends the frame and immediately moves on. No waiting!
        timestamp_ms = int(time.time() * 1000)
        app.detector.detect_async(mp_image, timestamp_ms)
def redrawAll(app):
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()
    if not app.gameStarted:
        drawImage(app.beach,0,0,width=950,height=535)
        # drawImage(app.palmTree,625,0,height=535)
        # drawImage(app.sign,60,60,width=800,height=580)
        # drawLabel('SANDBOX',475,240,size=140,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
        # drawRect(260,340,200,100,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        # drawRect(500,340,200,100,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        # drawLabel('PLAY!',360,390,font='caveat',fill='lemonChiffon',size=60,border='lemonChiffon',borderWidth=2)
        # drawLabel('INSTRUCTIONS',600,390,font='caveat',fill='lemonChiffon',size=30,border='lemonChiffon',borderWidth=2)
        # drawImage(app.drinks,-110,220,width=380,height=380)
        # drawImage(app.surfboards,720,200,width=260,height=420)
        if app.showInstructions:
            backgroundWidth, backgroundHeight = getImageSize(app.backgroundURL)
            drawImage(app.backgroundURL, 0, 0,
                  width=backgroundWidth//1.01, height=backgroundHeight//1.15)
            drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
            drawLabel('HOME',70,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1)
            drawLabel('HOW TO PLAY:',470,95,font='caveat',size = 70,fill='saddleBrown',border='saddleBrown',borderWidth=1)
    else:
        backgroundWidth, backgroundHeight = getImageSize(app.backgroundURL)
        drawImage(app.backgroundURL, 0, 0,
              width=backgroundWidth//1.01, height=backgroundHeight//1.15)
        drawImage(app.pineapple, 200,50,  width=100, height=100)
        drawImage(app.dragonfruit,40,300,width=65,height=65)
        drawImage(app.kiwi,550,200,width=45,height=45)
        drawImage(app.coconut,400,300,width = 50,height =50)
        drawImage(app.orange,500,400,width=50,height=50)
        drawImage(app.mango,250,400,width=80,height=60,rotateAngle=-20)
        drawImage(app.banana,350,200,width=55,height=55)
        drawImage(app.flower,425,140,width = 60,height=60)
        drawImage(app.torch,780,150,width=120,height=120,rotateAngle=-45)
        drawRect(20,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel('HOME',70,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawRect(250,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'HIGH: {app.highScore}',295,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1,align='center')
        drawRect(550,10,150,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
        drawLabel(f'{app.score}',625,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1,align='center')
    drawRect(830,10,100,35,fill='burlyWood',border='lemonChiffon',borderWidth=2)
    drawLabel('SOUND',880,26,font='caveat',fill='lemonChiffon',size=22,border='lemonChiffon',borderWidth=1)
    drawCircle(app.handX, app.handY, 10, fill='cyan', border='blue', borderWidth=2)

        
def main():
    runApp(width=950,height=535)
main()