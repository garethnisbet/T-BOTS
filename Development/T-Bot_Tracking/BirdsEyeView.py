import sys
import cv2
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import ndimage
plt.ion()

#------------  Transformation for birds eye view  -------------#

src = np.array([[202,331],[440,332],[25,479],[602,479]],np.float32)
dst=np.float32([[0,0],[602,0],[0,490],[602,490]])

src = np.array([[176,394],[251,297],[379,297],[450,394]],np.float32)
dst=np.float32([[176,394],[176,66],[450,66],[450,394]])


M = cv2.getPerspectiveTransform(src, dst)

#im1 = cv2.imread('frames/00100.png')
im1 = cv2.imread('3D/00182.png')

K = np.load("./camera_params/K.npy")
dist = np.load("./camera_params/dist.npy")
h,  w = im1.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(K,dist,(w,h),1,(w,h))
dst = cv2.undistort(im1, K, dist, None, newcameramtx)



wim1 = cv2.warpPerspective(dst, M, (635,480))
swim1 = np.sum(wim1,2)

plt.figure()
plt.imshow(swim1)
plt.figure()
plt.imshow(im1)
