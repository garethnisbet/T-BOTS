import sys
import cv2
import os
import imutils
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import tbt, pid, geometry
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from time import time

imagepath = 'TemplateImages/Elephant.png'
imagepath = 'TemplateImages/Track.png'
#imagepath = 'TemplateImages/Butterfly.png'
#imagepath = 'TemplateImages/Bot.png'
#imagepath = 'TemplateImages/hex.png'
#imagepath = 'TemplateImages/starfish.png'
#imagepath = 'TemplateImages/MiniMaze.png'
#imagepath = 'TemplateImages/T-Bot.png'
#imagepath = 'TemplateImages/Car.png'
#imagepath = 'TemplateImages/Plane.png'



filename = 'pathpoints.dat'
low_threshold = 0
high_threshold = 255
geom = geometry.geometry()
im = cv2.imread(imagepath, cv2.IMREAD_UNCHANGED)

#------------------  Check for, and remove alpha  ---------------------#
if im.shape[-1]>3:
	trans_mask = im[:,:,3] == 0
	im[trans_mask] = [255, 255, 255, 255]
	im = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
#----------------------------------------------------------------------#

aa = geom.image2path(im)
np.savetxt(filename,aa)

zeroim = im*0
cv2.polylines(zeroim, np.int32([aa]),True, (255,0,255),2)
cv2.imshow('MultiTracker', zeroim)

plt.figure()
plt.imshow(im)
plt.figure()
plt.imshow(zeroim)

