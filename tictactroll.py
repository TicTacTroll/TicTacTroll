#!/usr/bin/python3
import cv2
import numpy as np
import random
import sys
import RPi.GPIO as GPIO
import time
import threading
from matplotlib import pyplot as plt
from picamera import PiCamera


camera = PiCamera()
patron_tablero = "tablero.png"
patron_ficha_o = "o.png"
extension = 1
ultima_imagen_juego = "game-picture-"+ str(extension) + ".jpg"
tiradesRobot = 0
arrayColzeEspatlla = [[110, 86],[100, 100],[98, 113],[85, 94],[70, 115],[65, 130],[66, 97],[50, 123],[45, 165]]
arrayPoscioPecesRobot = [[47, 99], [40, 110]]
MaABaix = 12
MaADalt = 160
servoPINColze = 4
servoPINEspatlla = 17
servoPINMa = 27
electroimanPIN = 12
soundPIN = 26
GPIO_TRIGGER = 18
GPIO_ECHO = 24

ultimaColze = 140
ultimaEspatlla = 140
ultimaMa = 30


GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPINEspatlla, GPIO.OUT)
GPIO.setup(servoPINColze, GPIO.OUT)
GPIO.setup(servoPINMa, GPIO.OUT)



#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


board=[i for i in range(0,9)]
player, computer = '',''

# Corners, Center and Others, respectively
moves=((1,7,3,9),(5,),(2,4,6,8))
# Winner combinations
winners=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
# Table
tab=range(1,10)

def print_board():
    x=1
    for i in board:
        end = ' | '
        if x%3 == 0:
            end = ' \n'
            if i != 1: end+='---------\n';
        char=' '
        if i in ('X','O'): char=i;
        x+=1
        print(char,end=end)

def select_char():
    chars=('O','X')
    return chars

def can_move(brd, player, move):
    if move in tab and brd[move-1] == move-1:
        return True
    return False

def can_win(brd, player, move):
    places=[]
    x=0
    for i in brd:
        if i == player: places.append(x);
        x+=1
    win=True
    for tup in winners:
        win=True
        for ix in tup:
            if brd[ix] != player:
                win=False
                break
        if win == True:
            break
    return win

def make_move(brd, player, move, undo=False):
    if can_move(brd, player, move):
        brd[move-1] = player
        win=can_win(brd, player, move)
        if undo:
            brd[move-1] = move-1
        return (True, win)
    return (False, False)

# AI goes here
def computer_move(no_move = 0):
    global tiradesRobot
    move=-1
    # If I can win, others don't matter.
    # print(board)
    for i in range(1,10):
        if make_move(board, computer, i, True)[1]:
            move=i
            break
    if move == -1:
        # If player can win, block him.
        for i in range(1,10):
            if make_move(board, player, i, True)[1]:
                move=i
                break
    if move == -1:
        # Otherwise, try to take one of desired places.
        for tup in moves:
            for mv in tup:
                if move == -1 and can_move(board, computer, mv):
                    move=mv
                    break
    print("computer move: " + str(move))
    if no_move == 0:
        if move != -1:
            robot_put_new_in(move)
            tiradesRobot += 1
        return make_move(board, computer, move)
    else:
        return move


def space_exist():
    return board.count('X') + board.count('O') != 9



