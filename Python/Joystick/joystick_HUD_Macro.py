#!/usr/bin/python
import pygame, sys, os
import pygame.locals as pgl
from time import sleep, time
from collections import deque
import numpy as np
currentpath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(currentpath)
from TBotTools import tbt, pgt

starttime = time()
PlayMacro = 0
RecordMacro = 0
DeleteMacro = 0

clock = pygame.time.Clock()
t1 = 0
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
#bd_addr = '98:D3:51:FD:81:AC' # use: 'hcitool scan' to scan for your T-Bot address
bd_addr = '98:D3:32:21:3D:77'
# bd_addr = '98:D3:91:FD:46:C9' # B
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
    
    
    
    
def send(sendstr,sendcount,cmd_write):
    global starttime
    sendcount = btcom.send_data(sendstr,sendcount)
    if cmd_write:
        f2.write(str(time()-starttime)+','+sendstr+'\n')
    starttime = time()
    return sendcount


def playmacro(filename,sendcount):
    try:
        ff = open(filename)
        cmd_data = ff.readlines()
        ff.close()
            
        for ii in range(len(cmd_data)):
            aa = cmd_data[ii].split(',')
            dtime = float(aa[0])
            cmsstr = aa[1]
            sleep(dtime)
            sendcount = btcom.send_data(cmsstr,sendcount)
    except:
        print('The cmd.csv file does not exist. Try recording a macro first.')

        
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')
RED = pygame.Color('red')
#-----------------------------------------------------------------------
#                        Initialize PyGame
#-----------------------------------------------------------------------
pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((900, 590))

bg = pygame.image.load(dirpath+'/HUD/Controller7.png').convert()


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

spotB = pygame.image.load(dirpath+'/HUD/spotT.png')
spotT = pygame.image.load(dirpath+'/HUD/spotB.png')

stick = pygame.image.load(dirpath+'/HUD/stick.png')

L1 = pygame.image.load(dirpath+'/HUD/L1.png')
L2 = pygame.image.load(dirpath+'/HUD/L2.png')
L1L2 = pygame.image.load(dirpath+'/HUD/L1L2.png')
R1 = pygame.image.load(dirpath+'/HUD/R1.png')
R2 = pygame.image.load(dirpath+'/HUD/R2.png')
R1R2 = pygame.image.load(dirpath+'/HUD/R1R2.png')


posdpad = (295,340)
posbpad = (520,340)
posstickL = (358, 395)
posstickR = (480,395)
posL = (302,282)
posR = (531,282)

spotTorigin = (123,145)
spotBorigin = (765,145)
spotV = np.array([0,-62])



pygame.display.set_caption("Player 1")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = pgt.TextPrint(WHITE)

readdataevent = pygame.USEREVENT+1
pygame.time.set_timer(readdataevent, 33)
# -------- Main Program Loop -----------

joystick = pygame.joystick.Joystick(0)
joystick.init()
joystick_count = pygame.joystick.get_count()
name = joystick.get_name()
axes = joystick.get_numaxes()
hats = joystick.get_numhats()
while not done:
    if pygame.event.get(readdataevent):
        oldvals = btcom.get_data(oldvals)

    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.

    if event.type == pgl.KEYDOWN and event.key == pgl.K_q:
        done = True

    if event.type == pgl.KEYDOWN and event.key == pgl.K_t:
        WHITE = pygame.Color('white')
        
        themelist = ["bg = pygame.image.load(dirpath+'/HUD/Controller.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller2.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller3.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller4.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller5.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller6.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/Controller7.png').convert()",
                    "bg = pygame.image.load(dirpath+'/HUD/ControllerI.png').convert()"]
        exec(themelist[t1])
        if t1 == 7:
            WHITE = BLACK
        textPrint.setColour(WHITE)
            
        
        #pygame.image.save(screen, "CapturedImages/{:02d}.png".format(t1))
        if t1 == 7:
            t1 = 0
        else:
            t1 += 1
    

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
    

    textPrint.abspos(screen, "Number of joysticks: {}".format(joystick_count),(20,280))
    textPrint.indent()

    textPrint.tprint(screen, "Joystick name: {}".format('Generic Controller'))
    
    textPrint.tprint(screen, "")
    textPrint.tprint(screen, "Number of axes: {}".format(axes))
    textPrint.indent()
    textPrint.unindent()
    
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
        pygame.draw.lines(screen, WHITE, False, (gdata),1)
        
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
    textPrint.tprint(screen, "{} FPS".format(str(int(clock.get_fps()))))   

    textPrint.unindent()


    textPrint.abspos(screen, "www.klikrobotics.com",(20,20))
