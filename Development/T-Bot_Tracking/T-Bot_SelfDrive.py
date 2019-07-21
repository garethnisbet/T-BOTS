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

def region_of_interest(img, vertices):
    # Define a blank matrix that matches the image height/width.
    mask = np.zeros_like(img)
    # Retrieve the number of color channels of the image.
    channel_count = img.shape[2]
    # Create a match color with the same color channel counts.
    match_mask_color = (255,) * channel_count
      
    # Fill inside the polygon
    cv2.fillPoly(mask, vertices, match_mask_color)
    
    # Returning the image only where mask pixels match
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

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
        empty = np.zeros(frame.shape)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lowthresh = np.array([0,0, 212], dtype = 'uint8')
        highthresh = np.array([191,32,237], dtype='uint8')
        mask = cv2.inRange(img_hsv, lowthresh, highthresh)
        #cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#        mask_yellow = cv2.inRange(img_hsv, lower_yellow, upper_yellow)
#        mask_white = cv2.inRange(gray_image, 200, 255)
 #       mask_yw = cv2.bitwise_or(mask_white, mask_yellow)
#        mask_yw_image = cv2.bitwise_and(gray_image, mask_yw)
        gauss_gray = blurred = cv2.GaussianBlur(mask, (11, 11), 0)
        low_threshold = 100
        high_threshold = 150
        canny_edges = cv2.Canny(gauss_gray,low_threshold,high_threshold)
        #roi_image = region_of_interest(canny_edges, vertices)
        
        
        try:
            lines = cv2.HoughLines(canny_edges,1,np.pi/180,10)
            for ii in range(5):
                for rho,theta in lines[ii]:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),1)
        except:
            print('Hough didn not work')

        '''
        lines = cv2.HoughLinesP(canny_edges, rho = 1, theta = 1*np.pi/180, threshold = 100, minLineLength = 50,maxLineGap = 500)
        N = lines.shape[0]
        for i in range(N):
            x1 = lines[i][0][0]
            y1 = lines[i][0][1]    
            x2 = lines[i][0][2]
            y2 = lines[i][0][3]    
            cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)
        '''

        cv2.imshow('Overlay', frame)
        cv2.imshow('Edges', canny_edges)
        #cv2.imshow('MultiTracker', canny_edges)


        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break
        

cv2.destroyAllWindows()



