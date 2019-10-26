import sys
import os
import cv2
import numpy as np
from time import sleep
from time import time


K = np.load("./camera_params/K.npy")
dist = np.load("./camera_params/dist.npy")

img = cv2.imread('./frames/00023.png')
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(K,dist,(w,h),1,(w,h))

src = np.array([[176,394],[251,297],[379,297],[450,394]],np.float32)
dst=np.float32([[176,394],[176,66],[450,66],[450,394]])


M = cv2.getPerspectiveTransform(src, dst)


low_threshold = 50
high_threshold = 150

alpha = 1.5 # Contrast control (1.0-3.0)
beta = 0 # Brightness control (0-100)

#########################################################
#-------        Grab frames from webcam      -----------#
#########################################################

cap = cv2.VideoCapture(0)
record = 0

sleeptime = 0.001
numframes = 10*30
folder = '3D'
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
polygons = np.array([[(0, frame_height),(0, frame_height-100), (frame_width/7, frame_height-200), (6*frame_width/7, frame_height-200),(frame_width, frame_height-100), (frame_width, frame_height)]])
mask = np.zeros((frame_height,frame_width))
cv2.fillPoly(mask, polygons, 1)
mask = mask.astype(int)
#folder = 'SpeedTest/'
if record:
    if os.path.isdir(folder) is not True:
        os.mkdir(folder)
template = folder + '%05d.png'


iii = 0
oldtime = time()
if __name__ == '__main__':
    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)
    while cap.isOpened():
        
        
        success, frame = cap.read()
        if not success:
            break
        '''    
        #adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        canny_edges = cv2.Canny(frame,low_threshold,high_threshold)
        canny_edges = (canny_edges*mask).astype('uint8')
        #dst = cv2.undistort(frame, K, dist, None, newcameramtx)
        #wim1 = cv2.warpPerspective(dist, M, (635,480))
        lines = cv2.HoughLinesP(canny_edges, rho = 1, theta = 1*np.pi/90, threshold = 40, minLineLength = 60,maxLineGap = 100)
        if lines is not None:
            N = lines.shape[0]
            if N > 6:
                numlines = range(6)
            else:
                numlines = range(N)
            for i in numlines:
                x1 = lines[i][0][0]
                y1 = lines[i][0][1]    
                x2 = lines[i][0][2]
                y2 = lines[i][0][3]
                angle = np.arctan2(y1 - y2, x1 - x2)*180/np.pi;
                #print(angle)
                if np.abs(angle) > 20 and np.abs(angle) < 160: 
                    cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)
                #else: 
                #    cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),2)
        '''
        
        cv2.imshow('Frames', frame)
        #cv2.imshow('Canny Edges',canny_edges)
        
        if record:
            cv2.imwrite(template % iii, frame) 
        key = cv2.waitKey(1) & 0xFF
        sleep(sleeptime)

        if key == ord("q"):
            break
        if iii > numframes:
            break
        if record:
            iii+=1     
        print(1/(time()-oldtime))
        oldtime = time()
cap.release()
#out.release()
cv2.destroyAllWindows()



