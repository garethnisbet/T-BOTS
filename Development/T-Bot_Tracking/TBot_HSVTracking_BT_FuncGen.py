import sys
import cv2
import imutils
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from time import time
plt.ion()
import bluetooth as bt
x = []
y = []
x2 = []
y2 = []
loopcount = 0
pathindex = 0

#----------------- set variables --------------------#

#blueLower = (96,205,185)
#blueUpper = (152,255,255)

blueLower = (89,214,139)
blueUpper = (255,255,255)



greenLower = (37,64,0)
greenUpper = (100,255,211)
#greenLower = (71,43,84)
#greenUpper = (101,255,255)



pts = deque(maxlen=200)
pts2 = deque(maxlen=200)

pathindex = 0
rotspeed = 200
speedfactor = 0.26
turnspeedfactor = 0.2
turntimefactor = 0.02
bendscalefactor = 6

#--------------  Define functions  ------------------#

def turn(v0,v1,vto):
    vm = (np.array(v0)+np.array(v1))/2.0
    ang = -(np.arctan2(vto[0]-vm[0],vto[1]-vm[1])-(np.arctan2(v1[0]-v0[0],v1[1]-v0[1])+np.pi/2))*180/np.pi
    return (np.mod(ang+180.0,360.0)-180.0)


def distance(v0,v1,vto):
    vm = (np.array(v0)+np.array(v1))/2.0
    return np.linalg.norm([vto[0]-vm[0],vto[1]-vm[1]])
    

def send(sendstr):
    try:
        builtstr = chr(0X02)+sendstr+chr(0X03)
        sock.send(builtstr.encode(encoding='utf-8'))
    except:
        sock.close()
        sys.exit()

def tracker(image, lowthresh, highthresh):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
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
oldkps, oldkp, oldtrim, oldgyro, toggle = 0,0,0,0,0


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

#######################################################
#------------- Bluetooth  Connection -----------------#
#######################################################

search = False
if search == True:
    print('Searching for devices...')
    print("")
    nearby_devices = bt.discover_devices()
    #Run through all the devices found and list their name
    num = 0
    
    for i in nearby_devices:
	    num+=1
	    print(num , ": " , bt.lookup_name( i ))
    print('Select your device by entering its coresponding number...')
    selection = input("> ") - 1
    print('You have selected - '+bt.lookup_name(nearby_devices[selection]))

    bd_addr = nearby_devices[selection]
else:
    bd_addr = '98:D3:51:FD:81:AC' # T-Bot-Demo
    print('connecting...')
error = 1
port = 1
while error:
    try:
        sock = bt.BluetoothSocket( bt.RFCOMM )
        sock.connect((bd_addr,1))
        sock.settimeout(5)
        error = 0
        print('connected to '+bd_addr)
    except:
        print('Trying again...')
        sock.close()
        error = 1

#---------  Get or set destination points  ------------#


cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)


success, frame = cap.read()
cap.release()

#---------  Generate target function  ------------#
amplitude = 70
frequency = 2
phase = 0
border = 70
bg = frame.shape[0]/2
#----------   Create mask for coordinates   ------------#
xdata =  np.arange(border, frame.shape[1]-border, 1)
aa = sinfunc(xdata,border,bg,amplitude,frequency,phase)
maskdx, maskdy = 2,2
mask = buildmask(aa,frame,maskdx,maskdy)

#########################################################
#----------------   Start main loop --------------------#
#########################################################

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
#cap.set(0,1280)
starttime = time()
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
        try:         
            x, y, center, radius, M, cents = tracker(frame, greenLower, greenUpper)

            if radius > 1:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), -1)
                pts.appendleft(center)
        except:

            pass
            
        try:
            x2, y2, center2, radius2, M2, cents2 = tracker(frame, blueLower, blueUpper)

            if radius2 > 1:
                cv2.circle(frame, (int(x2), int(y2)), int(radius2),(113,212,198), 2)
                cv2.circle(frame, center2, 2, (113,212,198), -1)
                pts2.appendleft(center2)
            
        except:
            
            pass

               
        #------------- Plot tracking overlay -----------#

        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            if pts[i - 1] is None or pts[i] is None:
                continue
     
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), 1)


        for ii in range(1, len(pts2)):
            # if either of the tracked points are None, ignore
            if pts2[ii - 1] is None or pts2[ii] is None:
                continue
     

            # draw the connecting lines
            
            cv2.line(frame, pts2[ii - 1], pts2[ii], (113,212,198), 1)

        frame[:,:,1]=frame[:,:,1]*mask
        cv2.imshow('MultiTracker', frame)


        ###################################################
        #---------------  Control Strategy ---------------#
        ###################################################
        
        if x != [] and x2 !=[]:
            vto = aa[pathindex]
            try:
                vto_next = aa[pathindex+3]
            except:
                pass
            _distance = distance((x,y),(x2,y2),vto)

            if _distance < 30:
                pathindex += 1
                vto = aa[pathindex]          

            if pathindex == len(aa)-1:
                send('200200Z')
                print('Done')
                aa = np.flipud(aa)
                pathindex = 0
                data = sock.recv(10000).decode(encoding='utf-8')
                data = []



            angle = turn((x,y),(x2,y2),vto)
            angle2 = turn((x,y),(x2,y2),vto_next)
            turnduration = np.abs(turntimefactor * angle)
            elapsedtime = time()-starttime

            if elapsedtime < turnduration:
                if angle > 0:
                    rotspeed = 200+(turnspeedfactor*100)
                    if np.abs(angle) < 5:
                        rotspeed = 200
                else:
                    rotspeed = 200-(turnspeedfactor*100)
                    if np.abs(angle) < 5:
                        rotspeed = 200
            else:
                rotspeed = 200             
                starttime = time()
            if np.abs(angle) < 40:
                if _distance > 100:
                    forwardspeed = 260
                else:
                    if pathindex < len(aa)-2:
                        bendangle = bend(aa,pathindex)
                    else:
                        bendangle = 0

                    straightspeedfactor = 1-np.sin(bendangle*bendscalefactor)
       
                    forwardspeed = 200+(straightspeedfactor*speedfactor*100)
                    #forwardspeed = 200+(speedfactor*100)

            else: 
                forwardspeed = 200



            #------------  build data string  ------------#

            rotspeed = '%03d' % rotspeed
        
            forwardspeed = '%03d' % forwardspeed


            #--------------   Send data    ---------------#

            send(rotspeed+forwardspeed+'Z')
           

        key = cv2.waitKey(1) & 0xFF

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
            send('200200Z')
            break

cv2.destroyAllWindows()



