#!/usr/bin/python
import pygame, sys, pygame.mixer, os
from pygame.locals import *
from time import sleep, time
import bluetooth as bt
from TBotClasses import tbt
from collections import deque
import numpy as np
starttime = time()

# setup for plotting
xdatarange = [200,320]
y_origin = 30
posarrows = (30, 150)
yscale = 50
pts = deque(maxlen=xdatarange[1]-xdatarange[0])
for ii in range(xdatarange[0],xdatarange[1]):
    pts.appendleft((ii,np.random.rand(1)))
iii = 200
aa = np.zeros((len(pts),2))
aa[:,1]=np.array(pts)[:,1]
aa[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
bb=np.copy(aa)
    

dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'
timestart = time()
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
#bd_addr = '98:D3:91:FD:46:C9' # B
#bd_addr = '98:D3:32:21:3D:A2' # Foxy
#bd_addr = '98:D3:91:FD:46:9C' # T-Bot
#bd_addr = '98:D3:32:21:3D:77' # Cinemon
#bd_addr = '98:D3:51:FD:82:95' # 	George
port = 1
btcom = tbt.bt_connect(bd_addr,port,'PyBluez')
#btcom = tbt.bt_connect(bd_addr,port,'Socket')

#------------------------------------------------------------------
#               For Windows and Mac
#------------------------------------------------------------------
#port = 'COM5'
#port = '/dev/tty.George-DevB'
#baudrate = 38400
#bd_addr = 'Empty'
#btcom = tbt.bt_connect(bd_addr,port,'PySerial',baudrate)


###################  Screen Text Class #############################

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
        textBitmap = self.font.render(textString, True, WHITE)
        screen.blit(textBitmap, pos)
    
 

###################  Instantiate BT Class #############################    


      
        
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((350, 230))
logo = pygame.image.load(dirpath+'/logo.png')
bg = pygame.image.load(dirpath+'/hexMini.jpg').convert()
bgG = pygame.image.load(dirpath+'/hexGMini.jpg').convert()


arrowkeys = pygame.image.load(dirpath+'/arrowkeys.png')
arrowkeysL = pygame.image.load(dirpath+'/arrowkeysL.png')
arrowkeysR = pygame.image.load(dirpath+'/arrowkeysR.png')
arrowkeysUp = pygame.image.load(dirpath+'/arrowkeysUp.png')
arrowkeysDown = pygame.image.load(dirpath+'/arrowkeysDown.png')
arrowkeysUL = pygame.image.load(dirpath+'/arrowkeysUL.png')
arrowkeysUR = pygame.image.load(dirpath+'/arrowkeysUR.png')
arrowkeysDL = pygame.image.load(dirpath+'/arrowkeysDL.png')
arrowkeysDR = pygame.image.load(dirpath+'/arrowkeysDR.png')

pygame.display.set_caption("Player 1")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()

# -------- Main Program Loop -----------

while not done:
        

    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
            btcom.connect(0)
            print('Connection Closed')
    if event.type == KEYDOWN and event.key == K_q:
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



                
    oldvals = btcom.get_data(oldvals)
    #g_angle = (oldvals[3]*20/255)-10 # Conversion from scaled output from T-Bot
    g_angle = oldvals[3]
    pts.appendleft((iii,g_angle))
    iii+=1
    pygame.draw.lines(screen, (4,150,7), False, ((xdatarange[0],y_origin+0.5*yscale),(xdatarange[1],y_origin+0.5*yscale)),1)
    pygame.draw.lines(screen, (5,150,7), False, ((xdatarange[0],y_origin),(xdatarange[0],y_origin+yscale)),1)
    if iii > xdatarange[1]:
        iii = xdatarange[0]
    aa[:,1]=np.array(pts)[:,1]
    try:  
        bb[:,1] = (yscale/((aa[:,1]-aa[:,1].max()).min())*(aa[:,1]-aa[:,1].max()))+y_origin
        gdata = tuple(map(tuple, tuple(bb)))
        pygame.draw.lines(screen, (255,255,255), False, (gdata),1)
        
    except:
        b=1
        

    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].max()),[xdatarange[0],y_origin-20])
    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].min()),[xdatarange[0],y_origin+yscale+5])
    

    

    keys = pygame.key.get_pressed()

    screen.blit(arrowkeys,posarrows)
    
    # Images for arrow keys 

    if keys[K_RIGHT] and keys[K_UP]:
        screen.blit(arrowkeysUR,posarrows)
        sendstring = '%03d%03dZ'%(240,200+(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)

    elif keys[K_LEFT] and keys[K_UP]:
        screen.blit(arrowkeysUL,posarrows)
        sendstring = '%03d%03dZ'%(160,200+(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)
        
    elif keys[K_RIGHT] and keys[K_DOWN]:
        screen.blit(arrowkeysDR,posarrows)
        sendstring = '%03d%03dZ'%(260,200-(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)
        
    elif keys[K_LEFT] and keys[K_DOWN]:
        screen.blit(arrowkeysDL,posarrows)
        sendstring = '%03d%03dZ'%(140,200-(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)

    elif keys[K_DOWN]:
        screen.blit(arrowkeysDown,posarrows)
        sendstring = '%03d%03dZ'%(200,200-(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)
        
    elif keys[K_UP]:
        screen.blit(arrowkeysUp,posarrows)
        sendstring = '%03d%03dZ'%(200,200+(speedfactor*100))
        sendcount = btcom.send_data(sendstring,sendcount)

    elif keys[K_RIGHT]:
        screen.blit(arrowkeysR,posarrows)
        sendstring = '260200Z'
        sendcount = btcom.send_data(sendstring,sendcount)

    elif keys[K_LEFT]:
        screen.blit(arrowkeysL,posarrows)
        sendstring = '140200Z'
        sendcount = btcom.send_data(sendstring,sendcount)
        
        
    elif keys[K_t]:
        buttonstring = '200200F' # trim +ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif keys[K_r]:
        buttonstring = '200200E' # trim -ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif keys[K_k]:
        buttonstring = '200200B' # kps +ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif keys[K_j]:
        buttonstring = '200200A' # kps -ve
        sendcount = btcom.send_data(buttonstring,sendcount)
    elif keys[K_y]:
        buttonstring = '200200T' # Auto trim
        sendcount = btcom.send_data(buttonstring,sendcount)

    elif keys[K_w]:
        
        speedfactor +=0.1
        if speedfactor > 1:
            speedfactor = 1.0
        
    elif keys[K_s]:
        speedfactor -=0.1
        if speedfactor < 0.1:
            speedfactor = 0.1
            
    elif keys[K_a]:
        
        speedlimit -=5
        if speedlimit > 100:
            speedlimit = 100
        
    elif keys[K_d]:
        speedlimit += 5
        if speedlimit < 0:
            speedlimit = 0
    else:
        sendstring = '200200Z'
        sendcount = btcom.send_data(sendstring,sendcount)       
     



    textPrint.tprint(screen, "T-Bot Keyboard Controller")
    textPrint.indent()
        
    textPrint.tprint(screen, "gyrodata: {}".format(str(oldvals[3])))
    textPrint.tprint(screen, "kps: {} - j/k".format(str(oldvals[0])))
    textPrint.tprint(screen, "kp: {}".format(str(oldvals[1])))
    textPrint.tprint(screen, "trim: {} - r/t or y for Auto".format(str(oldvals[2])))
    textPrint.tprint(screen, "Speed Factor: {} - s/w".format(str(speedfactor)))
    textPrint.tprint(screen, "Speed Limit: {}% - a/d".format(str(speedlimit)))

    textPrint.unindent()

#
# #############   Send data   #################################
#


        
    # Go ahead and update the screen with what we've drawn.
    screen.blit(logo,(215,120))
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
