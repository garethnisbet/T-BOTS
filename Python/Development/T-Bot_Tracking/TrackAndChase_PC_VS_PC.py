import sys
import cv2
import os
import imutils
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))
dirpath = path_above+'/Joystick/Images/HUD'
sys.path.append(path_above)
from collections import deque
import numpy as np
from TBotTools import tbt, pid, geometry, pgt
from time import time
import bluetooth as bt
import pygame
from sys import exit
import pygame
import pygame.gfxdraw
pygame.init()
textPrint = pgt.TextPrint((255,255,255))
textPrint.setlineheight(25)

background = pygame.image.load(dirpath+'/BGTracker.png')
connecting = pygame.image.load(dirpath+'/offline.png')
scalefactor = 1
origin =  [130,20] # Cam image origin

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
camorigin = origin
exclusion_zone = [200,100]

cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cam.set(28, 0)
cam.set(cv2.CAP_PROP_GAIN,0)
cam.set(cv2.CAP_PROP_BRIGHTNESS,0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, camwidth)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camheight)
cam.set(cv2.CAP_PROP_BRIGHTNESS, 100)
sidebarwidth = 1
maskgridL = np.meshgrid(np.r_[0:camheight],np.r_[0:sidebarwidth])
maskgridR = np.meshgrid(np.r_[0:camheight],np.r_[camwidth-sidebarwidth:camwidth])

success, frame = cam.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#cam.release()
pygame.init()
screen0 = pygame.display.set_mode((1000, 359), 0, 0)
canvas = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')

# empty lists for disk positions
x = []
y = []
x2 = []
y2 = []
x3 = []
y3 = []
x4 = []
y4 = []

tolerance = 20
angle1 = 0 # inital target angle
angle2 = 0 # inital target angle
distance1 = 0 # initial target distance
distance2 = 0 # initial target distance

# setup plotting
xdatarange = [618,834]
iii = xdatarange[1]-xdatarange[0]
y_origin = 438
yscale = 100
plot_pts = deque(maxlen=xdatarange[1]-xdatarange[0])
plot_pts2 = deque(maxlen=xdatarange[1]-xdatarange[0])
plot_pts3 = deque(maxlen=xdatarange[1]-xdatarange[0])
plot_pts4 = deque(maxlen=xdatarange[1]-xdatarange[0])

for ii in range(xdatarange[0],xdatarange[1]):
    plot_pts.appendleft((ii,0))
    plot_pts2.appendleft((ii,0))
    plot_pts3.appendleft((ii,0))
    plot_pts4.appendleft((ii,0))

