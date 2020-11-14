import sys
import cv2
import os
import imutils
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))
sys.path.append(path_above)
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from TBotTools import tbt, pid, geometry, pgt
from scipy.interpolate import interp1d
from time import time
plt.ion()
import bluetooth as bt
from datetime import datetime
import pygame
from pygame.locals import *
from sys import exit
import pygame
import pygame.gfxdraw
pygame.init()
textPrint = pgt.TextPrint((255,255,255))
textPrint.setlineheight(25)
scalefactor = 1
#origin =  [636/2,357/2]
origin =  [0,0]
showline = 0
drawplot = 1
interpfactor = 5
flag = 0
geom = geometry.geometry(1) # scale factor to convert pixels to mm

bb = np.array([[0,0,],[0,1],[1,1],[2,0],[3,0],[4,0],[3,0],[2,0],[1,0]])
########################################################################
#-----------------------   Draw            ----------------------------#
########################################################################
filename = 'pathpoints.dat'
if os.path.isfile(filename):
    aa = np.loadtxt(filename)
    aa[:,0] = aa[:,0]*scalefactor+origin[0]
    aa[:,1] = aa[:,1]*scalefactor+origin[1] 
    coordinate = list(tuple(map(tuple,aa.astype(int))))
else:
    coordinate = []

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)
cap.set(14, 10) # gain

success, frame = cap.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
cap.release()
pygame.init()
screen0 = pygame.display.set_mode((633, 359), 0, 0)
canvas = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')

x = []
y = []
x2 = []
y2 = []
starttime = []
endtime = []
laptime = 1000
oldlaptime = 500


textstr = ''
textstr2 = ''

pathindex = 0
timeflag = 0
pathindex = 0
bendscalefactor = 10
rdeadban = 2
tolerance = 30


# sets the length of the trail
pts = deque(maxlen=10)
pts2 = deque(maxlen=10)


#----------------------------------------------------------------------#
#                        Set HSV Thresholds
#            Use getHSVThresh.py to find the correct values
#
#                        Artificial Lighting
#----------------------------------------------------------------------#

greenLower = (66,40,141)    # place green disc on the left
greenUpper = (88,255,255) 
 
pinkLower = (124,47,22)       
pinkUpper = (164,255,255) # place pink disc on the right

#----------------------------------------------------------------------#
#                                  Sunny
#----------------------------------------------------------------------#

#greenLower = (49,13,202)	
#greenUpper = (82,121,225)

#pinkLower = (142,54,146)    
#pinkUpper = (255,255,255)  

#----------------------------------------------------------------------#


#----------------------------------------------------------------------#
#                                  Dull
#----------------------------------------------------------------------#

#greenLower = (60,55,216)	
#greenUpper = (80,255,255)

#pinkLower = (126,33,210)    
#pinkUpper = (255,255,255)  

#----------------------------------------------------------------------#





#--------------------  Define functions  ------------------------------#


#--------------------- Setup Bluetooth --------------------------------#
data = [0,0,0,0]
sendcount = 0

#------------------------------------------------------------------
#               For Linux / Raspberry Pi
#------------------------------------------------------------------
# bd_addr = '98:D3:51:FD:81:AC' # use: 'hcitool scan' to scan for your T-Bot address
# bd_addr = '98:D3:51:FD:82:95' # George
# bd_addr = '98:D3:91:FD:46:C9' # B
#bd_addr = '98:D3:32:21:3D:77'
bd_addr = '98:D3:71:FD:44:F7'
port = 1
btcom = tbt.bt_connect(bd_addr,port,'PyBluez') # PyBluez works well for the Raspberry Pi
#btcom = tbt.bt_connect(bd_addr,port,'Socket')

#----------------------------------------------------------------------#
#               For Windows and Mac
#----------------------------------------------------------------------#
#port = 'COM5'
#port = '/dev/tty.George-DevB'
#baudrate = 38400
#bd_addr = 'Empty'
#btcom = tbt.bt_connect(bd_addr,port,'PySerial',baudrate)


#-----------------  Generate target function  -------------------------#

amplitude = 80
frequency = 1
phase = 0
stepsize = 5
border = 80 # sets the number of pixels from the edge which wont be occupied by the function.
bg = frame.shape[0]/2 # this is the background of the sin function

