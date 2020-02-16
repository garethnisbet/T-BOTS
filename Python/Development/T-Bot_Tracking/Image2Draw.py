import sys
import cv2
import os
import imutils
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
from time import time
#imagepath = 'face.png'
imagepath = 'TemplateImages/Elephant.png'

filename = 'pathpoints.dat'
low_threshold = 0
high_threshold = 255

im = cv2.imread(imagepath)

im = cv2.bitwise_not(im)
gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
cnts = cv2.findContours(gim, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
c = max(cnts, key=cv2.contourArea)

np.savetxt(filename,c[:,0])

plt.figure()
plt.imshow(gim)