def which_move():
    resetServos()
    global camera
    GPIO.setup(soundPIN, GPIO.OUT)
    output = GPIO.HIGH
    GPIO.output(soundPIN, output)
    time.sleep(0.1)
    output = GPIO.LOW
    GPIO.output(soundPIN, output)
    camera.start_preview()
    time.sleep(5)
    camera.capture('/home/pi/' + ultima_imagen_juego)
    camera.stop_preview()
    output = GPIO.HIGH
    GPIO.output(soundPIN, output)
    time.sleep(0.1)
    output = GPIO.LOW
    GPIO.output(soundPIN, output)
    time.sleep(0.2)
    output = GPIO.HIGH
    GPIO.output(soundPIN, output)
    time.sleep(0.1)
    output = GPIO.LOW
    GPIO.output(soundPIN, output)

    img = cv2.imread(ultima_imagen_juego,0)
    img2 = img.copy()
    template = cv2.imread(patron_tablero,0)
    w, h = template.shape[::-1]
    #print(template.shape[::-1])

    img = img2.copy()
    method = eval("cv2.TM_CCORR_NORMED")

    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    #print(res)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    crop_img = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    crop_img1 = crop_img[0:int((bottom_right[1]-top_left[1])/3), 0:int((bottom_right[0]-top_left[0])/3)]
    crop_img2 = crop_img[0:int(((bottom_right[1]-top_left[1])/3)*1), int((bottom_right[0]-top_left[0])/3):int(((bottom_right[0]-top_left[0])/3)*2)]
    crop_img3 = crop_img[0:int(((bottom_right[1]-top_left[1])/3)*1), int(((bottom_right[0]-top_left[0])/3)*2):int(((bottom_right[0]-top_left[0])/3)*3)]
    crop_img4 = crop_img[int((bottom_right[1]-top_left[1])/3):int(((bottom_right[1]-top_left[1])/3)*2), 0:int(((bottom_right[0]-top_left[0])/3))]
    crop_img5 = crop_img[int((bottom_right[1]-top_left[1])/3):int(((bottom_right[1]-top_left[1])/3)*2), int((bottom_right[0]-top_left[0])/3):int(((bottom_right[0]-top_left[0])/3)*2)]
    crop_img6 = crop_img[int((bottom_right[1]-top_left[1])/3):int(((bottom_right[1]-top_left[1])/3)*2), int(((bottom_right[0]-top_left[0])/3)*2):int(((bottom_right[0]-top_left[0])/3)*3)]
    crop_img7 = crop_img[int(((bottom_right[1]-top_left[1])/3)*2):int(((bottom_right[1]-top_left[1])/3)*3), 0:int(((bottom_right[0]-top_left[0])/3))]
    crop_img8 = crop_img[int(((bottom_right[1]-top_left[1])/3)*2):int(((bottom_right[1]-top_left[1])/3)*3), int(((bottom_right[0]-top_left[0])/3)*1):int(((bottom_right[0]-top_left[0])/3)*2)]
    crop_img9 = crop_img[int(((bottom_right[1]-top_left[1])/3)*2):int(((bottom_right[1]-top_left[1])/3)*3), int(((bottom_right[0]-top_left[0])/3)*2):int(((bottom_right[0]-top_left[0])/3)*3)]

    ArrayImatges = [crop_img1, crop_img2, crop_img3, crop_img4, crop_img5, crop_img6, crop_img7, crop_img8, crop_img9]
    ArrayReturnEstat = []
    for imatge in ArrayImatges:
        cv2.imwrite('temp.jpg', imatge)
        img_rgb = cv2.imread('temp.jpg')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(patron_ficha_o,0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.21
        loc = np.where( res >= threshold)
        #print(loc)
        if len(loc[0]) == 0:
            ArrayReturnEstat.append(0)
        else:
            ArrayReturnEstat.append(1)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

        #cv2.imwrite('res.png',img_rgb)
    print(ArrayReturnEstat)
    return ArrayReturnEstat

def moveServoToAction(servo, fromAngle, toAngle):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo,GPIO.OUT)
    pwm=GPIO.PWM(servo,50)
    pwm.start(7)
    if fromAngle < toAngle:
        for i in range(fromAngle, toAngle):
            DC=1./18.*(i)+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.05)
    else:
        for i in range(fromAngle,toAngle,-1):
            DC=1/18.*i+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.05)
    pwm.stop()
    # GPIO.cleanup()

def moveServoTo(servo, toAngle, avoidLowAngle = 0):
    global ultimaEspatlla
    global ultimaColze
    global ultimaMa
    fromAngle = -1
    if servo == servoPINEspatlla:
        fromAngle = ultimaEspatlla
        # moveServoTo(servoPINMa, MaADalt, 1)
    elif servo == servoPINColze:
        fromAngle = ultimaColze
        # moveServoTo(servoPINMa, MaADalt, 1)
    elif servo == servoPINMa:
        fromAngle = ultimaMa

    angleTemp = -1
    if abs(toAngle-fromAngle) < 40:
        if fromAngle >= 140:
            angleTemp = fromAngle - 40
        else:
            angleTemp = fromAngle + 40
    if avoidLowAngle == 1:
        angleTemp = -1
    if angleTemp != -1:
        moveServoToAction(servo, fromAngle, angleTemp)
        moveServoToAction(servo, angleTemp, toAngle)
    else:
        moveServoToAction(servo, fromAngle, toAngle)
    if servo == servoPINEspatlla:
        ultimaEspatlla = toAngle
    elif servo == servoPINColze:
        ultimaColze = toAngle
    elif servo == servoPINMa:
        ultimaMa = toAngle




