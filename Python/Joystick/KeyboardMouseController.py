#!/usr/bin/python
#------------------------ Import Libraries ----------------------------#

import pygame, sys, pygame.mixer, os
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from pygame.locals import *
from time import sleep, time
import bluetooth as bt
from TBotTools import tbt, pgt
from collections import deque
import numpy as np
starttime = time()

#---------------------- Setup for rolling plot  -----------------------#

xdatarange = [280,480]
y_origin = 100
yscale = 100
posarrows = (740, 480)
pts = deque(maxlen=xdatarange[1]-xdatarange[0])

for ii in range(xdatarange[0],xdatarange[1]):
    pts.appendleft((ii,np.random.rand(1)))
iii = 200
aa = np.zeros((len(pts),2))
aa[:,1]=np.array(pts)[:,1]
aa[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
bb=np.copy(aa)

#----------------------------------------------------------------------#   

dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'
timestart = time()
speedfactor = 0.6
speedlimit = 70
turnspeedlimit = 60
mx,my = 0,0
mx_origin,my_origin = 450, 425
mxnew, mynew = 250, 250
#-----------------------  Setup Bluetooth   ---------------------------#

oldvals = [0,0,0,0]
sendcount = 0

#----------------------------------------------------------------------#
#                     For Linux / Raspberry Pi
#----------------------------------------------------------------------#

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

#----------------------------------------------------------------------#
#                       For Windows and Mac
#----------------------------------------------------------------------#

#port = 'COM5'
#port = '/dev/tty.George-DevB'
#baudrate = 38400
#bd_addr = 'Empty'
#btcom = tbt.bt_connect(bd_addr,port,'PySerial',baudrate)

 #------------------     Define some colors  ---------------------------#

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')

pygame.init()

#------- Set the width and height of the screen (width, height) -------#

screen = pygame.display.set_mode((900, 590))

#--------------------   Load Artwork  ---------------------------------#



bg = pygame.image.load(dirpath+'/HUD/JoystickBG.png').convert()
bgG = pygame.image.load(dirpath+'/HUD/offline.png').convert()
arrowkeys = pygame.image.load(dirpath+'/arrowkeys.png')
arrowkeysL = pygame.image.load(dirpath+'/arrowkeysL.png')
arrowkeysR = pygame.image.load(dirpath+'/arrowkeysR.png')
arrowkeysUp = pygame.image.load(dirpath+'/arrowkeysUp.png')
arrowkeysDown = pygame.image.load(dirpath+'/arrowkeysDown.png')
arrowkeysUL = pygame.image.load(dirpath+'/arrowkeysUL.png')
arrowkeysUR = pygame.image.load(dirpath+'/arrowkeysUR.png')
arrowkeysDL = pygame.image.load(dirpath+'/arrowkeysDL.png')
arrowkeysDR = pygame.image.load(dirpath+'/arrowkeysDR.png')
joytop = pygame.image.load(dirpath+'/joysticktopSmall.png')
joybase = pygame.image.load(dirpath+'/joystickbase_250.png')


colour = (0,0,0,0)
pygame.display.set_caption("Player 1")

#---------- Loop until the user clicks the close button ---------------#
done = False

#---------- Used to manage how fast the screen updates  ---------------#

clock = pygame.time.Clock()

#------------------ Initialize the joysticks  -------------------------#

pygame.joystick.init()

#-----------------------  Print to Window -----------------------------#

textPrint = pgt.TextPrint(WHITE)


# ---------------------- Main Program Loop ----------------------------#

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
        #screen.fill(colour)
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
        print('Plotting Interupted')

    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].max()),[xdatarange[0],y_origin-20])
    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].min()),[xdatarange[0],y_origin+yscale+5])
    
    keys = pygame.key.get_pressed()

    screen.blit(arrowkeys,posarrows)
    
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
                   
    mx,my = pygame.mouse.get_pos()

    #print('x '+str(mx)+' y ' +str(my))
    c1, c2, c3 =  pygame.mouse.get_pressed()
          
        
    if mx > mx_origin + 115 or mx < mx_origin - 115 or my > my_origin+115 or my < my_origin-115:
        mx,my = mx_origin,my_origin

    jx = int(((mx-mx_origin-116)*0.862)+300)
    jy = int((((116+my_origin)-my)*0.862)+100)

    if mxnew != mx or mynew != my:   
        
        if c1==1:
            sendstring = str(jx)+str(jy)
            
        else:
            if np.sum(keys)==0:
                sendstring = '200200Z'      
        mxnew = mx
        mynew = my
        sendcount = btcom.send_data(sendstring,sendcount)

    if c1==0 and np.sum(keys)==0:
        sendcount = btcom.send_data('200200Z',sendcount) 
    
    screen.blit(joybase,(mx_origin-125,my_origin-125))
    screen.blit(joytop,(mx-40,my-40))    
    textPrint.abspos(screen, "T-Bot Keyboard Controller",(500,85))
    textPrint.indent()        
    textPrint.tprint(screen, "gyrodata: {}".format(str(oldvals[3])))
    textPrint.tprint(screen, "kps: {} - j/k".format(str(oldvals[0])))
    textPrint.tprint(screen, "kp: {}".format(str(oldvals[1])))
    textPrint.tprint(screen, "trim: {} - r/t or y for Auto".format(str(oldvals[2])))
    textPrint.tprint(screen, "Speed Factor: {} - s/w".format(str(speedfactor)))
    textPrint.tprint(screen, "Speed Limit: {}% - a/d".format(str(speedlimit)))
    textPrint.tprint(screen, "x, y: {}, {}".format(str(mx-mx_origin),str(my-my_origin)))
    textPrint.tprint(screen, "jx, jy: {}, {}".format(str(jx),str(jy)))
    textPrint.unindent()


#-----------------------   Send data to T-Bot   -----------------------#
        
    # Update the screen with what we've drawn.

    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
