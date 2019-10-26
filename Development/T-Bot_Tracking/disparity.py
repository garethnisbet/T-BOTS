import sys
import cv2
import numpy as np
from time import sleep
import imutils
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
plt.ion()


low_threshold = 50
high_threshold = 150
# loading the stereo pair
left  = cv2.imread('frames/00015.png')
left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
cleft = cv2.Canny(left,low_threshold,high_threshold)
left_r = imutils.rotate_bound(cleft, 90)
right = cv2.imread('frames/00016.png')
right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
cright = cv2.Canny(right,low_threshold,high_threshold)
right_r = imutils.rotate_bound(cright, 90)

stereo = cv2.StereoBM_create(numDisparities = 32, blockSize = 17)
disparity = stereo.compute(left_r, right_r)
disparity = imutils.rotate_bound(disparity, -90)
plt.figure(figsize=(16,6))
plt.subplot(1,3,1)
plt.imshow(cleft+cright)
plt.subplot(1,3,2)
plt.imshow(cleft-cright)
plt.subplot(1,3,3)
plt.imshow(cright)
#plt.imshow(disparity)
# ~ fig = plt.figure()
# ~ ax = fig.gca(projection='3d')
# ~ x,y = np.meshgrid(range(disparity.shape[1]), range(disparity.shape[0]))
# ~ surf = ax.plot_surface(x,y, disparity, cmap=cm.coolwarm,
                       # ~ linewidth=0, antialiased=False)