#
# #############   Send data to T-Bot  ##############################
#
    if abs(axis0)+abs(axis1)+abs(axis2)+abs(axis3) != 0:
        slowfactor = 1
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
     
        sendstring = str(turn)+str(speed)+'Z'
        sendcount = send(sendstring,sendcount,RecordMacro)
    else:
        turn = 200
        speed = 200
        sendstring = str(turn)+str(speed)+'Z'
        sendstring = '200200Z'
        sendcount = send(sendstring,sendcount,RecordMacro)

        
    
    theta = np.arctan((speed-200,speed-200))
    rmat = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    spotTpos = tuple(spotTorigin+np.dot(rmat,np.array([spotV]).T).T[0].astype(int))
    theta = -theta-np.pi
    rmat = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    spotTpos2 = tuple(spotTorigin+np.dot(rmat,np.array([spotV]).T).T[0].astype(int))

    
    theta2 = np.arctan((turn-200,turn-200))+np.pi/2
    rmat = np.array([[np.cos(theta2),-np.sin(theta2)],[np.sin(theta2),np.cos(theta2)]])
    spotBpos = tuple(spotBorigin+np.dot(rmat,np.array([spotV]).T).T[0].astype(int))
    rmat = np.array([[np.cos(-theta2),-np.sin(-theta2)],[np.sin(-theta2),np.cos(-theta2)]])
    spotBpos2 = tuple(spotBorigin+np.dot(rmat,np.array([spotV]).T).T[0].astype(int))
    
    screen.blit(spotT,spotTpos)
    screen.blit(spotT,spotTpos2)
    screen.blit(spotB,spotBpos)
    screen.blit(spotB,spotBpos2)   
        
    if joystick.get_button(0):
        buttonstring = '200200F' # trim +ve
        sendcount = send(buttonstring,sendcount,RecordMacro)
    elif joystick.get_button(2):
        buttonstring = '200200E' # trim -ve
        sendcount = send(buttonstring,sendcount,RecordMacro)

    elif joystick.get_button(1):
        buttonstring = '200200B' # kps +ve
        sendcount = send(buttonstring,sendcount,RecordMacro)
    elif joystick.get_button(3):
        buttonstring = '200200A' # kps -ve
        sendcount = send(buttonstring,sendcount,RecordMacro)
    elif joystick.get_button(9):
        buttonstring = '200200T' # kps -ve
        sendcount = send(buttonstring,sendcount,RecordMacro)

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
        RecordMacro = 1
        f2= open('cmd.csv','a')
        
    elif joystick.get_button(6):
        screen.blit(L2,posL)
        RecordMacro = 0
        f2.close()

    elif joystick.get_button(5):
        screen.blit(R1,posR)
        PlayMacro = 1
        
    elif joystick.get_button(7):
        screen.blit(R2,posR)
        DeleteMacro = 1
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
    
    textPrint.abspos(screen, "Press T to change Theme",(20,470))
    textPrint.tprint(screen, "L1 - Record")
    textPrint.tprint(screen, "L2 - Stop Recording")
    textPrint.tprint(screen, "R1 - Play Macro")
    textPrint.tprint(screen, "R2 - Delete Macro")
        
    textPrint.setColour(RED)
    textPrint.setfontsize(20)
    if RecordMacro:
        textPrint.tprint(screen, 'Recording Macro')
    if PlayMacro:
        if RecordMacro == 0:
            textPrint.tprint(screen, 'Locked - Playing Macro')
            pygame.display.flip()
            playmacro('cmd.csv',sendcount)
            PlayMacro = 0
        else:
            textPrint.tprint(screen, 'Stop Recording First')
            
    if DeleteMacro:
        if RecordMacro == 0:
            f2= open('cmd.csv','w')
            f2.close()
            DeleteMacro = 0
        else:
            textPrint.tprint(screen, 'Stop Recording First')
            
        
    textPrint.setColour(WHITE)
    textPrint.setfontsize(15)    
    
    
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(30)

# Close the window and quit.

pygame.quit()
btcom.connect(0)
print('Connection Closed')