def resetServos():
    global ultimaColze
    global ultimaEspatlla
    if ultimaColze != 180 or ultimaEspatlla !=180:
        moveServoTo(servoPINEspatlla, 180)
        moveServoTo(servoPINColze, 180)
        time.sleep(1)
    ultimaColze = 180
    ultimaEspatlla = 180

def moveColzeEspatlla(colzeAngle, EspatllaAngle):
    # moveServoTo(servoPINMa, MaADalt, 1)
    moveServoTo(servoPINColze, colzeAngle)
    moveServoTo(servoPINEspatlla, EspatllaAngle)

def activarElectroiman():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(electroimanPIN, GPIO.OUT)
    output = GPIO.HIGH
    GPIO.output(electroimanPIN, output)

def desactivarElectroiman():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(electroimanPIN, GPIO.OUT)
    output = GPIO.LOW
    GPIO.output(electroimanPIN, output)

def setServoCatch():
    global ultimaColze
    global MaABaix
    global MaADalt
    activarElectroiman()
    moveServoTo(servoPINMa, MaABaix, 1)
    time.sleep(0.3)
    moveServoTo(servoPINMa, MaABaix+8, 1)
    time.sleep(0.3)
    moveServoTo(servoPINColze, ultimaColze-8, 1)
    time.sleep(0.3)
    moveServoTo(servoPINMa, MaABaix, 1)
    time.sleep(0.3)
    moveServoTo(servoPINMa, MaABaix+8, 1)
    time.sleep(0.3)
    moveServoTo(servoPINColze, ultimaColze+24, 1)
    moveServoTo(servoPINMa, MaABaix, 1)
    moveServoTo(servoPINMa, MaADalt)

def setServoCatchHome():
    global ultimaColze
    global MaABaix
    global MaADalt
    activarElectroiman()
    # print(MaABaix)
    moveServoTo(servoPINMa, MaABaix, 1)
    time.sleep(0.3)
    # print(ultimaMa)
    moveServoTo(servoPINColze, ultimaColze-2, 1)
    time.sleep(0.3)
    moveServoTo(servoPINColze, ultimaColze+18, 1)
    time.sleep(0.3)
    moveServoTo(servoPINMa, MaABaix, 1)
    moveServoTo(servoPINMa, MaADalt)
    # print(MaADalt)
    # print(ultimaMa)
    time.sleep(0.3)
    # print("exit")

def setServoRelease():
    global ultimaColze
    global MaABaix
    global MaADalt
    moveServoTo(servoPINMa, MaABaix)
    desactivarElectroiman()
    moveServoTo(servoPINMa, MaADalt)

def robot_put_new_in(numCasella):
    resetServos()
    global tiradesRobot
    if tiradesRobot >= 2:
        moveColzeEspatlla(arrayPoscioPecesRobot[1][0], arrayPoscioPecesRobot[1][1])
    else:
        moveColzeEspatlla(arrayPoscioPecesRobot[0][0], arrayPoscioPecesRobot[0][1])
    setServoCatchHome()
    # moveServoTo(servoPINMa, MaADalt, 1)
    resetServos()
    moveColzeEspatlla(arrayColzeEspatlla[numCasella-1][0], arrayColzeEspatlla[numCasella-1][1])
    # moveServoTo(servoPINMa, MaADalt, 1)
    setServoRelease()
    resetServos()

