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


low_threshold = 140
high_threshold = 150

#########################################################
#-------        Grab frames from webcam      -----------#
#########################################################

cap = cv2.VideoCapture(0)
record = 0

sleeptime = 0.001
numframes = 10*30
folder = '3D'

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
        canny_edges = cv2.Canny(frame,low_threshold,high_threshold)
        #dst = cv2.undistort(frame, K, dist, None, newcameramtx)
        #wim1 = cv2.warpPerspective(dist, M, (635,480))
        #gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #cnts, hierarchy = cv2.findContours(canny_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        #boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        #(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b:b[1][0], reverse=False)) # sorts left to right
                   
        cv2.imshow('Frames', frame)
        cv2.imshow('Edge', canny_edges)
        
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



