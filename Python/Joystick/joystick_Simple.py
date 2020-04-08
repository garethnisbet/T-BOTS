#!/usr/bin/python
import pygame
import pygame.locals as pgl
import sys, os

import numpy as np
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import tbt

clock = pygame.time.Clock()

dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'
# setup for plotting

speedfactor = 0.6
speedlimit = 70
turnspeedlimit = 60

###################  Setup Bluetooth   #############################

oldvals = [0,0,0,0]
sendcount = 0

#------------------------------------------------------------------
#               For Linux / Raspberry Pi
#------------------------------------------------------------------
bd_addr = '98:D3:51:FD:81:AC' # use: 'hcitool scan' to scan for your T-Bot address
#bd_addr = '98:D3:32:21:3D:77'
port = 1
#btcom = tbt.bt_connect(bd_addr,port,'PyBluez')
btcom = tbt.bt_connect(bd_addr,port,'Socket')

#------------------------------------------------------------------
#               For Windows and Mac
#------------------------------------------------------------------
#port = 'COM5'
#port = '/dev/tty.George-DevB'
#baudrate = 38400
#bd_addr = 'Empty'
#btcom = tbt.bt_connect(bd_addr,port,'PySerial',baudrate)


#######################  Screen Text Class #############################

class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 15)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, WHITE)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10
        
    def abspos(self,screen, textString, pos):
        self.x = pos[0]
        self.y = pos[1]
        textBitmap = self.font.render(textString, True, WHITE)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height
 

###################  Instantiate BT Class #############################    

WHITE = pygame.Color('white')

pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((512, 294))

bg = pygame.image.load(dirpath+'/Simple/Controller.png').convert()
bgG = pygame.image.load(dirpath+'/Simple/Offline.png').convert()
dpad = pygame.image.load(dirpath+'/Simple/dpad.png')
dpadU = pygame.image.load(dirpath+'/Simple/dpadU.png')
dpadD = pygame.image.load(dirpath+'/Simple/dpadD.png')
dpadL = pygame.image.load(dirpath+'/Simple/dpadL.png')
dpadR = pygame.image.load(dirpath+'/Simple/dpadR.png')
dpadUR = pygame.image.load(dirpath+'/Simple/dpadUR.png')
dpadDR = pygame.image.load(dirpath+'/Simple/dpadDR.png')
dpadUL = pygame.image.load(dirpath+'/Simple/dpadUL.png')
dpadDL = pygame.image.load(dirpath+'/Simple/dpadDL.png')

bpad = pygame.image.load(dirpath+'/Simple/bpad.png')
bpadU = pygame.image.load(dirpath+'/Simple/bpadU.png')
bpadD = pygame.image.load(dirpath+'/Simple/bpadD.png')
bpadL = pygame.image.load(dirpath+'/Simple/bpadL.png')
bpadR = pygame.image.load(dirpath+'/Simple/bpadR.png')
bpadUR = pygame.image.load(dirpath+'/Simple/bpadUR.png')
bpadDR = pygame.image.load(dirpath+'/Simple/bpadDR.png')
bpadUL = pygame.image.load(dirpath+'/Simple/bpadUL.png')
bpadDL = pygame.image.load(dirpath+'/Simple/bpadDL.png')

stick = pygame.image.load(dirpath+'/Simple/stick.png')

L1 = pygame.image.load(dirpath+'/Simple/L1.png')
L2 = pygame.image.load(dirpath+'/Simple/L2.png')
L1L2 = pygame.image.load(dirpath+'/Simple/L1L2.png')
R1 = pygame.image.load(dirpath+'/Simple/R1.png')
R2 = pygame.image.load(dirpath+'/Simple/R2.png')
R1R2 = pygame.image.load(dirpath+'/Simple/R1R2.png')

offset = (190,60)
posdpad = (102, 75)
posbpad = (327, 75)
posstickL = (165, 130)
posstickR = (287, 130)
posL = (108,15)
posR = (337,15)


