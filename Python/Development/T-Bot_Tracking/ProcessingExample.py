import sys
import cv2
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage.filters import gaussian_filter
from scipy import ndimage
plt.ion()

def buildmask(inputarray,frame,maskdx,maskdy):
    inputarray= inputarray.astype(int)
    mask = np.ones(frame.shape)[:,:]
    for ii in range(len(inputarray)):
        mask[tuple(np.meshgrid(np.r_[inputarray[ii][1]-maskdx:inputarray[ii][1]+maskdx],np.r_[inputarray[ii][0]-maskdy:inputarray[ii][0]+maskdy]))]=0
    return mask


def poly(x, a, b, c, d):
  return a + b * x + c * x ** 2 + d * x ** 3

#------------  Transformation for birds eye view  -------------#
#src = np.array([[202,331],[440,332],[25,479],[602,479]],np.float32)
#dst=np.float32([[0,0],[602,0],[0,490],[602,490]])

src = np.array([[176,394],[251,297],[379,297],[450,394]],np.float32)
dst=np.float32([[176,394],[176,66-50],[450,66-50],[450,394]])


M = cv2.getPerspectiveTransform(src, dst)
iM = np.matrix(M).I

#im1 = cv2.imread('frames/00010.png')
#im1 = cv2.imread('frames/00044.png')
im1 = cv2.imread('3D/00200.png')


wim1 = cv2.warpPerspective(im1, M, (635,500))
swim1 = np.sum(wim1,2)


roisV = np.linspace(swim1.shape[0],2*swim1.shape[0]/3,6).astype(int)


#roisV = np.linspace(int(swim1.shape[0]/2),swim1.shape[0],20).astype(int)

roisH = np.linspace(0, swim1.shape[1],3).astype(int)
Lcentre = int(swim1.shape[1]/4)
Rcentre = int(3*swim1.shape[1]/4)
Lcentres = np.array(3*[[]]).T
Rcentres = np.array(3*[[]]).T

for ii in range(roisV.shape[0]-1):
	CL = np.sum(swim1[tuple(np.meshgrid(np.r_[roisV[ii+1]:roisV[ii]],np.r_[Lcentre-70:Lcentre+70]))].T,0)
	L = np.mean(np.where(CL > np.percentile(CL,90))).astype(int)+Lcentre-70
	CR = np.sum(swim1[tuple(np.meshgrid(np.r_[roisV[ii+1]:roisV[ii]],np.r_[Rcentre-70:Rcentre+70]))].T,0)
	R = np.mean(np.where(CR > np.percentile(CR,90))).astype(int)+Rcentre-70
	Lcentre = L
	Rcentre = R
	Y = int((roisV[ii]+roisV[ii+1])/2)
	Lcentres = np.vstack((Lcentres,[[L,Y,0]]))
	Rcentres = np.vstack((Rcentres,[[R,Y,0]]))
	
Lcentres  = Lcentres.astype(int)

Lpopt, Lpcov = curve_fit(poly, roisV[:-1], Lcentres[:,0])
Rcentres  = Rcentres.astype(int)
mask1 = buildmask(np.concatenate((Lcentres,Rcentres,(Lcentres+Rcentres)/2)),swim1,5,5)


plt.figure(figsize=(16,6))
plt.plot()
plt.subplot(2,2,1)
plt.imshow(swim1*mask1)
maski = np.ceil(cv2.warpPerspective(mask1, iM, (640,480))).astype(int)

im1[:,:,0] = im1[:,:,0]*maski
plt.subplot(2,2,2)
plt.imshow(im1)
plt.subplot(2,2,3)
plt.plot(roisV[:-1],Lcentres[:,0],roisV[:-1],poly(roisV[:-1],Lpopt[0],Lpopt[1],Lpopt[2],Lpopt[3]))
plt.subplot(2,2,4)
plt.plot(np.diff(Lcentres[:,0]),'-x')
plt.plot(np.diff(Rcentres[:,0]),'-.')

