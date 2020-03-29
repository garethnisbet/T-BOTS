#!/usr/bin/python
import pygame, sys, pygame.mixer, os
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from pygame.locals import *
from time import sleep, time
import bluetooth as bt
from TBotTools import tbt
from collections import deque
import numpy as np
import threading
import Queue
import cv2


cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)




response_to_send_que = Queue.Queue()
rcv_data_que = Queue.Queue()
starttime = time()

# setup for plotting
xdatarange = [280,520]
y_origin = 100
yscale = 100
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


      
        
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((900, 590))

bg = pygame.image.load(dirpath+'/HUD/Controller.png').convert()
#bg = pygame.image.load(dirpath+'/HUD/ControllerTemplate.png').convert()
bgG = pygame.image.load(dirpath+'/HUD/offline.png').convert()
dpad = pygame.image.load(dirpath+'/HUD/dpad.png')
dpadU = pygame.image.load(dirpath+'/HUD/dpadU.png')
dpadD = pygame.image.load(dirpath+'/HUD/dpadD.png')
dpadL = pygame.image.load(dirpath+'/HUD/dpadL.png')
dpadR = pygame.image.load(dirpath+'/HUD/dpadR.png')
dpadUR = pygame.image.load(dirpath+'/HUD/dpadUR.png')
dpadDR = pygame.image.load(dirpath+'/HUD/dpadDR.png')
dpadUL = pygame.image.load(dirpath+'/HUD/dpadUL.png')
dpadDL = pygame.image.load(dirpath+'/HUD/dpadDL.png')

bpad = pygame.image.load(dirpath+'/HUD/bpad.png')
bpadU = pygame.image.load(dirpath+'/HUD/bpadU.png')
bpadD = pygame.image.load(dirpath+'/HUD/bpadD.png')
bpadL = pygame.image.load(dirpath+'/HUD/bpadL.png')
bpadR = pygame.image.load(dirpath+'/HUD/bpadR.png')
bpadUR = pygame.image.load(dirpath+'/HUD/bpadUR.png')
bpadDR = pygame.image.load(dirpath+'/HUD/bpadDR.png')
bpadUL = pygame.image.load(dirpath+'/HUD/bpadUL.png')
bpadDL = pygame.image.load(dirpath+'/HUD/bpadDL.png')

stick = pygame.image.load(dirpath+'/HUD/stick.png')


posdpad = (295,340)
posbpad = (520,340)
posstickL = (358, 395)
posstickR = (480,395)




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
        
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
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
            
    success, frame = cap.read()
    frame = cv2.resize(frame, (int(320/1.2), int(240/1.2)))
    canvas = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')
    screen.blit(canvas,(270,50))
    

    
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for i in [0]: # If you have multiple joysticks connected, set this index for the one you want to use.
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.abspos(screen, "Joystick {}".format(i),(20,280))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick.
        name = joystick.get_name()
        textPrint.tprint(screen, "Joystick name: {}".format(name))
        #textPrint.tprint(screen, "Joystick name: {}".format('Generic Controller'))
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.tprint(screen, "")
        textPrint.tprint(screen, "Number of axes: {}".format(axes))
        textPrint.indent()
        textPrint.unindent()
        hats = joystick.get_numhats()
        textPrint.tprint(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        axis0 = joystick.get_axis(0)
        axis1 = joystick.get_axis(1)
        axis2 = joystick.get_axis(2)
        axis3 = joystick.get_axis(3)
        textPrint.unindent()
        textPrint.tprint(screen, "")
        buttons = joystick.get_numbuttons()
        
        textPrint.abspos(screen, "Number of buttons: {}".format(buttons),(710,280))
        textPrint.tprint(screen, "")
        for i in range(buttons):
            button = joystick.get_button(i)
            textPrint.tprint(screen,
                             "Button {:>2} value: {}".format(i, button))


        # Hat position. All or nothing for direction, not a float like
        # get_axis(). Position is a tuple of int values (x, y).
        for i in range(hats):
            hat = joystick.get_hat(i)
            textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
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


                

        getdata = threading.Thread(target=lambda q, arg1: q.put(btcom.get_data(oldvals)), args=(rcv_data_que,'make_iterable,'))
        getdata.start()
        #getdata.join()
        oldvals = rcv_data_que.get()

        
        
        #g_angle = (oldvals[3]*20/255)-10 # Conversion from scaled output from T-Bot
        g_angle = oldvals[3]
        pts.appendleft((iii,g_angle))
        iii+=1
        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin+0.5*yscale),(xdatarange[1],y_origin+0.5*yscale)),1)
        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin),(xdatarange[0],y_origin+yscale)),1)
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
        
        
        
        textPrint.abspos(screen, "T-Bot Data",(550,85))
        textPrint.tprint(screen, "")
        textPrint.tprint(screen, "gyrodata: {}".format(str(oldvals[3])))
        textPrint.tprint(screen, "kps: {}".format(str(oldvals[0])))
        textPrint.tprint(screen, "kp: {}".format(str(oldvals[1])))
        textPrint.tprint(screen, "trim: {}".format(str(oldvals[2])))
        textPrint.tprint(screen, "Speed Factor: {}".format(str(speedfactor)))
        textPrint.tprint(screen, "Speed Limit: {}%".format(str(speedlimit)))

        textPrint.unindent()

    #
    # #############   Send data   #################################
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

        else:
            sendstring = '200200Z'

        if joystick.get_button(0):
            sendstring = '200200F' # trim +ve

        elif joystick.get_button(2):
            sendstring = '200200E' # trim -ve


        elif joystick.get_button(1):
            sendstring = '200200B' # kps +ve

        elif joystick.get_button(3):
            sendstring = '200200A' # kps -ve

        elif joystick.get_button(9):
            buttonstring = '200200T' # kps -ve
            
        senddata = threading.Thread(target=lambda q, arg1: q.put(btcom.send_data(sendstring,sendcount)), args=(response_to_send_que,'make_iterable,'))
        senddata.start()
        #senddata.join()
        sendcount = response_to_send_que.get()



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
        elif hat[0] == -1 & hat[1] == 1:
            screen.blit(dpadUL,posdpad)
        elif hat[0] == 1 & hat[1] == -1:
            screen.blit(dpadDR,posdpad)
        elif hat[0] == 1 & hat[1] == 1:
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
        elif joystick.get_button(0) & joystick.get_button(1):
            screen.blit(bpadUR,posbpad)
        elif joystick.get_button(1) & joystick.get_button(2):
            screen.blit(bpadDR,posbpad)
        elif joystick.get_button(2) & joystick.get_button(3):
            screen.blit(bpadDL,posbpad)
        elif joystick.get_button(0) & joystick.get_button(3):
            screen.blit(bpadUL,posbpad)

        
    # Go ahead and update the screen with what we've drawn.
    #modelr = pygame.transform.rotate(model,-g_angle)
    #screen.blit(logo,(20,480))
    
    #blitRotate(screen, model, (260,160), (75,75), -g_angle)
    #screen.blit(modelr,(230,100))    

    
    
    pygame.display.flip()


    # Limit to 20 frames per second.
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