#----------   Create mask for coordinates   ------------#
xdata =  np.arange(border, frame.shape[1]-border, stepsize)

aa = np.loadtxt('pathpoints.dat') # Use Click2Path.py to create an arbitrary path

if interpfactor != 1:
    print('Interpolating data')
    xdata = range(aa.shape[0])
    x_hires = np.linspace(xdata[0],(xdata[-1]-1),len(xdata)*interpfactor)
    f1 = interp1d(xdata,aa[:,0], kind = 'cubic')
    f2 = interp1d(xdata,aa[:,1], kind = 'cubic')
    y1 = f1(x_hires)
    y2 = f2(x_hires)
    aa = np.concatenate(([y1],[y2])).T


########################################################################
#-----------------------   Start main loop ----------------------------#
########################################################################

cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
cap.set(14, 10) # gain
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)


oldtime = time()
done = 0

screen = pygame.display.set_mode((640, 700))

# sets the length of the trail
pts = deque(maxlen=100)
pts2 = deque(maxlen=100)

pathindex = 0

bendscalefactor = 10
rdeadban = 2
tolerance = 30

rotspeed = 200
speedfactor = 0.3

dt = 0.005

feedforward = 2
pkp_o = 2.02
pki_o = 0.4
pkd_o = 0
akp_o = 0.68
aki_o = 0.4
akd_o = 0.01
FW_o = 2
FW = FW_o
FW_old = FW_o
pkp_old = pkp_o
pki_old = pki_o
pkd_old = pkd_o
akp_old = akp_o
aki_old = aki_o
akd_old = akd_o


sbar = pgt.SliderBar(screen, (100,455), pkp_o, 440, 5, 6, (200,200,200),(255,10,10))
sbar2 = pgt.SliderBar(screen, (100,480), pki_o, 440, 5, 6, (200,200,200),(255,10,10))
sbar3 = pgt.SliderBar(screen, (100,505), pkd_o, 440, 0.5, 6, (200,200,200),(255,10,10))

sbar4 = pgt.SliderBar(screen, (100,555), akp_o, 440, 5, 6, (200,200,200),(255,10,10))
sbar5 = pgt.SliderBar(screen, (100,580), aki_o, 440, 5, 6, (200,200,200),(255,10,10))
sbar6 = pgt.SliderBar(screen, (100,605), akd_o, 440, 0.5, 6, (200,200,200),(255,10,10))
sbar7 = pgt.SliderBar(screen, (100,655), FW, 440, 500, 6, (200,200,200),(255,10,10))

pos_pid = pid.pid(pkp_o,pki_o,pkd_o,[-10,10],[0,20],dt)
angle_pid = pid.pid(akp_o,aki_o,akd_o,[-15,15],[-60,60],dt)
pygame.display.set_caption("Tuning")



