import sys
import cv2
import os
import imutils
sys.path.append('/home/gareth/GitHub/T-BOTS/Python')
from TBotTools import tbt, pid, geometry
import numpy as np
#plt.ion()
from time import time
#imagepath = 'face.png'
imagepath = 'TemplateImages/Elephant.png'
import matplotlib.pyplot as plt
plt.ion()
filename = 'pathpoints.dat'
low_threshold = 0
high_threshold = 255
geom = geometry.geometry()
im = cv2.imread(imagepath)
aa = geom.image2path(im)
np.savetxt(filename,aa)

zeroim = im*0
cv2.polylines(zeroim, np.int32([aa]),True, (255,0,255),2)
cv2.imshow('MultiTracker', zeroim)

plt.figure()
plt.imshow(im)
plt.figure()
plt.imshow(zeroim)

