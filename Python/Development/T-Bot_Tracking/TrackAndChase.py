import sys
import cv2
import os
import imutils
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))
dirpath = path_above+'/Joystick/Images/HUD'
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

background = pygame.image.load(dirpath+'/BGTracker.png')
scalefactor = 1
#origin =  [636/2,357/2]
origin =  [130,20]
showline = 0
drawplot = 1
interpfactor = 5
flag = 0
geom = geometry.geometry(1) # scale factor to convert pixels to mm
arrow = np.array([[2,0],[2,50],[7,50],[0,65],[-7,50],[-2,50],[-2,0],[2,0]])
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


camwidth = 640
camheight = 360
vto = np.array([320,180])
camorigin = origin

cam = cv2.VideoCapture(2,cv2.CAP_V4L2)
cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cam.set(28, 0)
cam.set(cv2.CAP_PROP_GAIN,0)
cam.set(cv2.CAP_PROP_BRIGHTNESS,0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cam.set(cv2.CAP_PROP_BRIGHTNESS, 100)

maskgridL = np.meshgrid(np.r_[0:360],np.r_[0:20])
maskgridR = np.meshgrid(np.r_[0:360],np.r_[640-20:640])

success, frame = cam.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#cam.release()
pygame.init()
screen0 = pygame.display.set_mode((1000, 359), 0, 0)
canvas = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')

x = []
y = []
x2 = []
y2 = []
x3 = []
y3 = []
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
tolerance = 10
angle = 0


# sets the length of the trail
angle = 0
_distance = 0
xdatarange = [618,834]
y_origin = 438
yscale = 100
plot_pts = deque(maxlen=xdatarange[1]-xdatarange[0])
plot_pts2 = deque(maxlen=xdatarange[1]-xdatarange[0])
plot_pts3 = deque(maxlen=xdatarange[1]-xdatarange[0])

for ii in range(xdatarange[0],xdatarange[1]):
    plot_pts.appendleft((ii,0))
    plot_pts2.appendleft((ii,0))
    plot_pts3.appendleft((ii,0))
iii = 200
plot_aa = np.zeros((len(plot_pts),2))
plot_aa[:,1]=np.array(plot_pts)[:,1]
plot_aa[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
plot_cc = np.zeros((len(plot_pts),2))
plot_cc[:,1]=np.array(plot_pts2)[:,1]
plot_cc[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
plot_bb=np.copy(plot_aa)
plot_dd=np.copy(plot_cc)


pts = deque(maxlen=10)
pts2 = deque(maxlen=10)


#----------------------------------------------------------------------#
#                        Set HSV Thresholds
#            Use getHSVThresh.py to find the correct values
#
#                        Artificial Lighting
#----------------------------------------------------------------------#

greenLower = (27,94,49)  # place green disc on the left.
greenUpper = (109,255,255) 

 
pinkLower = (0,138,45)       
pinkUpper = (2,255,255) # place pink disc on the right


blueLower = (53,150,23)       
blueUpper = (255,255,255) # Blue fin on helmet

# blueLower = (0,39,106)       
# blueUpper = (18,255,255) # For gold helmet

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
# bd_addr = '98:D3:71:FD:44:F7'
bd_addr = '98:D3:71:FD:46:9C' # Trailblazer

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




########################################################################
#-----------------------   Start main loop ----------------------------#
########################################################################

oldtime = time()
done = 0

screen = pygame.display.set_mode((900, 590))

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

barcolour = (150,150,150)
spotcolour = (255,10,0)
sbar = pgt.SliderBar(screen, (100,450-30), pkp_o, 460, 5, 4, barcolour,spotcolour)
sbar2 = pgt.SliderBar(screen, (100,475-30), pki_o, 460, 5, 4, barcolour,spotcolour)
sbar3 = pgt.SliderBar(screen, (100,500-30), pkd_o, 460, 0.5, 4, barcolour,spotcolour)

sbar4 = pgt.SliderBar(screen, (100,525-30), akp_o, 460, 5, 4, barcolour,spotcolour)
sbar5 = pgt.SliderBar(screen, (100,550-30), aki_o, 460, 5, 4, barcolour,spotcolour)
sbar6 = pgt.SliderBar(screen, (100,575-30), akd_o, 460, 0.5, 4, barcolour,spotcolour)
sbar7 = pgt.SliderBar(screen, (100,600-30), FW, 460, 100, 4, barcolour,spotcolour)

pos_pid = pid.pid(pkp_o,pki_o,pkd_o,[-10,10],[0,20],dt)
angle_pid = pid.pid(akp_o,aki_o,akd_o,[-15,15],[-60,60],dt)
pygame.display.set_caption("Track and Chase")

if __name__ == '__main__':


    success, frame = cam.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    #####################################################
    #-----------------  Track T-Bot  -------------------#
    #####################################################

    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            print('Problems Connecting to Camera')
            break
        frame[maskgridL] = 0
        frame[maskgridR] = 0
        
        # screen.fill((40,40,40))
        screen.blit(background,(0,0))
        #screen.blit(tbot_ortho,(600,500))
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

        try:
            x3, y3, center3, radius3, M3, cents3 = geom.tracker(hsv, blueLower, blueUpper)

            if radius3 > 1:
                cv2.circle(frame, (int(x3), int(y3)), int(radius3),(113,212,198), 2)
                cv2.circle(frame, center3, 2, (113,212,198), -1)
                pts2.appendleft(center3)
        except:
            pass

        
        #---------------------------------------------------------------
        #                     Control Strategy
        #---------------------------------------------------------------
        
        if x != [] and x2 !=[] and x3!=[]:
            vto = center3 # target coordinate
            _distance = geom.distance((x,y),(x2,y2),(x3,y3)) # distance to target coordinate
            if np.abs(_distance) < tolerance:
                pos_pid.clear()  
                angle_pid.clear()
                sendcount = btcom.send_data('200200Z',sendcount)
            else:
                #-----------------------------------------------------------
                #      Calculate angle and distance to way point
                #-----------------------------------------------------------
                angle = geom.angle((x,y),(x2,y2),(x3,y3))
                rotspeed = 200+angle_pid.output(0,-angle)
                oldtime = time()
                straightspeedfactor = 1
                forwardspeed = 200+(pos_pid.output(0,-_distance)+FW)

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
            cam.release()
            sendcount = btcom.send_data('200200Z',sendcount)
            btcom.connect(0)
            break
        plot_pts.appendleft((iii,angle))
        plot_pts2.appendleft((iii,_distance))
        iii+=1
        if iii > xdatarange[1]:
            iii = xdatarange[0]
        plot_aa[:,1]=np.array(plot_pts)[:,1]
        plot_cc[:,1]=np.array(plot_pts2)[:,1]
        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin+0.5*yscale),(xdatarange[1],y_origin+0.5*yscale)),1)
        try:  
            plot_bb[:,1] = (yscale/((plot_aa[:,1]-plot_aa[:,1].max()).min())*(plot_aa[:,1]-plot_aa[:,1].max()))+y_origin
            plot_dd[:,1] = (yscale/((plot_cc[:,1]-plot_cc[:,1].max()).min())*(plot_cc[:,1]-plot_cc[:,1].max()))+y_origin
            gdata = tuple(map(tuple, tuple(plot_bb)))
            vdata = tuple(map(tuple, tuple(plot_dd)))
            pygame.draw.lines(screen, (255,255,255,255), False, (gdata),1)
            pygame.draw.lines(screen, (255,0,0,255), False, (vdata),1)
        except Exception:
            pass

        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin),(xdatarange[0],y_origin+yscale)),1)
        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[-1],y_origin),(xdatarange[-1],y_origin+yscale)),1)

        textPrint.abspos(screen, "{:+.2f}".format(plot_aa[:,1].max()),[xdatarange[0],y_origin-20])
        textPrint.abspos(screen, "{:+.2f}".format(plot_aa[:,1].min()),[xdatarange[0],y_origin+yscale+5])
        textPrint.tprint(screen,'Angle')
        textPrint.setColour((255,0,0,255))
        textPrint.abspos(screen, "{:+.2f}".format(plot_cc[:,1].max()),[xdatarange[-1],y_origin-20])
        textPrint.abspos(screen, "{:+.2f}".format(plot_cc[:,1].min()),[xdatarange[-1],y_origin+yscale+5])
        textPrint.tprint(screen,'Distance')
        textPrint.setColour((255,255,255,255))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')
        screen.blit(frame,camorigin)
        textPrint.abspos(screen, "pkp: {:.3f}".format(pkp),(10,416))
        textPrint.tprint(screen, "pki: {:.3f}".format(pki))
        textPrint.tprint(screen, "pkd: {:.3f}".format(pkd))
        textPrint.tprint(screen, "akp: {:.3f}".format(akp))
        textPrint.tprint(screen, "aki: {:.3f}".format(aki))
        textPrint.tprint(screen, "akd: {:.3f}".format(akd))
        textPrint.tprint(screen, "FW: {:.3f}".format(FW))
        textPrint.abspos(screen, textstr,(450,425))
        textPrint.tprint(screen,textstr2)
        try:
            orient = geom.orientation(center2,center)
        except:
            orient = geom.orientation([0,0],[1,1])
        arrow_rot1 = np.array(geom.rotxy(orient[1]*np.pi/180,arrow))
        arrow1_tup = tuple(map(tuple, tuple((arrow_rot1+orient[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow1_tup), (0,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow1_tup), (0,255,255,200))
        arrow_rot2 = np.array(geom.rotxy((angle+orient[1])*np.pi/180,arrow))
        arrow2_tup = tuple(map(tuple, tuple((arrow_rot2+orient[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow2_tup), (255,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow2_tup), (0,255,255,200))
        pygame.display.flip()

cv2.destroyAllWindows()
pygame.display.quit()


