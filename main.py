from cmu_graphics import * 
import random

def onAppStart(app):
    songURL = 'cmu://1166089/46424597/Beach+Theme+-+Super+Mario+Bros.+Wonder+OST.mp3'
    app.sound = Sound(songURL)
    app.soundIsPlaying = True
    app.surfboards = 'cmu://1166089/46424547/boards.png'
    # app.palmTree = 'cmu://1166089/46424978/856741bfee38ebdb1aec5f78ed9c713f.gif'
    app.palmTree = 'cmu://1166089/46424523/551-5518286_palm-tree-clipart-borders-cartoon-palm-tree-transparent.png;'
    app.drinks = 'cmu://1166089/46424467/pngtree-summer-beach-drinks-surfboards-watermelon-shell-flat-style-png-image_15561778.png'
    app.beach = 'cmu://1166089/46424357/360_F_277079720_pRGT81JFRtcOTqDUOtuvfEKAScdXFbEv.jpg'
    app.sign = 'cmu://1166089/46424382/pngtree-cartoon-hand-drawn-watercolor-brand-wooden-sign-png-image_551050+(1).png'
    app.backgroundURL= 'cmu://1166089/46422960/112+TP+Background.png'
    app.fruitCenters = []
    app.pineapple = 'cmu://1166089/46423677/vecteezy_pineapple-fruit-cartoon-illustration-isolated-on-transparent_47130664.png'
    app.dragonfruit = 'cmu://1166089/46423722/pngimg.com+-+pitaya_PNG39.png'
    app.kiwi = 'cmu://1166089/46423818/vibrant-kiwi-slice-illustration-eklixauo5drmhzwt.png'
    app.coconut = 'cmu://1166089/46423941/coconut-575780_1280.png'
    app.orange = 'cmu://1166089/46424008/pngimg.com+-+orange_PNG751.png'
    app.mango = 'cmu://1166089/46424029/5ul06s21m7hor9h7sw5o93w031oi.png'
    app.banana = 'cmu://1166089/46424057/8-84869_vector-banana-png-image-download-bananas-cartoon-png.png'
    app.flower = 'cmu://1166089/46424126/pngtree-hibiscus-flower-clipart-pink-hibiscus-flower-cartoon-vector-png-image_12157044.png'
    app.torch = 'cmu://1166089/46424134/pngtree-burning-cartoon-torch-illustration-png-image_15615612.png'
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

def redrawAll(app):
    if app.soundIsPlaying:
        app.sound.play(loop=True)
    else:
        app.sound.pause()
    if not app.gameStarted:
        drawImage(app.beach,0,0,height=535)
        drawImage(app.palmTree,625,0,height=535)
        drawImage(app.sign,60,60,width=800,height=580)
        drawLabel('SANDBOX',475,240,size=140,font='caveat',fill='lemonChiffon',border='lemonChiffon',borderWidth=3)
        drawRect(260,340,200,100,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        drawRect(500,340,200,100,fill='burlyWood',border='lemonChiffon',borderWidth=5)
        drawLabel('PLAY!',360,390,font='caveat',fill='lemonChiffon',size=60,border='lemonChiffon',borderWidth=2)
        drawLabel('INSTRUCTIONS',600,390,font='caveat',fill='lemonChiffon',size=30,border='lemonChiffon',borderWidth=2)
        drawImage(app.drinks,-110,220,width=380,height=380)
        drawImage(app.surfboards,720,200,width=260,height=420)
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

        
def main():
    runApp(width=950,height=535)
main()