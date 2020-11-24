#!/usr/bin/python
import numpy as np
import cv2
import imutils

class geometry(object):
    '''Geometry tools for using a webcam to control the T-Bot''' 
    def __init__(self,scalefactor=[]):
        '''Usage geom = geometry(scalefactor) where the scale factor maps the camera resolution to the real distance on the floor'''
        if scalefactor == []:
            self.scalefactor = 1
        else:
            self.scalefactor = scalefactor

    def tracker(self,hsv, lowthresh, highthresh):
        '''Tracker uses the hsv colour space to track specific colored objects''' 
        mask = cv2.inRange(hsv, lowthresh, highthresh)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)   
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return x, y, center, radius, M, cnts

    def buildmask(self,inputarray,frame,maskdx,maskdy):
        '''Simple mask builder to overlay arbitrary array''' 
        inputarray= inputarray.astype(int)
        mask = np.ones(frame.shape)[:,:,0]
        for ii in range(len(inputarray)):
            mask[tuple(np.meshgrid(np.r_[inputarray[ii][1]-maskdx:inputarray[ii][1]+maskdx],np.r_[inputarray[ii][0]-maskdy:inputarray[ii][0]+maskdy]))]=0
        return mask

    def sinfunc(self,xdata,border,bg,amplitude,frequency,phase):
        '''Generates a sine function'''
        scaledx = ((xdata-border)*2*np.pi)/(xdata.max()-border)
        xdata = np.array([xdata]).T
        ydata = np.array([bg+(amplitude*np.sin((frequency*scaledx)+phase))]).T
        return np.concatenate((xdata,ydata),1)
        
    def sinfuncM(self,xdata,border,bg,amplitude,frequency,phase):
        '''Generates a sine function and it's reflection about the horizontal axis'''
        frequency = float(frequency)
        scaledx = ((xdata-border)*2*np.pi)/(xdata.max()-border)
        ydata = bg+(amplitude*np.sin((frequency*scaledx)+phase))
        if frequency.is_integer():
            ydata2 = bg+(amplitude*-np.sin((frequency*scaledx)+phase+np.pi))
        else:
            ydata2 = bg+(amplitude*-np.sin((frequency*scaledx)+phase))
        xdata = np.concatenate((np.array([xdata]),np.fliplr(np.array([xdata]))),1).T
        ydata = np.concatenate((np.array([ydata]),np.array([ydata2])),1).T
        return np.concatenate((xdata,ydata),1)
        
    def circlefunc(self,origin,radius,n):
        x = np.linspace(-np.pi,np.pi,n)
        xdata = np.array([np.cos(x)*radius+origin[1]]).T
        ydata = np.array([np.sin(x)*radius+origin[0]]).T
        return np.concatenate((xdata,ydata),1)

    def orientation(self,v0,v1):
        '''Calculates the angle of the T-Bot with respect frame'''
        vm = (np.array(v0)+np.array(v1))/2.0
        ang = (np.arctan2(v1[0]-v0[0],v0[1]-v1[1])-np.pi/2)*180/np.pi
        return [vm, ang]

    def angle(self,v0,v1,vto):
        '''Calculates the angle of the T-Bot with respect to a target coordinate'''
        vm = (np.array(v0)+np.array(v1))/2.0
        ang = -(np.arctan2(vto[0]-vm[0],vto[1]-vm[1])-(np.arctan2(v1[0]-v0[0],v1[1]-v0[1])+np.pi/2))*180/np.pi
        return (np.mod(ang+180.0,360.0)-180.0)

    def bend(self,array_in,pathindex):
        '''Calculates the angle between two vectors'''
        v0,v1,v2 = array_in[pathindex], array_in[pathindex+1], array_in[pathindex+2]
        ang = -((np.arctan2(v2[0]-v1[0],v2[1]-v1[1])-np.arctan2(v1[0]-v0[0],v1[1]-v0[1]))+np.pi)*180/np.pi
        return (np.mod(ang+180.0,360.0)-180.0)

    def distance(self,v0,v1,vto):
        '''Calculates the distance the T-Bot is from a target coordinate. If the scale factor is 1 the units are in pixels'''
        vm = (np.array(v0)+np.array(v1))/2.0
        return np.linalg.norm([vto[0]-vm[0],vto[1]-vm[1]])*self.scalefactor
        
    def distanceSingle(self,v0,vto):
        '''Calculates the distance the T-Bot is from a target coordinate. If the scale factor is 1 the units are in pixels'''
        return np.linalg.norm([vto[0]-v0[0],vto[1]-v0[1]])*self.scalefactor
      
    def image2path(self,im):
        imi = cv2.bitwise_not(im)
        gim = cv2.cvtColor(imi, cv2.COLOR_BGR2GRAY)
        cnts = cv2.findContours(gim, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return max(cnts, key=cv2.contourArea)[:,0]
        
    def rotxy(self,theta,v1):
        return (np.matrix([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])*v1.T).T

    def v2ang(self,h,g,v):
        if v < 0:
            angout = -np.arccos(1-((v**2)/(2*g*h)))
        elif v > 0:
            angout = np.arccos(1-((v**2)/(2*g*h)))
        else:
            angout = 0
        if np.isnan(angout):
            angout = 0
        return angout

    def v(self,l,g,theta):
        if theta != 0:
            return np.sqrt(2*g*(l-l*np.cos(theta)))*theta/np.abs(theta)
        else:
            return 0.0