plot_aa = np.zeros((len(plot_pts),2))
plot_aa[:,1]=np.array(plot_pts)[:,1]
plot_aa[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
plot_cc = np.zeros((len(plot_pts),2))
plot_cc[:,1]=np.array(plot_pts2)[:,1]
plot_cc[:,0]=np.array(range(xdatarange[0],xdatarange[1]))

plot_ee = np.zeros((len(plot_pts),2))
plot_ee[:,1]=np.array(plot_pts)[:,1]
plot_ee[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
plot_gg = np.zeros((len(plot_pts),2))
plot_gg[:,1]=np.array(plot_pts2)[:,1]
plot_gg[:,0]=np.array(range(xdatarange[0],xdatarange[1]))


plot_bb=np.copy(plot_aa)
plot_dd=np.copy(plot_cc)
plot_ff=np.copy(plot_ee)
plot_hh=np.copy(plot_gg)

#----------------------------------------------------------------------#
#                        Set HSV Thresholds
#            Use getHSVThresh.py to find the correct values
#----------------------------------------------------------------------#

greenLower = (53,15,135)  # place green disc on the left.
greenUpper = (82,255,255) 
 
redLower = (0,83,198)       
redUpper = (11,255,255) # place red disc on the right

blueLower = (79,51,161)       
blueUpper = (135,255,255) # place blue disc on the left.

purpleLower = (141,59,43)       
purpleUpper = (169,255,255) # place purple disc on the right


#------------- Initialise Bluetooth data variables --------------------#
data1 = [0,0,0,0]
data2 = [0,0,0,0]
sendcount1 = 0
sendcount2 = 0
#----------------------------------------------------------------------#
#               For Linux / Raspberry Pi
#    use: 'hcitool scan' to scan for your T-Bot address
#    Note: you will have to connect to the T-Bot using your 
#    system's bluetooth application using the 1234 as the password
#----------------------------------------------------------------------#


bd_addr2 = '98:D3:71:FD:46:9C' # Trailblazer
bd_addr = '98:D3:51:FD:82:95' # George

port = 1
btcom1 = tbt.bt_connect(bd_addr,port,'PyBluez') # PyBluez works well for the Raspberry Pi
btcom2 = tbt.bt_connect(bd_addr2,port,'Socket') # PyBluez works well for the Raspberry Pi
#btcom = tbt.bt_connect(bd_addr,port,'Socket')

#----------------------------------------------------------------------#
#               For Windows and Mac
#----------------------------------------------------------------------#
#port = 'COM5'
#port = '/dev/tty.George-DevB'
#baudrate = 38400
#bd_addr = 'Empty'
#btcom = tbt.bt_connect(bd_addr,port,'PySerial',baudrate)

########################################################################
#-----------------------   Start main loop ----------------------------#
########################################################################

done = 0

screen = pygame.display.set_mode((900, 590))

rotspeed = 200 # range is 100 to 300 with 200 being zero

#-----------------------------------------------------------------------
#                         Tracking PID setup
#-----------------------------------------------------------------------
dt = 0.005
pkp1_o = 2.02
pki1_o = 0.4
pkd1_o = 0
akp1_o = 0.68
aki1_o = 0.4
akd1_o = 0.01
FW1_o = 2
FW1 = FW1_o
FW1_old = 2
pkp1_old = pkp1_o
pki1_old = pki1_o
pkd1_old = pkd1_o
akp1_old = akp1_o
aki1_old = aki1_o
akd1_old = akd1_o
pos1_pid = pid.pid(pkp1_o,pki1_o,pkd1_o,[-10,10],[0,20],dt)
angle1_pid = pid.pid(akp1_o,aki1_o,akd1_o,[-15,15],[-60,60],dt)

pkp2_o = 2.02
pki2_o = 0.4
pkd2_o = 0
akp2_o = 0.68
aki2_o = 0.4
akd2_o = 0.01
FW2_o = 2
FW2 = FW1_o
FW2_old = 2
pkp2_old = pkp2_o
pki2_old = pki2_o
pkd2_old = pkd2_o
akp2_old = akp2_o
aki2_old = aki2_o
akd2_old = akd2_o
pos2_pid = pid.pid(pkp2_o,pki2_o,pkd2_o,[-10,10],[0,20],dt)
angle2_pid = pid.pid(akp2_o,aki2_o,akd2_o,[-15,15],[-60,60],dt)


#-----------------------------------------------------------------------
#                         Create slider bars
#-----------------------------------------------------------------------
barcolour = (150,150,150)
spotcolour = (255,10,0)
sbar = pgt.SliderBar(screen, (90,450-30), pkp1_o, 180, 5, 4, barcolour,spotcolour)
sbar2 = pgt.SliderBar(screen, (90,475-30), pki1_o, 180, 5, 4, barcolour,spotcolour)
sbar3 = pgt.SliderBar(screen, (90,500-30), pkd1_o, 180, 0.5, 4, barcolour,spotcolour)
sbar4 = pgt.SliderBar(screen, (90,525-30), akp1_o, 180, 5, 4, barcolour,spotcolour)
sbar5 = pgt.SliderBar(screen, (90,550-30), aki1_o, 180, 5, 4, barcolour,spotcolour)
sbar6 = pgt.SliderBar(screen, (90,575-30), akd1_o, 180, 0.5, 4, barcolour,spotcolour)
sbar7 = pgt.SliderBar(screen, (90,600-30), FW1, 180, 100, 4, barcolour,spotcolour)


sbar8 = pgt.SliderBar(screen, (400,450-30), pkp2_o, 180, 5, 4, barcolour,spotcolour)
sbar9 = pgt.SliderBar(screen, (400,475-30), pki2_o, 180, 5, 4, barcolour,spotcolour)
sbar10 = pgt.SliderBar(screen, (400,500-30), pkd2_o, 180, 0.5, 4, barcolour,spotcolour)
sbar11 = pgt.SliderBar(screen, (400,525-30), akp2_o, 180, 5, 4, barcolour,spotcolour)
sbar12 = pgt.SliderBar(screen, (400,550-30), aki2_o, 180, 5, 4, barcolour,spotcolour)
sbar13 = pgt.SliderBar(screen, (400,575-30), akd2_o, 180, 0.5, 4, barcolour,spotcolour)
sbar14 = pgt.SliderBar(screen, (400,600-30), FW2, 180, 100, 4, barcolour,spotcolour)



pygame.display.set_caption("Track and Chase")

if __name__ == '__main__':

    #-------------------------------------------------------------------
    #                   Track T-Bot  
    #-------------------------------------------------------------------
    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            print('Problems Connecting to Camera')
            break
        frame[maskgridL] = 0
        frame[maskgridR] = 0       
        screen.blit(background,(0,0))
        
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
        pkp1 = sbar.get_mouse_and_set()
        pki1 = sbar2.get_mouse_and_set()
        pkd1 = sbar3.get_mouse_and_set()
        akp1 = sbar4.get_mouse_and_set()
        aki1 = sbar5.get_mouse_and_set()
        akd1 = sbar6.get_mouse_and_set()
        FW1 = sbar7.get_mouse_and_set()
        
        pkp2 = sbar8.get_mouse_and_set()
        pki2 = sbar9.get_mouse_and_set()
        pkd2 = sbar10.get_mouse_and_set()
        akp2 = sbar11.get_mouse_and_set()
        aki2 = sbar12.get_mouse_and_set()
        akd2 = sbar13.get_mouse_and_set()
        FW2  = sbar14.get_mouse_and_set()
        #---------------------------------------------------------------
        #               Update tuning from slider bars
        #---------------------------------------------------------------
        if pkp1 != pkp1_old:
            pos1_pid.set_PID(pkp1,pki1,pkd1)
            pkp1_old = pkp1
            
        if pki1 != pki1_old:
            pos1_pid.set_PID(pkp1,pki1,pkd1)
            pki1_old = pki1

        if pkd1 != pkd1_old:
            pos1_pid.set_PID(pkp1,pki1,pkd1)
            pkd1_old = pkd1
            
        if akp1 != akp1_old:
            angle1_pid.set_PID(akp1,aki1,akd1)
            akp1_old = akp1

        if aki1 != aki1_old:
            angle1_pid.set_PID(akp1,aki1,akd1)
            aki1_old = aki1

        if akd1 != akd1_old:
            angle1_pid.set_PID(akp1,aki1,akd1)
            akd1_old = akd1

        if FW1 != FW1_old:
            FW1_old = FW1
            
        #---------------------- Slider bars for T-Bot 2 ----------------
        if pkp2 != pkp2_old:
            pos2_pid.set_PID(pkp2,pki2,pkd2)
            pkp2_old = pkp2
            
        if pki2 != pki2_old:
            pos2_pid.set_PID(pkp2,pki2,pkd2)
            pki2_old = pki2

        if pkd2 != pkd2_old:
            pos2_pid.set_PID(pkp2,pki2,pkd2)
            pkd2_old = pkd2
            
        if akp2 != akp2_old:
            angle2_pid.set_PID(akp2,aki2,akd2)
            akp2_old = akp2

        if aki2 != aki2_old:
            angle2_pid.set_PID(akp2,aki2,akd2)
            aki2_old = aki2

        if akd2 != akd1_old:
            angle2_pid.set_PID(akp2,aki2,akd2)
            akd2_old = akd2

        if FW2 != FW2_old:
            FW2_old = FW2

        #---------------------------------------------------------------
        #            Check Status of Bluetooth Connection
        #---------------------------------------------------------------
        if ~btcom1.connected():
            tries = 0
            while btcom1.connected() < 1 and tries < 10:
                screen.blit(connecting,(0,0))
                pygame.display.flip()
                print('Connecting ...')              
                try:
                    print('Try '+str(tries+1)+' of 10')
                    btcom1.connect(0)
                    btcom1.connect(1)
                    tries+=1
                except:
                    print('Something went wrong')                  
            if btcom1.connected() < 1:
                print('Exiting Program')
                sys.exit()
            else:
                tries = 0
                data1 = btcom1.get_data(data1)

        if ~btcom2.connected():
            tries = 0
            while btcom2.connected() < 1 and tries < 10:
                screen.blit(connecting,(0,0))
                pygame.display.flip()
                print('Connecting ...')              
                try:
                    print('Try '+str(tries+1)+' of 10')
                    btcom2.connect(0)
                    btcom2.connect(1)
                    tries+=1
                except:
                    print('Something went wrong')                  
            if btcom2.connected() < 1:
                print('Exiting Program')
                sys.exit()
            else:
                tries = 0
                data2 = btcom2.get_data(data2)
                
        #---------------------------------------------------------------
        #        Track red and green discs and oponents blue fin 
        #---------------------------------------------------------------

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # do this outside function so it is not done twice
        try:         
            x, y, center, radius, M, cents = geom.tracker(hsv, greenLower, greenUpper)
            if radius > 1:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), -1)
        except:
            pass
        try:
            x2, y2, center2, radius2, M2, cents2 = geom.tracker(hsv, redLower, redUpper)
            if radius2 > 1:
                cv2.circle(frame, (int(x2), int(y2)), int(radius2),(113,212,198), 2)
                cv2.circle(frame, center2, 2, (113,212,198), -1)
        except:
            pass
        try:
            x3, y3, center3, radius3, M3, cents3 = geom.tracker(hsv, blueLower, blueUpper)
            if radius3 > 1:
                cv2.circle(frame, (int(x3), int(y3)), int(radius3),(113,212,198), 2)
                cv2.circle(frame, center3, 2, (113,212,198), -1)
        except:
            pass
        
        try:
            x4, y4, center4, radius4, M4, cents4 = geom.tracker(hsv, purpleLower, purpleUpper)
            if radius3 > 1:
                cv2.circle(frame, (int(x4), int(y4)), int(radius4),(113,212,198), 2)
                cv2.circle(frame, center4, 2, (113,212,198), -1)
                
        except:
            pass
        

        #---------------------------------------------------------------
        #                     Control Strategy
        #---------------------------------------------------------------
        
        if x != [] and x2 !=[] and x3!=[] and x4!=[]:
            if x < exclusion_zone[0] or x > camwidth-exclusion_zone[0] or y < exclusion_zone[1] or y > camheight-exclusion_zone[1]:
                distance1 = geom.distance((x,y),(x2,y2),(int(camwidth/2.),int(camheight/2.))) # distance to target coordinate
                angle1 = geom.angle((x,y),(x2,y2),(int(camwidth/2.),int(camheight/2.)))
            else:
                distance1 = geom.distance((x,y),(x2,y2),(int((x3+x4)/2.0) ,int((y3+y4)/2.))) # distance to target coordinate
                angle1 = geom.angle((x,y),(x2,y2),(int((x3+x4)/2.0) ,int((y3+y4)/2.)))
                
            if x3 < exclusion_zone[0] or x3 > camwidth-exclusion_zone[0] or y3 < exclusion_zone[1] or y3 > camheight-exclusion_zone[1]:
                distance2 = geom.distance((x3,y3),(x4,y4),(int(camwidth/2.),int(camheight/2.))) # distance to target coordinate
                angle2 = geom.angle((x3,y3),(x4,y4),(int(camwidth/2.),int(camheight/2.)))
            else:
                distance2 = geom.distance((x3,y3),(x4,y4),(int((x+x2)/2.),int((y+y2)/2.))) # distance to target coordinate
                angle2 = geom.angle((x3,y3),(x4,y4),(int((x+x2)/2.),int((y+y2)/2.)))
            if np.abs(distance1) < tolerance:
                abc = 'You could add some extra logic here for battle AI'
                # angle1 = angle1+90 
            else:
                pass

            rotspeed1 = 200+angle1_pid.output(0,-angle1)
            forwardspeed1 = 200+(pos1_pid.output(0,-distance1)+FW1)
            rotspeed2 = 200+angle2_pid.output(0,-angle2)
            forwardspeed2 = 200+(pos2_pid.output(0,-distance2)+FW2)
            
            #-----------------------------------------------------------
            #          build data string to send to T-Bot
            #-----------------------------------------------------------
            rotspeed1 = '%03d' % rotspeed1
            forwardspeed1 = '%03d' % forwardspeed1
            rotspeed2 = '%03d' % rotspeed2
            forwardspeed2 = '%03d' % forwardspeed2
            #-----------------------------------------------------------
            #                  Send Data To T-Bot
            #-----------------------------------------------------------
            sendstr1 = str(rotspeed1)+str(forwardspeed1)+'Z'
            sendcount1 = btcom1.send_data(sendstr1,sendcount1)
            sendstr2 = str(rotspeed2)+str(forwardspeed2)+'Z'
            sendcount2 = btcom2.send_data(sendstr2,sendcount2)
            
        #---------------------------------------------------------------
        #          Basic Trim Controls for The T-Bot
        #---------------------------------------------------------------
        if keys[pygame.K_t]:
            buttonstring = '200200T' # Auto trim
            sendcount1 = btcom1.send_data(buttonstring,sendcount1)
        if keys[pygame.K_a]:
            buttonstring = '200200E' # -ve trim
            sendcount1 = btcom1.send_data(buttonstring,sendcount1)
        if keys[pygame.K_f]:
            buttonstring = '200200F' # +ve trim
            sendcount1 = btcom1.send_data(buttonstring,sendcount1)

        #---------------------------------------------------------------
        #            Reset tuning to default settings 
        #---------------------------------------------------------------

        if keys[pygame.K_r]:       
            pos1_pid.set_PID(pkp1_o,pki1_o,pkd1_o)
            angle1_pid.set_PID(akp1_o,aki1_o,akd1_o)
            sbar.set_pos2(pkp1_o)
            sbar2.set_pos2(pki1_o)
            sbar3.set_pos2(pkd1_o)
            sbar4.set_pos2(akp1_o)
            sbar5.set_pos2(aki1_o)
            sbar6.set_pos2(akd1_o)
            sbar7.set_pos2(FW1_o)
            pos1_pid.clear()
            angle1_pid.clear()

            pos2_pid.set_PID(pkp2_o,pki2_o,pkd2_o)
            angle2_pid.set_PID(akp2_o,aki2_o,akd2_o)
            sbar8.set_pos2(pkp2_o)
            sbar9.set_pos2(pki2_o)
            sbar10.set_pos2(pkd2_o)
            sbar11.set_pos2(akp2_o)
            sbar12.set_pos2(aki2_o)
            sbar13.set_pos2(akd2_o)
            sbar14.set_pos2(FW2_o)
            pos2_pid.clear()
            angle2_pid.clear()

        if keys[pygame.K_q]: # Quit and exit
            cam.release()
            sendcount1 = btcom1.send_data('200200Z',sendcount1)
            sendcount2 = btcom2.send_data('200200Z',sendcount2)
            btcom1.connect(0)
            btcom2.connect(0)
            break
            
        #---------------------------------------------------------------
        #            Add data points for plotting 
        #---------------------------------------------------------------          
        plot_pts.appendleft((iii,angle1))
        plot_pts2.appendleft((iii,distance1))
        plot_pts3.appendleft((iii,angle2))
        plot_pts4.appendleft((iii,distance2))
        iii+=1
        if iii > xdatarange[1]:
            iii = xdatarange[0]
        plot_aa[:,1]=np.array(plot_pts)[:,1]
        plot_cc[:,1]=np.array(plot_pts2)[:,1]
        plot_ee[:,1]=np.array(plot_pts)[:,1]
        plot_gg[:,1]=np.array(plot_pts2)[:,1]
        pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin+0.5*yscale),(xdatarange[1],y_origin+0.5*yscale)),1)
        try:  
            plot_bb[:,1] = (yscale/((plot_aa[:,1]-plot_aa[:,1].max()).min())*(plot_aa[:,1]-plot_aa[:,1].max()))+y_origin
            plot_dd[:,1] = (yscale/((plot_cc[:,1]-plot_cc[:,1].max()).min())*(plot_cc[:,1]-plot_cc[:,1].max()))+y_origin
            plot_ff[:,1] = (yscale/((plot_ee[:,1]-plot_ee[:,1].max()).min())*(plot_ee[:,1]-plot_ee[:,1].max()))+y_origin
            plot_hh[:,1] = (yscale/((plot_gg[:,1]-plot_gg[:,1].max()).min())*(plot_gg[:,1]-plot_gg[:,1].max()))+y_origin
            gdata1 = tuple(map(tuple, tuple(plot_bb)))
            vdata1 = tuple(map(tuple, tuple(plot_dd)))
            gdata2 = tuple(map(tuple, tuple(plot_ff)))
            vdata2 = tuple(map(tuple, tuple(plot_hh)))
            pygame.draw.lines(screen, (255,255,255,255), False, (gdata1),1)
            pygame.draw.lines(screen, (255,0,0,255), False, (vdata1),1)

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
        textPrint.abspos(screen, "pkp: {:.3f}".format(pkp1),(10,416))
        textPrint.tprint(screen, "pki: {:.3f}".format(pki1))
        textPrint.tprint(screen, "pkd: {:.3f}".format(pkd1))
        textPrint.tprint(screen, "akp: {:.3f}".format(akp1))
        textPrint.tprint(screen, "aki: {:.3f}".format(aki1))
        textPrint.tprint(screen, "akd: {:.3f}".format(akd1))
        textPrint.tprint(screen, "FW: {:.3f}".format(FW1))

        textPrint.abspos(screen, "pkp: {:.3f}".format(pkp2),(320,416))
        textPrint.tprint(screen, "pki: {:.3f}".format(pki2))
        textPrint.tprint(screen, "pkd: {:.3f}".format(pkd2))
        textPrint.tprint(screen, "akp: {:.3f}".format(akp2))
        textPrint.tprint(screen, "aki: {:.3f}".format(aki2))
        textPrint.tprint(screen, "akd: {:.3f}".format(akd2))
        textPrint.tprint(screen, "FW: {:.3f}".format(FW2))

        try:
            orient = geom.orientation(center2,center)
        except:
            orient = geom.orientation([0,0],[1,1])
        arrow_rot1 = np.array(geom.rotxy(orient[1]*np.pi/180,arrow))
        arrow1_tup = tuple(map(tuple, tuple((arrow_rot1+orient[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow1_tup), (0,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow1_tup), (0,255,255,200))
        arrow_rot2 = np.array(geom.rotxy((angle1+orient[1])*np.pi/180,arrow))
        arrow2_tup = tuple(map(tuple, tuple((arrow_rot2+orient[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow2_tup), (255,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow2_tup), (0,255,255,200))

        try:
            orient2 = geom.orientation(center4,center3)
        except:
            orient2 = geom.orientation([0,0],[1,1])
        arrow_rot1 = np.array(geom.rotxy(orient2[1]*np.pi/180,arrow))
        arrow1_tup = tuple(map(tuple, tuple((arrow_rot1+orient2[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow1_tup), (0,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow1_tup), (0,255,255,200))
        arrow_rot2 = np.array(geom.rotxy((angle2+orient2[1])*np.pi/180,arrow))
        arrow2_tup = tuple(map(tuple, tuple((arrow_rot2+orient2[0]+origin).astype(int))))
        pygame.gfxdraw.filled_polygon(screen, (arrow2_tup), (255,255,255,155))
        pygame.gfxdraw.aapolygon(screen, (arrow2_tup), (0,255,255,200))
        pygame.draw.rect(screen, (255, 0,0,0), (camorigin[0]+exclusion_zone[0], camorigin[1]+exclusion_zone[1], camwidth-exclusion_zone[0]*2, camheight-exclusion_zone[1]*2), 3)
        pygame.display.flip()
        framearray = np.array(frame)
cv2.destroyAllWindows()
pygame.display.quit()


