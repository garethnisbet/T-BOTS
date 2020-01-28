import sys
import cv2
import os
import imutils
sys.path.append('/home/pi/GitHub/T-BOTS/Joystick')
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from Classes import tbt, pid
from time import time
plt.ion()
import bluetooth as bt
x = []
y = []
x2 = []
y2 = []
starttime = []
endtime = []
laptime = 1000
oldlaptime = 500

folder = 'RecordedImages/'
record = 0

#folder = 'SpeedTest/'
if record:
    if os.path.isdir(folder) is not True:
        os.mkdir(folder)
template = folder + '%05d.png'
font = cv2.FONT_HERSHEY_SIMPLEX 

#---------------- Setup text writing  -----------------#
# org 
org = (50, 50)  
# fontScale 
fontScale = 0.5   
# Blue color in BGR 
color = (255, 0, 0) 
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
turntime = 0.01
bendscalefactor = 10
rdeadban = 2
tolerance = 30

feedforward = 7
pos_pid = pid.pid(0.05,0.6,0,[-15,15],[0,30],turntime)
angle_pid = pid.pid(0.4,2.4,0.02,[-15,15],[-60,60],turntime)
#----------------- set variables --------------------#

#blueLower = (96,205,185)
#blueUpper = (152,255,255)

blueLower = (89,214,139)
blueUpper = (255,255,255)

#pinkLower = (133,97,83)
#pinkUpper = (255,255,255)
#pinkLower = (149,147,31)
#pinkUpper = (255,255,255)

pinkLower = (0,74,53)
pinkUpper = (11,255,255)

#greenLower = (37,64,0)
#greenUpper = (100,255,211)
greenLower = (49,64,18)
greenUpper = (97,255,255)
greenLower = (36,40,76)
greenUpper = (95,255,255)


# sets the length of the trail
pts = deque(maxlen=10)
pts2 = deque(maxlen=10)

pathindex = 0
rotspeed = 200
speedfactor = 0.3
turnspeedfactor = 0.3
turntime = 0.01
bendscalefactor = 2
rdeadban = 2
tolerance = 30

#--------------  Define functions  ------------------#

def turn(v0,v1,vto):
    vm = (np.array(v0)+np.array(v1))/2.0
    ang = -(np.arctan2(vto[0]-vm[0],vto[1]-vm[1])-(np.arctan2(v1[0]-v0[0],v1[1]-v0[1])+np.pi/2))*180/np.pi
    return (np.mod(ang+180.0,360.0)-180.0)

def distance(v0,v1,vto):
    vm = (np.array(v0)+np.array(v1))/2.0
    return np.linalg.norm([vto[0]-vm[0],vto[1]-vm[1]])
    



def tracker(hsv, lowthresh, highthresh):

    mask = cv2.inRange(hsv, lowthresh, highthresh)
    #mask = cv2.erode(mask, None, iterations=2)
    #mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)   
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    return x, y, center, radius, M, cnts

def buildmask(inputarray,frame,maskdx,maskdy):
    inputarray= inputarray.astype(int)
    mask = np.ones(frame.shape)[:,:,0]
    for ii in range(len(inputarray)):
        mask[tuple(np.meshgrid(np.r_[inputarray[ii][1]-maskdx:inputarray[ii][1]+maskdx],np.r_[inputarray[ii][0]-maskdy:inputarray[ii][0]+maskdy]))]=0
    return mask

def sinfunc(xdata,border,bg,amplitude,frequency,phase):
    scaledx = ((xdata-border)*2*np.pi)/(xdata.max()-border)
    xdata = np.array([xdata]).T
    ydata = np.array([bg+(amplitude*np.sin((frequency*scaledx)+phase))]).T
    return np.concatenate((xdata,ydata),1)

def bend(array_in,pathindex):
    array_in = array_in.astype(float)
    v1,v2 = array_in[pathindex+1]-array_in[pathindex], array_in[pathindex+2]-array_in[pathindex+1]
    return np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))



###################  Setup Bluetooth   #############################

data = [0,0,0,0]
sendcount = 0

#------------------------------------------------------------------
#               For Linux / Raspberry Pi
#------------------------------------------------------------------
bd_addr = '98:D3:51:FD:81:AC' # use: 'hcitool scan' to scan for your T-Bot address
#bd_addr = '98:D3:51:FD:82:95' # George
#bd_addr = '98:D3:91:FD:46:C9' # Brenda
#bd_addr = '98:D3:32:21:3D:77'
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
#---------  Get or set destination points  ------------#




cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)


success, frame = cap.read()
if not success:
    sys.exit(1)

cap.release()

#---------  Generate target function  ------------#

amplitude = 80
frequency = 1
phase = 0
stepsize = 5
border = 80 # sets the number of pixels from the edge.
bg = frame.shape[0]/2 # the is is the background of the sin function

