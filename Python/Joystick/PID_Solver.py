#!/usr/bin/python
import sys, os
import numpy as np
sys.path.append('/home/gareth/GitHub/T-BOTS/Python')
from TBotTools import pid, geometry
from time import time
from scipy.optimize import minimize
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt
plt.ion()


# ------------------------- Physics and Controls -----------------------
#
#   Note, the T-Bot motor is geared so when the robot falls over, the   
#   lateral force exerted on the wheel is insufficient to turn the motor 
#   which simplifies the equations.   
#
# ---------------------------------------------------------------------- 

sf = 0.1
#sf = 0.165 # For the moon
#sf = 1 # For the Earth
framerate = 50 # set to 30 for Rasoberry pi
dt = 1.0/framerate 
acc_g = 9.81 
h = 0.08
t = 0
alpha = 0
gamma = 0
acc = 0
omega = 0
velocity = 0
distance = 0
theta = np.pi+0.001
targetvelocity = 0

geom = geometry.geometry()



#------------------------- Tuning for Earth -----------------------
s_kpo, s_kio, s_kdo = 0.050, 0.147, 0.041
a_kpo, a_kio, a_kdo = 1.898, 0.006, 0.067
#----------------------------------------------------------------------

g = acc_g * sf


class PID_Min(object):
    def __init__(self,*args):
        self.g=args[0]
        self.h=args[1]
        self.dt = args[2]

    def amplitude(self,*inputs):
        inputs=inputs[0]
        self.s_kp = inputs[0]
        self.s_ki = inputs[1]
        self.s_kd = inputs[2]
        self.a_kp = inputs[3]
        self.a_ki = inputs[4]
        self.a_kd = inputs[5]
        self.speed_pid = pid.pid(self.s_kp, self.s_ki, self.s_kd,[-10,10],[-5,5],self.dt)
        self.angle_pid = pid.pid(self.a_kp, self.a_ki, self.a_kd,[-6,6],[-1,1],self.dt)
        v1 = np.array([[]]*1).T
        theta = 0.99*np.pi
        acc = 0
        omega = 0
        velocity = 0
        distance = 0
        for ii in range(1000):
            if theta >= np.pi/1.845 and theta <= 1.43*np.pi:
                alpha =  -np.sin(theta)*self.g/self.h
                gamma =  -np.cos(theta)*acc/self.h
                a_acc = alpha-gamma
                # integrate angular acceleration to get angular velocity
                omega += a_acc*self.dt
                # integrate angular velocity to get angle
                theta += omega*self.dt
                # integrate dt to get time
                velocity += acc*self.dt
                distance += velocity*self.dt
                noise = np.random.rand(1)*np.pi/180
                noise = [1]
                settheta = -self.speed_pid.output(geom.v2ang(h,g,targetvelocity),-geom.v2ang(h,g,velocity),self.dt)
                acc = -self.angle_pid.output(np.pi+settheta,(theta+noise[0]),self.dt)
                v1 = np.vstack((v1,(theta-np.pi)*distance))
        self.v1 = v1
        self.amp = np.abs(v1).max()
    def fit(self,inputs):
        try:
            self.amplitude(inputs)
            return self.amp # adding attribute
        except:
            return 500


PIDFIT = PID_Min(g,h,dt)
ig = [s_kpo, s_kio, s_kdo, a_kpo, a_kio, a_kdo]
#res = minimize(PIDFIT.fit, ig, method='Powell')
#res = minimize(PIDFIT.fit, ig, method='Nelder-Mead')
#res = minimize(PIDFIT.fit, ig,method='TNC')

iglow = np.array(ig) - 1.0
ighigh = np.array(ig) + 1.0
iglow[iglow<0] = 0
bounds=tuple(zip(iglow,ighigh))
res = differential_evolution(PIDFIT.fit,bounds,strategy='best1exp',polish=True)


PIDFIT.amplitude(ig)
PIDFIT.amplitude(res.x)
plt.plot(np.arange(PIDFIT.v1.shape[0])*dt,PIDFIT.v1)

