import sys
import cv2
import PID
from random import randint
import matplotlib.pyplot as plt
plt.ion()
import numpy as np
import bluetooth as bt
pid = PID.PID(0.2,10,0) # P I D
pid.SetPoint = 0
pid.setSampleTime(0.1)
forwardspeed = '%03d' % 220
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
        

###############  Functions   #######################

def turn(v0,v1,vto):
    ang = -(np.arctan2(vto[0]-v1[0],vto[1]-v1[1])-np.arctan2(v1[0]-v0[0],v1[1]-v0[1]))*180/np.pi
    return (np.mod(ang+180.0,360.0)-180.0)


def distance(vto,v1):
    return np.linalg.norm([vto[0]-v1[0],vto[1]-v1[1]])
    

def send(sendstr):
    try:
        builtstr = chr(0X02)+sendstr+chr(0X03)
        sock.send(builtstr.encode(encoding='utf-8'))
    except:
        sock.close()
        sys.exit()

#########  Get image and set coordinates  ##################
numpathpoints = 19


try:
    aa = np.loadtxt('pathpoints.dat')
    nomapdata = 0
except:
    nomapdata = 1


tracker = cv2.TrackerCSRT_create()
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)

cap.set(0,1280)
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


################  Setup some counters   ####################
ii = 0
iii = 0
pathindex = 0
v0 = [0,0]
v1 = [0,0]


# Create a video capture object
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
cap.set(0,1280)

############   Start main loop #############################

if __name__ == '__main__':

    # Read first frame to select ROI
    success, frame = cap.read()
    # quit if unable to read the from camera
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    ## Select boxes
    bboxes = []
    colors = [] 

    # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
    # So we will call this function in a loop till we are done selecting all objects

    while True:
        # draw bounding boxes over objects
        # selectROI's default behaviour is to draw box starting from the center
        # when fromCenter is set to false, you can draw box starting from top left corner
        bbox = cv2.selectROI('MultiTracker', frame)
        bboxes.append(bbox)
        #colors.append((randint(64, 255), randint(64, 255), randint(64, 255)))
        colors.append((0,0,0))
        print("Press q to quit selecting boxes and start tracking")
        print("Press any other key to select next object")
        k = cv2.waitKey(0) & 0xFF
        if (k == 113):    # q is pressed
            break
    
    print('Selected bounding boxes {}'.format(bboxes))

    ## Initialize MultiTracker
    multiTracker = cv2.MultiTracker_create()

    for bbox in bboxes:
        multiTracker.add(tracker, frame, bbox)


    # Process video stream and track objects
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # get updated location of objects in subsequent frames
        success, boxes = multiTracker.update(frame)

        # draw tracked objects
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)

            #extract coordinates from tracker
            if ii == 0:
                v0 = [(p1[0]+p2[0])/2.0,(p1[1]+p2[1])/2.0]
                ii = 1
            else:
                v1 = [(p1[0]+p2[0])/2.0,(p1[1]+p2[1])/2.0]
                ii = 0


        # show frame
        frame[:,:,1]=frame[:,:,1]*mask
        cv2.imshow('MultiTracker', frame)

        #extract coordinates from tracker 


        vto = aa[pathindex]
        _distance = distance(vto,v1)
        if _distance < 30:
            pathindex += 1
        if pathindex == len(aa):
            send('200200Z')
            print('Done')
            break
        
        angle = turn(v0,v1,vto)
        pid.update(angle)
        rotspeed = pid.output+200
        rspeedfactor = 30
        if rotspeed >=200 + rspeedfactor:
            rotspeed = 200 + rspeedfactor
        elif rotspeed <=200 - rspeedfactor:
            rotspeed = 200 - rspeedfactor
        
        forwardspeed = 220+(_distance/np.max(frame.shape))*50
        if forwardspeed > 300:
            forwardspeed = 300
        
        if distance(v0,v1) < 1:
            rotspeed = 200
            forwardspeed = 225

        rotspeed = '%03d' % rotspeed
        forwardspeed = '%03d' % forwardspeed
        send(rotspeed+forwardspeed+'Z')
        

        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:    # Esc pressed
            send('200200Z')
            
            break