#----------   Create mask for coordinates   ------------#
xdata =  np.arange(border, frame.shape[1]-border, stepsize)
aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
maskdx, maskdy = 2,2 # these define the marker size
mask = buildmask(aa,frame,maskdx,maskdy)

#########################################################
#----------------   Start main loop --------------------#
#########################################################

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
#cap.set(0,1280)

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


        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) # do this outside function so is is not done twice

        try:         
            x, y, center, radius, M, cents = tracker(hsv, greenLower, greenUpper)

            if radius > 1:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), -1)
                pts.appendleft(center)
        except:

            pass
            
        try:
            x2, y2, center2, radius2, M2, cents2 = tracker(hsv, pinkLower, pinkUpper)

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

        cv2.circle(frame, tuple(aa[pathindex,:].astype(int)), 8, (250,150,10), -1)
        frame[:,:,2]=frame[:,:,2]*mask
        frame[:,:,1]=frame[:,:,1]*mask
        if laptime < oldlaptime:
            if laptime < 1000:
                textstr = 'Best time is: '+"{:6.4f}".format(laptime)
                oldlaptime = laptime
        cv2.putText(frame, textstr, org, font,fontScale, color, thickness, cv2.LINE_AA)


        cv2.imshow('MultiTracker', frame)


        ###################################################
        #---------------  Control Strategy ---------------#
        ###################################################
        
        if x != [] and x2 !=[]:
            vto = aa[pathindex] # target coordinate
            try:
                vto_next = aa[pathindex+3] # next target coordinate
            except:
                pass
            _distance = distance((x,y),(x2,y2),vto) # distance to target coordinate

            if _distance < tolerance:
                pathindex += 1  # if close enough to target coordinate, get next coordinate
                vto = aa[pathindex]
                if timeflag == 0:
                    starttime = time()
                    timeflag = 1
                    
                #pos_pid.clear()  
                #angle_pid.clear()
            

            if pathindex == len(aa)-1:
                sendcount = btcom.send_data('200200Z',sendcount)
                print('Done, reached end of path...')
                aa = np.flipud(aa)
                laptime = time()-starttime
                pathindex = 0
                timeflag = 0

            angle = turn((x,y),(x2,y2),vto)
            rotspeed = 200+angle_pid.output(0,-angle)

            straightspeedfactor = 1-np.sin(abs(angle))
            forwardspeed = 200+straightspeedfactor*(pos_pid.output(0,-_distance)+feedforward)


            #------------  build data string  ------------#

            rotspeed = '%03d' % rotspeed
        
            forwardspeed = '%03d' % forwardspeed

            print('forward speed '+forwardspeed+' turn speed '+rotspeed)
            #--------------   Send data    ---------------#
            sendstr = str(rotspeed)+str(forwardspeed)+'Z'
            sendcount = btcom.send_data(sendstr,sendcount)
            
            

        key = cv2.waitKey(1) & 0xFF
        if key == ord("x"):
            stepsize += 1
            xdata =  np.arange(border, frame.shape[1]-border, stepsize)
            aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
            mask = buildmask(aa,frame,maskdx,maskdy)
        if key == ord("z"):
            
            if stepsize > 1:
                stepsize -= 1
                xdata =  np.arange(border, frame.shape[1]-border, stepsize)
                aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
                mask = buildmask(aa,frame,maskdx,maskdy)

        if key == ord("w"):
            amplitude += 5
            aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
            mask = buildmask(aa,frame,maskdx,maskdy)
        if key == ord("s"):
            amplitude -= 5
            aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
            mask = buildmask(aa,frame,maskdx,maskdy)  
        if key == ord("d"):
            frequency += 0.5
            aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
            mask = buildmask(aa,frame,maskdx,maskdy)
        if key == ord("a"):
            frequency -= 0.5
            aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
            mask = buildmask(aa,frame,maskdx,maskdy)
        if key == ord("g"):
            speedfactor += 0.01
            print('speedfactor = '+str(speedfactor))

        if key == ord("f"):
            speedfactor -= 0.01
            print('speedfactor = '+str(speedfactor))
        if key == ord("t"):
            turnspeedfactor += 0.01
            print('turnspeedfactor = '+str(turnspeedfactor))
        if key == ord("y"):
            turnspeedfactor -= 0.01
            print('turnspeedfactor = '+str(turnspeedfactor))
            # if the 'q' key is pressed, stop the loop
        if key == ord("q"):

            cap.release()
            sendcount = btcom.send_data('200200Z',sendcount)

            break
        if record:
            if tii == 1:
                cv2.imwrite(template % iii, frame)
                iii += 5
                tii = 0
            else:
                tii += 1


cv2.destroyAllWindows()



