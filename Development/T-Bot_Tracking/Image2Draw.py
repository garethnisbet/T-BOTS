import sys
import cv2
import os
import imutils
sys.path.append('/home/pi/GitHub/T-BOTS/Joystick')
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
from TBotClasses import tbt, pid, geometry
from time import time
#imagepath = 'face.png'
imagepath = '/home/pi/Desktop/Bot.png'

filename = 'pathpoints.dat'
low_threshold = 0
high_threshold = 255

im = cv2.imread(imagepath)


gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
gim[np.where(gim > 110)]=0
gim[np.where(gim > 10)]=255


#canny_edges = cv2.Canny(gray_image,low_threshold,high_threshold)
cnts = cv2.findContours(gim, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
c = max(cnts, key=cv2.contourArea)

np.savetxt(filename,c[:,0])

plt.figure()
plt.imshow(gim)