def agafar_enemic_tirar_terra(numCasellaEnemic):
    global tiradesRobot
    resetServos()
    moveColzeEspatlla(arrayColzeEspatlla[numCasellaEnemic-1][0], arrayColzeEspatlla[numCasellaEnemic-1][1])
    setServoCatch()
    resetServos()
    setServoRelease()
    if tiradesRobot >= 2:
        moveColzeEspatlla(arrayPoscioPecesRobot[1][0], arrayPoscioPecesRobot[1][1])
    else:
        moveColzeEspatlla(arrayPoscioPecesRobot[0][0], arrayPoscioPecesRobot[0][1])
    setServoCatchHome()
    # moveServoTo(servoPINMa, MaADalt, 1)
    resetServos()
    moveColzeEspatlla(arrayColzeEspatlla[numCasellaEnemic-1][0], arrayColzeEspatlla[numCasellaEnemic-1][1])
    # moveServoTo(servoPINMa, MaADalt, 1)
    setServoRelease()
    resetServos()

def ferTrampa():
    print("fertrampa")
    move = -1
    contador = 0
    haTocat = random.randint(0,1)
    boardCopy = board.copy()
    for element in board:
        contador += 1
        if element == 'O':
            board[contador-1] = contador-1
    # print(board)
    if haTocat == 1:
        # print("haTocat == 1")
        move = computer_move(1)
        print(move)
        if move != -1:
            agafar_enemic_tirar_terra(move)
            soGuanyador()

def testejarCasella(numCasella):
    count = 1
    for colzeEspatlla in arrayColzeEspatlla:
        if count == numCasella:
            moveColzeEspatlla(colzeEspatlla[0], colzeEspatlla[1])
            primercas = 0
            setServoCatch()
            time.sleep(2)
        count += 1
def testejarTotesCaselles2():
    primercas = 1
    for colzeEspatlla in arrayColzeEspatlla:
        resetServos()
        moveColzeEspatlla(colzeEspatlla[0], colzeEspatlla[1])
        if primercas == 0:
            setServoRelease()
        primercas = 0
        setServoCatch()

def testejarTotesCaselles():
    for colzeEspatlla in arrayColzeEspatlla:
        resetServos()
        moveColzeEspatlla(colzeEspatlla[0], colzeEspatlla[1])
        setServoRelease()
        moveServoTo(servoPINMa, MaADalt, 1)
def soGuanyador():
    GPIO.setup(soundPIN, GPIO.OUT)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    #1
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    #2
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)

def soGuanyador2():
    GPIO.setup(soundPIN, GPIO.OUT)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    #1
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)

    GPIO.setup(soundPIN, GPIO.OUT)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    #1
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)


def enfadat():
    GPIO.setup(soundPIN, GPIO.OUT)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.75)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.375)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.125)
    GPIO.output(soundPIN, GPIO.HIGH)
    time.sleep(0.75)
    GPIO.output(soundPIN, GPIO.LOW)
    time.sleep(0.375)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime

    distance = (TimeElapsed * 34300) / 2

    return distance

def control_distancia():
        try:
            while True:
                dist = distance()
                # print ("Measured Distance = %.1f cm" % dist)
                if dist > 500 or dist < 7:
                    enfadat()
                time.sleep(1)

            # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            GPIO.cleanup()







player, computer = select_char()
print('Jugador: [%s], ordinador: [%s].' % (player, computer))
result='=== Empat ! ==='
startDistanceLoop = threading.Thread(target=control_distancia)
startDistanceLoop.start()
try:
    while space_exist():
        detected_next_move = 0
        what_was_move = -1
        print_board()
        moveServoTo(servoPINMa, MaADalt, 1)
        resetServos()

        while detected_next_move == 0:
            counterPostion = 0
            time.sleep(5)
            arrayReturn = which_move()
            for movement in arrayReturn:
                counterPostion +=1
                if movement == 1:
                    if board[counterPostion-1] != 'X' and board[counterPostion-1] != 'O':
                        what_was_move = counterPostion
                        detected_next_move = 1
        moved, won = make_move(board, player, what_was_move)
        if not moved:
            print(' >> Invalid number ! Try again !')
            continue

        if won:
            result='=== Has guanyat ! ==='
            enfadat()
            break
        elif computer_move()[1]:
            result='=== Has perdut ! =='
            soGuanyador2()
            break;
except KeyboardInterrupt:
    GPIO.cleanup()

print_board()
if result == '=== Empat ! ===':
    enfadat()
    ferTrampa()
print(result)
