import sys
import cv2
import os
import imutils
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..'))
sys.path.append(path_above)
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from TBotTools import tbt, pid, geometry
from scipy.interpolate import interp1d
from time import time
plt.ion()
import bluetooth as bt
from datetime import datetime
import pygame
from pygame.locals import *
from sys import exit
scalefactor = 1
#origin =  [636/2,357/2]
origin =  [0,0]
showline = 1
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

success, frame = cap.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
cap.release()
pygame.init()
screen = pygame.display.set_mode((633, 359), 0, 0)
canvas = pygame.image.frombuffer(frame.tostring(),frame.shape[1::-1],'RGB')
 

drawplot = 1


while drawplot:
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

        pygame.display.update()
        
        if keys[K_r]:
            drawplot = 0
            pygame.display.quit()


x = []
y = []
x2 = []
y2 = []
starttime = []
endtime = []
laptime = 1000
oldlaptime = 500
folder = 'RecordedImages2/'
record = 0

#folder = 'SpeedTest/'
if record:
    if os.path.isdir(folder) is not True:
        os.mkdir(folder)
template = folder + '%05d.png'
frameskip = 10


font = cv2.FONT_HERSHEY_SIMPLEX 

#---------------- Setup text writing  -----------------#
# org 
org = (60, 20)  
# fontScale 
fontScale = 0.5   
# Blue color in BGR 
color = (255, 0, 0)
color2 = (0, 255, 0)  
# Line thickness of 2 px 
thickness = 1
textstr = ''



tii = 0 # counter to prevent recording every frame and slowing the Pi
iii = 1
loopcount = 0
pathindex = 0
timeflag = 0
pathindex = 0
rotspeed = 200
speedfactor = 0.3

turnspeedfactor = 0.3
turntime = 0.005
bendscalefactor = 10
rdeadban = 2
tolerance = 30


feedforward = 2
pkp_o = 0.4
pki_o = 0.4
pkd_o = 0
akp_o = 0.4
aki_o = 0.4
akd_o = 0.01


pos_pid = pid.pid(pkp_o,pki_o,pkd_o,[-10,10],[0,20],turntime)
angle_pid = pid.pid(akp_o,aki_o,akd_o,[-15,15],[-60,60],turntime)


slider_scale = 3
cv2.namedWindow("Tuning",cv2.WINDOW_NORMAL)

cv2.resizeWindow("Tuning", 700, 700)
pkp = round(pos_pid.get_PID()[0]/(slider_scale/255.))
cv2.createTrackbar('p_KP', "Tuning", pkp, 255, (lambda a: None))
pki = round(pos_pid.get_PID()[1]/(slider_scale/255.))
cv2.createTrackbar('p_KI', "Tuning", pki, 255, (lambda a: None))
pkd = round(pos_pid.get_PID()[2]/(slider_scale/255.))
cv2.createTrackbar('p_KD', "Tuning", pkd, 255, (lambda a: None))

akp = round(angle_pid.get_PID()[0]/(slider_scale/255.))
cv2.createTrackbar('a_KP', "Tuning", akp, 255, (lambda a: None))
aki = round(angle_pid.get_PID()[1]/(slider_scale/255.))
cv2.createTrackbar('a_KI', "Tuning", aki, 255, (lambda a: None))
akd = round(angle_pid.get_PID()[2]/(slider_scale/255.))
cv2.createTrackbar('a_KD', "Tuning", akd, 255, (lambda a: None))
fw = feedforward
cv2.createTrackbar('FW', "Tuning", fw, 255, (lambda a: None))



#----------------------------------------------------------------------#
#                        Set HSV Thresholds
#
#                        Artificial Lighting
#----------------------------------------------------------------------#
greenLower = (40,38,193)   # place green disc on the left
greenUpper = (97,107,255) 
 
pinkLower = (129,45,0)     # place pink disc on the right
pinkUpper = (255,255,255) 

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




# sets the length of the trail
pts = deque(maxlen=10)
pts2 = deque(maxlen=10)

pathindex = 0
rotspeed = 200
speedfactor = 0.3
turnspeedfactor = 0.3
turntime = 0.005
bendscalefactor = 10
rdeadban = 2
tolerance = 30

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