if __name__ == '__main__':
    
    while drawplot:
        screen.fill((40,40,40))
        keys = pygame.key.get_pressed()
         
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            c1, c2, c3 =  pygame.mouse.get_pressed()

            if event.type == MOUSEMOTION and c1:
                if len(coordinate)>2:
                    if np.linalg.norm(np.array(event.pos)-np.array(coordinate[-1])) > 5:
                        coordinate.append(event.pos)
                else:
                    coordinate.append(event.pos)
                

            if c3:
                if len(coordinate)>10:
                    coordinate = coordinate[0:len(coordinate)-10]
                else:
                    coordinate  = []
            if keys[K_c]:
                coordinate  = []

            if keys[K_q]:
                pygame.display.quit()
                exit()
            if keys[K_s]:
                aa = np.array(coordinate)
                np.savetxt(filename,aa)
            if keys[K_b]:
                aa = np.array(coordinate)
                timestampedname = 'Paths/'+datetime.now().strftime('%d-%m-%y-%H%M%S')+'.dat'
                np.savetxt(timestampedname,aa)
                print('Backup created in '+timestampedname)


            screen.blit(canvas,(0,0))
         
            if len(coordinate)>1:
                pygame.draw.lines(screen, (0,255,0), False, coordinate, 3)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.display.quit()
                exit()
            textPrint.abspos(screen, "Press R to run with current path",(10,420))
            textPrint.tprint(screen, " ")
            textPrint.tprint(screen, "Press S to save the current path (note this will overwrite the previous path)")
            pygame.display.update()
            
            if keys[K_r]:
                drawplot = 0
                # pygame.display.quit()

    
    

    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    #####################################################
    #-----------------  Track T-Bot  -------------------#
    #####################################################

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print('Problems Connecting to Camera')
            break
        
        screen.fill((40,40,40))
        #---------------------------------------------------------------
        #                 Listen for user events
        #---------------------------------------------------------------
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        c1, c2, c3 =  pygame.mouse.get_pressed()
        mx,my = pygame.mouse.get_pos()
        #---------------------------------------------------------------
        #                     Draw Slide Bars
        #---------------------------------------------------------------
        pkp = sbar.get_mouse_and_set()
        pki = sbar2.get_mouse_and_set()
        pkd = sbar3.get_mouse_and_set()
        
        akp = sbar4.get_mouse_and_set()
        aki = sbar5.get_mouse_and_set()
        akd = sbar6.get_mouse_and_set()
        
        FW = sbar7.get_mouse_and_set()

        #---------------------------------------------------------------
        #                      Update Tuning
        #---------------------------------------------------------------
        if pkp != pkp_old:
            pos_pid.set_PID(pkp,pki,pkd)
            pkp_old = pkp
            
        if pki != pki_old:
            pos_pid.set_PID(pkp,pki,pkd)
            pki_old = pki

        if pkd != pkd_old:
            pos_pid.set_PID(pkp,pki,pkd)
            pkd_old = pkd
            
        if akp != akp_old:
            angle_pid.set_PID(akp,aki,akd)
            akp_old = akp

        if aki != aki_old:
            angle_pid.set_PID(akp,aki,akd)
            aki_old = aki

        if akd != akd_old:
            angle_pid.set_PID(akp,aki,akd)
            akd_old = akd

        if FW_old != feedforward:
            angle_pid.set_PID(akp,aki,akd)

            feedforward = FW
        #---------------------------------------------------------------
        #            Check Status of Bluetooth Connection
        #---------------------------------------------------------------
        if ~btcom.connected():
            tries = 0
            while btcom.connected() < 1 and tries < 10:
                print('Connecting ...')
                try:
                    print('Try '+str(tries+1)+' of 10')
                    btcom.connect(0)
                    btcom.connect(1)
                    tries+=1
                except:
                    print('Something went wrong')
                    
            if btcom.connected() < 1:
                print('Exiting Program')
                sys.exit()
            else:
                tries = 0
                data = btcom.get_data(data)
                
        #---------------------------------------------------------------
        #          Track pink and green discs
        #---------------------------------------------------------------

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # do this outside function so it is not done twice
        try:         
            x, y, center, radius, M, cents = geom.tracker(hsv, greenLower, greenUpper)
            if radius > 1:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), -1)
                pts.appendleft(center)
        except:
            pass
        try:
            x2, y2, center2, radius2, M2, cents2 = geom.tracker(hsv, pinkLower, pinkUpper)

            if radius2 > 1:
                cv2.circle(frame, (int(x2), int(y2)), int(radius2),(113,212,198), 2)
                cv2.circle(frame, center2, 2, (113,212,198), -1)
                pts2.appendleft(center2)
        except:
            pass
        #---------------------------------------------------------------
        #                  Plot trail overlay
        #---------------------------------------------------------------
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            if pts[i - 1] is None or pts[i] is None:
                continue
     
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), 1)

        for ii in range(1, len(pts2)):
            # if either of the tracked points are None, ignore
            if pts2[ii - 1] is None or pts2[ii] is None:
                continue
     
            cv2.line(frame, pts2[ii - 1], pts2[ii], (113,212,198), 1)
        #---------------------------------------------------------------
        #                    Plot Path Overlay
        #---------------------------------------------------------------
        if showline:
            cv2.polylines(frame, np.int32([aa]),True, (255,0,255),2)
        cv2.circle(frame, tuple(aa[pathindex,:].astype(int)), 8, (250,150,10), -1)
        #---------------------------------------------------------------
        #                   Calculate Lap Times
        #---------------------------------------------------------------
        if laptime < oldlaptime:
            if laptime < 1000:
                textstr = 'Best time is: '+"{:6.4f}".format(laptime)
                oldlaptime = laptime
                flag = 1
        if flag == 1:
            textstr2 = 'Last lap time: '+"{:6.4f}".format(laptime)
        
        #---------------------------------------------------------------
        #                     Control Strategy
        #---------------------------------------------------------------
        
        if x != [] and x2 !=[]:
            vto = aa[pathindex] # target coordinate
            try:
                vto_next = aa[pathindex+3] # next target coordinate
            except:
                pass
            _distance = geom.distance((x,y),(x2,y2),vto) # distance to target coordinate

            if np.abs(_distance) < tolerance:
                pathindex += 1  # if close enough to target coordinate, get next coordinate
                vto = aa[pathindex]
                
                if timeflag == 0:
                    starttime = time()
                    timeflag = 1
                    
                pos_pid.clear()  
                angle_pid.clear()
            

            if pathindex == len(aa)-1:
                sendcount = btcom.send_data('200200Z',sendcount)
                print('Done, reached end of path...')
                laptime = time()-starttime
                pathindex = 0
                timeflag = 0
                
            #-----------------------------------------------------------
            #      Calculate angle and distance to way point
            #-----------------------------------------------------------
            angle = geom.angle((x,y),(x2,y2),vto)
            rotspeed = 200+angle_pid.output(0,-angle)
            oldtime = time()
            straightspeedfactor = 1
            forwardspeed = 200+straightspeedfactor*(pos_pid.output(0,-_distance)+feedforward)

            #-----------------------------------------------------------
            #          build data string to sent to T-Bot
            #-----------------------------------------------------------
            rotspeed = '%03d' % rotspeed
            forwardspeed = '%03d' % forwardspeed

            #-----------------------------------------------------------
            #                  Send Data To T-Bot
            #-----------------------------------------------------------
            sendstr = str(rotspeed)+str(forwardspeed)+'Z'
            sendcount = btcom.send_data(sendstr,sendcount)

        #---------------------------------------------------------------
        #          Basic Trim Controls for The T-Bot
        #---------------------------------------------------------------
        if keys[pygame.K_t]:
            buttonstring = '200200F' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
        if keys[pygame.K_a]:
            buttonstring = '200200E' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
        if keys[pygame.K_y]:
            buttonstring = '200200T' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
            showline
        #---------------------------------------------------------------
        #                    Show Or Hide Overlay
        #---------------------------------------------------------------
        if keys[pygame.K_h]: # hide line
            showline = 0
        if keys[pygame.K_s]: # show line
            showline = 1
        if keys[pygame.K_t]: # show line
            sendcount = btcom.send_data('200200T',sendcount)
        if keys[pygame.K_e]: # show line
            sendcount = btcom.send_data('200200E',sendcount)
        if keys[pygame.K_f]: # show line
            sendcount = btcom.send_data('200200F',sendcount)
        if keys[pygame.K_r]:        
            pos_pid.set_PID(pkp_o,pki_o,pkd_o)
            angle_pid.set_PID(akp_o,aki_o,akd_o)
            sbar.set_pos2(pkp_o)
            sbar2.set_pos2(pki_o)
            sbar3.set_pos2(pkd_o)
            sbar4.set_pos2(akp_o)
            sbar5.set_pos2(aki_o)
            sbar6.set_pos2(akd_o)
            sbar7.set_pos2(FW_o)
            pos_pid.clear()
            angle_pid.clear()

        if keys[pygame.K_q]:
            cap.release()
            sendcount = btcom.send_data('200200Z',sendcount)
            btcom.connect(0)
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')
        screen.blit(frame,(0,0))
        textPrint.abspos(screen, "Tuning Parameters",(10,400))
        textPrint.tprint(screen, " ")
        textPrint.tprint(screen, "pkp: {:.3f}".format(pkp))
        textPrint.tprint(screen, "pki: {:.3f}".format(pki))
        textPrint.tprint(screen, "pkd: {:.3f}".format(pkd))
        textPrint.tprint(screen, " ")
        textPrint.tprint(screen, "akp: {:.3f}".format(akp))
        textPrint.tprint(screen, "aki: {:.3f}".format(aki))
        textPrint.tprint(screen, "akd: {:.3f}".format(akd))
        textPrint.tprint(screen, " ")
        textPrint.tprint(screen, "FW: {:.3f}".format(FW))
        textPrint.abspos(screen, textstr,(480,380))
        textPrint.tprint(screen,textstr2)
        pygame.display.flip()

cv2.destroyAllWindows()
pygame.display.quit()


