import sys
import cv2
import PID
from random import randint
import matplotlib.pyplot as plt
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import tbt, pid, geometry
plt.ion()
import numpy as np
import bluetooth as bt
pid = PID.PID(0.2,10,0) # P I D
pid.SetPoint = 0
pid.setSampleTime(0.1)
forwardspeed = '%03d' % 220
geom = geometry.geometry(1)
#--------------------- Setup Bluetooth --------------------------------#
data = [0,0,0,0]
sendcount = 0

#------------------------------------------------------------------
#               For Linux / Raspberry Pi
#------------------------------------------------------------------
bd_addr = '98:D3:51:FD:81:AC' # use: 'hcitool scan' to scan for your T-Bot address
#bd_addr = '98:D3:51:FD:82:95' # George
#bd_addr = '98:D3:91:FD:46:C9' # B
#bd_addr = '98:D3:32:21:3D:77'
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




#########  Get image and set coordinates  ##################
numpathpoints = 19


try:
    aa = np.loadtxt('pathpoints.dat')
    nomapdata = 0
except:
    nomapdata = 1


tracker = cv2.TrackerCSRT_create()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)

cap.set(0,1280)
success, frame = cap.read()

#-----------------  Generate target function  -------------------------#


amplitude = 80
frequency = 1.5
phase = 0
stepsize = 5
border = 80 # sets the number of pixels from the edge which wont be occupied by the function.
bg = frame.shape[0]/2 # this is the background of the sin function


xdata =  np.arange(border, frame.shape[1]-border, stepsize)
aa = geom.sinfuncM(xdata,border,bg,amplitude,frequency,phase)



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
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
cap.set(0,1280)

############   Start main loop #############################

if __name__ == '__main__':


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
        _distance = geom.distanceSingle(v1,vto)
        if _distance < 30:
            pathindex += 1
        if pathindex == len(aa):
            sendcount = btcom.send_data('200200Z',sendcount)

            print('Done')
            break
        
        angle = geom.angle(v0,v1,vto)
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
        
        if geom.distanceSingle(v0,v1) < 1:
            rotspeed = 200
            forwardspeed = 225

        rotspeed = '%03d' % rotspeed
        forwardspeed = '%03d' % forwardspeed
        sendcount = btcom.send_data(rotspeed+forwardspeed+'Z',sendcount)
        

        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:    # Esc pressed
            sendcount = btcom.send_data('200200Z',sendcount)
            
            break