pygame.display.set_caption("Player 1")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joystick.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()


readdataevent = pygame.USEREVENT+1
pygame.time.set_timer(readdataevent, 50)

joystick = pygame.joystick.Joystick(0)
joystick.init()
name = joystick.get_name()
axes = joystick.get_numaxes()
hats = joystick.get_numhats()

# -------- Main Program Loop -----------

while not done:
        
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
            btcom.connect(0)
            print('Connection Closed')
    if event.type == pgl.KEYDOWN and event.key == pgl.K_q:
        btcom.connect(0)
        pygame.display.quit()
        sys.exit()
        print('Connection Closed')
        pass   

    if btcom.connected():
        screen.blit(bg, [0, 0])
    else:
        tries = 0
        while btcom.connected() < 1 and tries < 10:
            print('Connecting ...')
            screen.blit(bgG, [0, 0])
            pygame.display.flip()
            try:
                print('Try '+str(tries+1)+' of 10')
                btcom.connect(0)
                btcom.connect(1)
                tries+=1
            except:
                print('Something went wrong')
                
        if btcom.connected() < 1:
            print('Exiting Program')
            pygame.display.quit()
            sys.exit()
        else:
            tries = 0
    
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    # Get the name from the OS for the controller/joystick.
    
    axis0 = joystick.get_axis(0)
    axis1 = joystick.get_axis(1)
    axis2 = joystick.get_axis(2)
    axis3 = joystick.get_axis(3)
  
    for i in range(hats):
        hat = joystick.get_hat(i)
        #textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
        if hat[1] == 1:
            speedfactor += 0.1
        elif hat[1] == -1:
            speedfactor -= 0.1
        elif hat[0] == -1:
            speedlimit -= 5
        elif hat[0] == +1:
            speedlimit += 5
        if speedlimit >= 100:
            speedlimit = 100
        if speedlimit <= 0:
            speedlimit = 0
        if speedfactor >= 5:
            speedfactor = 5
        if speedfactor <= 0:
            speedfactor = 0
            
    textPrint.unindent()
    
    if pygame.event.get(readdataevent):
        oldvals = btcom.get_data(oldvals)

    textPrint.abspos(screen, "Gyro Data: {}".format(str(oldvals[3])),(10,10))
    textPrint.tprint(screen, "KPS: {}".format(str(oldvals[0])))
    textPrint.tprint(screen, "KP: {}".format(str(oldvals[1])))
    textPrint.tprint(screen, "Trim: {}".format(str(oldvals[2])))
    
    textPrint.abspos(screen, "Speed Factor: {}".format(str(speedfactor)),(415,10))
    textPrint.tprint(screen, "Speed Limit: {}%".format(str(speedlimit)))
    textPrint.tprint(screen, "{} FPS".format(str(int(clock.get_fps()))))   

    textPrint.unindent()


