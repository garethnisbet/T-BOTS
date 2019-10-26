import sys
import cv2
import numpy as np
from time import sleep
import imutils
from scipy.ndimage.filters import gaussian_filter
#########################################################
#-------        Curved Lane Detection        -----------#
#########################################################

cap = cv2.VideoCapture(0)

# ------        Get correction files            --------#

K = np.load("./camera_params/K.npy")
dist = np.load("./camera_params/dist.npy")

h,  w = int(cap.get(3)),int(cap.get(4))
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(K,dist,(w,h),1,(w,h))

empty = np.zeros((500,635,3))
# ----------------------------------------------------- #
frame_height = empty.shape[0]
frame_width = empty.shape[1]
polygons = np.array([[(0,0),(634,0),(634,388),(497,500),(136,500),(0,368)]])

mask = np.zeros((frame_height,frame_width))
cv2.fillPoly(mask, polygons, 1)

#src = np.array([[202,331],[440,332],[25,479],[602,479]],np.float32)
#dst=np.float32([[0,0],[602,0],[0,490],[602,490]])

src = np.array([[176,394],[251,297],[379,297],[450,394]],np.float32)
dst=np.float32([[176,394],[176,66],[450,66],[450,394]])


M = cv2.getPerspectiveTransform(src, dst)
iM = np.matrix(M).I
low_threshold = 50
high_threshold = 150

lowthresh = (0,0,184)
highthresh = (198,255,255)
alpha = 1.5 # Contrast control (1.0-3.0)
beta = 0 # Brightness control (0-100)
if __name__ == '__main__':
    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)
    while cap.isOpened():
        success, frame = cap.read()
        frame = cv2.undistort(frame, K, dist, None, newcameramtx)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray_filtered = cv2.bilateralFilter(gray_image, 7, 50, 50)

        adjusted = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
        adjusted[np.where(adjusted < np.percentile(adjusted,98))]=0
        median = cv2.medianBlur(gray_image,5)
        canny_edges = cv2.Canny(adjusted,low_threshold,high_threshold)
        
        
        #imsum = (np.sum(frame,2)/3.).astype(np.uint8)
        #imsum = cv2.bitwise_not(imsum) # invert
        #lpf = gaussian_filter(imsum,10,0)
        #hps = imsum - lpf
        #mask = cv2.erode(imsum, None, iterations=4)
        #mask = cv2.dilate(mask, None, iterations=3)


        
        
        warped = cv2.warpPerspective(canny_edges , M, (635,500))
        #warped[np.where(warped < np.percentile(warped,85))] = 0
        warped = (mask*warped).astype(np.uint8)
        cnts = cv2.findContours(warped.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cntsSorted = sorted(cnts, key=lambda x: cv2.contourArea(x))

        empty[:,:,0] = warped
        try:
            for contour in range(4):
                cv2.drawContours(empty, cntsSorted[-contour][np.r_[0:cntsSorted[-contour].shape[0]:5]], -1, (0, 0, 255), 2)
        #inv_warped = cv2.warpPerspective(warped, iM, (635,500))
        except:
            pass
        
        if not success:
            break
        cv2.imshow('Frames', frame)
        cv2.imshow('Warped', warped)
        cv2.imshow('imsum', median)
        cv2.imshow('Contours', empty)
        cv2.imshow('Contrast',adjusted)
        empty[:,:,:] = 0
        #cv2.imshow('Warped Colour', warpedC)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        
cap.release()

cv2.destroyAllWindows()




