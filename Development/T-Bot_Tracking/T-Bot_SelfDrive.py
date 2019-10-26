import sys
import cv2
import imutils
import numpy as np
from time import time

#--------------  Define functions  ------------------#


def buildmask(inputarray,frame,maskdx,maskdy):
    inputarray= inputarray.astype(int)
    mask = np.ones(frame.shape)[:,:,0]
    for ii in range(len(inputarray)):
        mask[tuple(np.meshgrid(np.r_[inputarray[ii][1]-maskdx:inputarray[ii][1]+maskdx],np.r_[inputarray[ii][0]-maskdy:inputarray[ii][0]+maskdy]))]=0
    return mask



#########################################################
#----------------   Start main loop --------------------#
#########################################################

#cap = cv2.VideoCapture('/home/gareth/Desktop/Driving.mp4')
cap = cv2.VideoCapture(0)

height = 400
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

polygons = np.array([[(0, frame_height),(0, frame_height-100), (frame_width/7, frame_height-200), (6*frame_width/7, frame_height-200),(frame_width, frame_height-100), (frame_width, frame_height)]])

mask = np.zeros((frame_height,frame_width))
diff = np.zeros((frame_height,frame_width))
gray_filtered_0ld = np.zeros((frame_height,frame_width))
cv2.fillPoly(mask, polygons, 1)
mask = mask.astype(int)

record = 0


if record:

    out = cv2.VideoWriter('outpy.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

#cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
#cap.set(0,1280)
starttime = time()
ii = 0
low_threshold = 50
high_threshold = 150
if __name__ == '__main__':
    
    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    #####################################################
    #----------------- Lane Tracker  -------------------#
    #####################################################

    while cap.isOpened():

        success, frame = cap.read()
                
        if not success:
            break
            
        #frame = cv2.resize(frame,None,fx=0.25,fy=0.25)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if ii > 1:
            gray_filtered_0ld = np.copy(gray_filtered)
        else:
            ii+=1
        gray_filtered = cv2.bilateralFilter(gray_image, 7, 50, 50)
        #diff = (np.array(gray_filtered)-np.array(gray_filtered_0ld)).astype('uint8')   

        canny_edges = cv2.Canny(gray_filtered,low_threshold,high_threshold)
        canny_edges = (canny_edges*mask).astype('uint8')
        lines = cv2.HoughLinesP(canny_edges, rho = 1, theta = 1*np.pi/90, threshold = 40, minLineLength = 75,maxLineGap = 535)
        if lines is not None:
            N = lines.shape[0]
            for i in range(N):
                x1 = lines[i][0][0]
                y1 = lines[i][0][1]    
                x2 = lines[i][0][2]
                y2 = lines[i][0][3]
                angle = np.arctan2(y1 - y2, x1 - x2)*180/np.pi;
                #print(angle)
                if np.abs(angle) > 20 and np.abs(angle) < 160: 
                    cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)
                #else: 
                    #cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),2)
       
        cv2.imshow('Edges', canny_edges)
        cv2.imshow('Overlay', frame)
        #cv2.imshow('Diff', diff)

        if record:
            out.write(frame)
        #cv2.imshow('MultiTracker', canny_edges)


        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):
            break
        
cap.release()
out.release()
cv2.destroyAllWindows()