# #############   Send data to T-Bot  ##############################
#
    if abs(axis0)+abs(axis1)+abs(axis2)+abs(axis3) != 0:
        slowfactor = 1+joystick.get_button(7)
        turn = 200+int(((axis0+(axis2*0.5))*speedfactor*100/slowfactor))
        speed = 200-int(((axis1+(axis3*0.5))*speedfactor*100/slowfactor))
        if speed > 200+speedlimit:
            speed = 200+speedlimit
        if speed < 200-speedlimit:
            speed = 200-speedlimit

        if turn > 200+turnspeedlimit:
            turn = 200+turnspeedlimit
        if turn < 200-turnspeedlimit:
            turn = 200-turnspeedlimit
        cmdwrite = 1       
        sendstring = str(turn)+str(speed)+'Z'
        sendcount = btcom.send_data(sendstring,sendcount)
    else:
        turn = 200
        speed = 200
        sendstring = str(turn)+str(speed)+'Z'
        sendstring = '200200Z'
        sendcount = btcom.send_data(sendstring,sendcount)
        
        
    if joystick.get_button(0):
        buttonstring = '200200F' # trim +ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif joystick.get_button(2):
        buttonstring = '200200E' # trim -ve
        sendcount = btcom.send_data(buttonstring,sendcount)

    elif joystick.get_button(1):
        buttonstring = '200200B' # kps +ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif joystick.get_button(3):
        buttonstring = '200200A' # kps -ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif joystick.get_button(9):
        buttonstring = '200200T' # kps -ve
        sendcount = btcom.send_data(buttonstring,sendcount)

    # ------------------ Highlight buttons ----------------#
    screen.blit(dpad,posdpad)
    screen.blit(bpad,posbpad)
    screen.blit(stick,(posstickL[0]+axis0*5,posstickL[1]+axis1*5))
    screen.blit(stick,(posstickR[0]+axis2*5,posstickR[1]+axis3*5))
    
    if hat[0] == 1:
        screen.blit(dpadR,posdpad)
    elif hat[0] == -1:
        screen.blit(dpadL,posdpad)
    elif hat[1] == 1:
        screen.blit(dpadU,posdpad)
    elif hat[1] == -1:
        screen.blit(dpadD,posdpad)
    else:
        screen.blit(dpad,posdpad)
        
    if (hat[0] == -1) & (hat[1] == 1):
        screen.blit(dpadUL,posdpad)
    elif (hat[0] == 1) & (hat[1] == -1):
        screen.blit(dpadDR,posdpad)
    elif (hat[0] == 1 & hat[1] == 1):
        screen.blit(dpadUR,posdpad)
    elif hat[0] == -1 & hat[1] == -1:
        screen.blit(dpadDL,posdpad)
        
    if joystick.get_button(0):
        screen.blit(bpadU,posbpad)
    elif joystick.get_button(1):
        screen.blit(bpadR,posbpad)
    elif joystick.get_button(2):
        screen.blit(bpadD,posbpad)
    elif joystick.get_button(3):
        screen.blit(bpadL,posbpad)
    else:
        screen.blit(bpad,posbpad)
        
    if joystick.get_button(0) & joystick.get_button(1):
        screen.blit(bpadUR,posbpad)
    elif joystick.get_button(1) & joystick.get_button(2):
        screen.blit(bpadDR,posbpad)
    elif joystick.get_button(2) & joystick.get_button(3):
        screen.blit(bpadDL,posbpad)
    elif joystick.get_button(0) & joystick.get_button(3):
        screen.blit(bpadUL,posbpad)

    if joystick.get_button(4):
        screen.blit(L1,posL)
    elif joystick.get_button(6):
        screen.blit(L2,posL)
    elif joystick.get_button(5):
        screen.blit(R1,posR)
    elif joystick.get_button(7):
        screen.blit(R2,posR)
    else:
        screen.blit(bpad,posbpad)
        
    if joystick.get_button(4) & joystick.get_button(6):
        screen.blit(L1L2,posL)
    elif joystick.get_button(5) & joystick.get_button(7):
        screen.blit(R1R2,posR)
    elif joystick.get_button(4) & joystick.get_button(5):
        screen.blit(L1,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(4) & joystick.get_button(7):
        screen.blit(L1,posL)
        screen.blit(R2,posR)
    elif joystick.get_button(6) & joystick.get_button(5):
        screen.blit(L2,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L2,posL)
        screen.blit(R2,posR)
        
    if joystick.get_button(4) & joystick.get_button(6) & joystick.get_button(5):
        screen.blit(L1L2,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(4) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L1L2,posL)
        screen.blit(R2,posR)
    elif joystick.get_button(4) & joystick.get_button(5) & joystick.get_button(7):
        screen.blit(L1,posL)
        screen.blit(R1R2,posR)
    elif joystick.get_button(5) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L2,posL)
        screen.blit(R1R2,posR) 
    
    if joystick.get_button(4) & joystick.get_button(5) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L1L2,posL)
        screen.blit(R1R2,posR)


    pygame.display.flip()

    # Limit to 30 frames per second.
    clock.tick(30)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
