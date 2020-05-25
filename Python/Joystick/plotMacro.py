import matplotlib.pyplot as plt
import numpy as np


def rotxy(v1,r1,time):
    rmat = np.matrix([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

filename = '/home/gareth/GitHub/T-BOTS/Python/Joystick/cmd.csv'
ff = open(filename)
cmd_data = ff.readlines()
v1 = np.array([[]]*2).T
for ii in range(len(cmd_data)):
    data = cmd_data[ii].split(',')
    T = float(data[0])
    data = data[1].split('\n')[0]
    X = int(data[:3])-200
    Y = int(data[3:-1])-200
    w1 = (X/2.+Y)*T
    w2 = (-X/2.+Y)*T
    w_average = (w1+w2)/2.0
    if (w1-w2) != 0:
        angle = 60./(w1-w2)*2*np.pi
    else:
        angle = 0
    v = [angle, w_average]
    v1 = np.vstack((v1,v))
v2 = v1*0
v2[:,0] = v1[:,1]*np.cos(v1[:,0])
v2[:,1] = v1[:,1]*np.sin(v1[:,0])
xdata = np.cumsum(v2[:,0])
ydata = np.cumsum(v2[:,1])

plt.figure()
plt.plot(xdata,ydata,'o-')
plt.show()

    
    
