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

cap = cv2.VideoCapture(1)

#cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
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
        #frame = cv2.resize(frame,None,fx=0.25,fy=0.25)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_filtered = cv2.bilateralFilter(gray_image, 7, 50, 50)
        low_threshold = 60
        high_threshold = 120
        canny_edges = cv2.Canny(gray_filtered,low_threshold,high_threshold)
        canny_edges[np.r_[0:int(frame.shape[0]/3)],:] = 0
        '''
        try:
            lines = cv2.HoughLines(canny_edges,1,np.pi/180,60)
            
            for ii in range(6):
                for rho,theta in lines[ii]:
                    print('theta min = '+ str(theta.min()) + ' theta max = '+ str(theta.max()))
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),5)
        except:
            print('Hough didn not work')
    '''
        lines = cv2.HoughLinesP(canny_edges, rho = 1, theta = 1*np.pi/90, threshold = 80, minLineLength = 75,maxLineGap = 535)
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
                else: 
                    cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),2)
        else:
            print('No lines detected')
       
        cv2.imshow('Edges', canny_edges)
        cv2.imshow('Overlay', frame)

        #cv2.imshow('MultiTracker', canny_edges)


        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break
        

cv2.destroyAllWindows()



