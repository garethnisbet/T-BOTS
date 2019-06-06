import sys
import cv2
import imutils
from collections import deque
import PID
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
import bluetooth as bt
x = []
y = []
x2 = []
y2 = []
loopcount = 0
#################### set variables ###################

pid = PID.PID(5,50,0) # P I D
pid.SetPoint = 0
pid.setSampleTime(0.1)
forwardspeed = 200
blueLower = (96,170,150)
blueUpper = (131,255,247)

greenLower = (37,64,0)
greenUpper = (100,255,211)

pts = deque(maxlen=22)
pts2 = deque(maxlen=22)


pathindex = 0
rotspeed = 200
#################  Define functions  #################

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
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)   
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    return x, y, center, radius, M, cnts

###################  Connection #############################

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

################  Get or set destination points  ##########
numpathpoints = 60

try:
    aa = np.loadtxt('pathpoints.dat')
    nomapdata = 0
except:
    nomapdata = 1
cap = cv2.VideoCapture(1)
success, frame = cap.read()
if nomapdata:
    plt.figure()
    plt.imshow(frame)
    aa = plt.ginput(numpathpoints,0)
    aa = map(list,np.array(aa).astype(int))
    np.savetxt('pathpoints.dat',aa)
    plt.close()
else:
    aa = aa.astype(int)
cap.release()

###########  Create mask for coordinates   #################
mask = np.ones(frame.shape)[:,:,0]
print(mask.shape)
maskdx, maskdy = 2,2
for ii in range(len(aa)):
    mask[np.meshgrid(np.r_[aa[ii][1]-maskdx:aa[ii][1]+maskdx],np.r_[aa[ii][0]-maskdy:aa[ii][0]+maskdy])]=0





############   Start main loop #############################

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
#cap.set(0,1280)
if __name__ == '__main__':

    # Create a video capture object
    # Read first frame to select ROI
    success, frame = cap.read()
    # quit if unable to read the from camera
    if not success:
        print('Failed to capture video')
        sys.exit(1)


    ##############  find circles  ###########################
 
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        try:         
            x, y, center, radius, M, cents = tracker(frame, greenLower, greenUpper)

            if radius > 3:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 255, 0), -1)
                pts.appendleft(center)
        except:

            pass
            
        try:
            x2, y2, center2, radius2, M2, cents2 = tracker(frame, blueLower, blueUpper)

            if radius2 > 3:
                cv2.circle(frame, (int(x2), int(y2)), int(radius2),(113,212,198), 2)
                cv2.circle(frame, center2, 2, (113,212,198), -1)
                pts2.appendleft(center2)
            
        except:
            
            pass
        
        #################  Plot tracking overlay  ###############

        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue
     
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            #thickness = int(np.sqrt(22 / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 255, 0), 1)


        for ii in range(1, len(pts2)):
            # if either of the tracked points are None, ignore
            # them
            if pts2[ii - 1] is None or pts2[ii] is None:
                continue
     
            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            #thickness2 = int(np.sqrt(22 / float(i + 1)) * 2.5)
            cv2.line(frame, pts2[ii - 1], pts2[ii], (113,212,198), 1)
     
        # Display frame

        frame[:,:,1]=frame[:,:,1]*mask
        cv2.imshow('MultiTracker', frame)



        #####  calculate speed and rotations and send signals to T-Bot ####
        if x != [] and x2 !=[]:
            vto = aa[pathindex]
            _distance = distance((x,y),(x2,y2),vto)
            if _distance < 40:
                pathindex += 1
            if pathindex == len(aa):
                send('200200Z')
                print('Done')
                break

            angle = turn((x,y),(x2,y2),vto)
            pid.update(-angle)

            rotspeed = pid.output+200

            if np.abs(angle) > 25:
                
                forwardspeed = 200
            else:
                loopcount += 2 # accelerate loop count
                forwardspeed = 210+(_distance)*0.1


            ###################  Set Limits  ################

            if forwardspeed > 220:
                forwardspeed = 220

            rspeedfactor = 40

            if rotspeed >=200 + rspeedfactor:
                rotspeed = 200 + rspeedfactor
            elif rotspeed <=200 - rspeedfactor:
                rotspeed = 200 - rspeedfactor

            ##############  build data string  ##############

            rotspeed = '%03d' % rotspeed
        
            forwardspeed = '%03d' % forwardspeed


            #################   Send data    ###############

            if loopcount < 6:
                send(rotspeed+forwardspeed+'Z')
            else:
               send('200'+forwardspeed+'Z')

            loopcount +=1
            if loopcount > 20:
               loopcount = 0             

        key = cv2.waitKey(1) & 0xFF
     
            # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            cap.release()
            send('200200Z')
            break

cv2.destroyAllWindows()