oldtime = time()
if __name__ == '__main__':
   
    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    #####################################################
    #-----------------  Track T-Bot  -------------------#
    #####################################################

    while cap.isOpened():
        success, frame = cap.read()
        #frame = cv2.flip(frame,1)
        if not success:
            break

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
                
        pkp = round(cv2.getTrackbarPos('p_KP', "Tuning") * (slider_scale/255.),2)
        pki = round(cv2.getTrackbarPos('p_KI', "Tuning") * (slider_scale/255.),2)
        pkd = round(cv2.getTrackbarPos('p_KD', "Tuning") * (slider_scale/255.),2)
        akp = round(cv2.getTrackbarPos('a_KP', "Tuning") * (slider_scale/255.),2)
        aki = round(cv2.getTrackbarPos('a_KI', "Tuning") * (slider_scale/255.),2)
        akd = round(cv2.getTrackbarPos('a_KD', "Tuning") * (slider_scale/255.),2)
        fw = cv2.getTrackbarPos('FW', "Tuning")
        if pkp != pkp_o:
            pos_pid.set_PID(pkp,pki,pkd)
            print('set new '+str(pkp)+' '+str(pki)+' '+str(pkd)+' '+str(pkp_o))
            pkp_o = pkp
        if pki != pki_o:
            pos_pid.set_PID(pkp,pki,pkd)
            print('set new '+str(pkp)+' '+str(pki)+' '+str(pkd)+' '+str(pki_o))
            pki_o = pki
        if pkd != pkd_o:
            pos_pid.set_PID(pkp,pki,pkd)
            print('set new '+str(pkp)+' '+str(pki)+' '+str(pkd)+' '+str(pkd_o))
            pkd_o = pkd
            
        if akp != akp_o:
            angle_pid.set_PID(akp,aki,akd)
            print('set new angle PID '+str(akp)+' '+str(aki)+' '+str(akd)+' '+str(akp_o))
            akp_o = akp
        if aki != aki_o:
            angle_pid.set_PID(akp,aki,akd)
            print('set new angle PID '+str(akp)+' '+str(aki)+' '+str(akd)+' '+str(aki_o))
            aki_o = aki
        if akd != akd_o:
            angle_pid.set_PID(akp,aki,akd)
            print('set new angle PID '+str(akp)+' '+str(aki)+' '+str(akd)+' '+str(akd_o))
            akd_o = akd
        if fw != feedforward:
            angle_pid.set_PID(akp,aki,akd)
            print('set new '+str(fw))
            feedforward = fw


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

        #------------- Plot trail overlay -------------#

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

        if showline:
            cv2.polylines(frame, np.int32([aa]),True, (255,0,255),2)
        cv2.circle(frame, tuple(aa[pathindex,:].astype(int)), 8, (250,150,10), -1)
        if laptime < oldlaptime:
            if laptime < 1000:
                textstr = 'Best time is: '+"{:6.4f}".format(laptime)
                oldlaptime = laptime
                flag = 1
        if flag == 1:
            cv2.putText(frame, textstr, org, font,fontScale, color, thickness, cv2.LINE_AA)
            textstr2 = 'Last lap time: '+"{:6.4f}".format(laptime)
            cv2.putText(frame, textstr2, (org[0],org[1]+20), font,fontScale, color2, thickness, cv2.LINE_AA)

        cv2.imshow("Tuning", frame)


        ###################################################
        #---------------  Control Strategy ---------------#
        ###################################################
        
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
                #aa = np.flipud(aa)
                laptime = time()-starttime
                #feedforward += 1
                #print(feedforward)
                pathindex = 0
                timeflag = 0

            angle = geom.angle((x,y),(x2,y2),vto)
            rotspeed = 200+angle_pid.output(0,-angle)
            oldtime = time()
            straightspeedfactor = 1
            forwardspeed = 200+straightspeedfactor*(pos_pid.output(0,-_distance)+feedforward)


            #------------  build data string  ------------#

            rotspeed = '%03d' % rotspeed
        
            forwardspeed = '%03d' % forwardspeed

            #print('forward speed '+forwardspeed+' turn speed '+rotspeed)
            #--------------   Send data    ---------------#
            sendstr = str(rotspeed)+str(forwardspeed)+'Z'
            sendcount = btcom.send_data(sendstr,sendcount)

            

        key = cv2.waitKey(1) & 0xFF


        if key == ord("t"):
            buttonstring = '200200F' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
        if key == ord("r"):
            buttonstring = '200200E' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
        if key == ord("y"):
            buttonstring = '200200T' # Auto trim
            sendcount = btcom.send_data(buttonstring,sendcount)
            showline
        if key == ord("h"):
            showline = 0
        if key == ord("s"):
            showline = 1


        if key == ord("f"):
            feedforward -= 1
            print('feedforward = '+str(feedforward))
        if key == ord("g"):
            feedforward += 1
            print('feedforward = '+str(feedforward))
        if key == ord("y"):
            turnspeedfactor -= 0.01
            print('turnspeedfactor = '+str(turnspeedfactor))
            # if the 'q' key is pressed, stop the loop
        if key == ord("t"):
            sendcount = btcom.send_data('200200T',sendcount)

        if key == ord("q"):

            cap.release()
            sendcount = btcom.send_data('200200Z',sendcount)
            btcom.connect(0)
            break
        if record:
            if tii == frameskip:
                cv2.imwrite(template % iii, frame)
                iii += 1
                tii = 0
            else:
                tii += 1


cv2.destroyAllWindows()



