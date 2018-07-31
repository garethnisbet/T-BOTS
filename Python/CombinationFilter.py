import numpy as np
import matplotlib.pyplot as plt
from matplotlib import interactive
interactive(True)


v1 = np.loadtxt('T-Bot_FilteredData.dat')
v1=v1[np.where(v1[:,0]>0.001),:][0]


################   Simple Combination Filter    ################
'''
Note the integral of the gyro here differs from T-Bot because of latency;
possibly because the serial print interferes with the timing. 
This code serves as a guide to show how the filters work. 
Typically, the filter_weighting will be a factor of 10 smaller on 
the T-Bot. A filter_weighting of 0 zero will be equivalent to using
the gyro only. A value of 1 will be equivalent to using the accelerometer  
only. You can use serial_GetData.py to collect the data from the T-BOT
to see how effective your filter is.
'''

angle = 0
filter_weighting = 0.3

def getAngleCFilter(pitch, gyro_rate, dt):
    global angle
    angle += gyro_rate * dt
    angle += filter_weighting * (pitch - angle)
    return angle


################################################################




####################   Kalman Filter    ########################
''' 
Based on Arduino code written by Kristian Lauszus 2012
                 TKJ Electronics.
'''

bias = 0
R_measure = 0.15 # measurement noise
Q_angle = 1 # process noise 
Q_bias = 0.03 # 
R_measure = 0.1 # measurement noise
P = np.zeros((2,2))
K = np.zeros(2)


def getAngle(pitch, gyrorate, dt):
    global bias
    global angle
    global P
    rate = gyrorate - bias;
    angle += dt * rate;
    # Update estimation error covariance - Project the error covariance ahead
    P[0,0] += dt * (dt*P[1,1] - P[0,1] - P[1,0] + Q_angle)
    P[0,1] -= dt * P[1,1]
    P[1,0] -= dt * P[1,1]
    P[1,1] += Q_bias * dt

    # Calculate Kalman gain - Compute the Kalman gain
    S = P[0,0] + R_measure
    K[0] = P[0,0] / S
    K[1] = P[1,0] / S
    y = pitch - angle

    #Calculate angle and bias - Update estimate with measurement zk (newAngle)
    angle += K[0] * y
    bias += K[1] * y

    #Calculate estimation error covariance - Update the error covariance
    P[0,0] -= K[0] * P[0,0]
    P[0,1] -= K[0] * P[0,1]
    P[1,0] -= K[1] * P[0,0]
    P[1,1] -= K[1] * P[0,1]
    return angle


################################################################

angleCF = np.array([getAngleCFilter(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])
v1[0,2] = v1[0,4]
gyroangle = np.cumsum(v1[:,2]*v1[:,0]*3)

angle = 0
angleKF = np.array([getAngle(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

t = np.cumsum(v1[:,0])

###############   Plot the data  ########################

plt.figure(figsize=(8, 8))

ax = plt.subplot(211)
plt.title('On-board Processing')
ax.plot(t, v1[:,1], c=(91/255.,111/255.,189/255.),label = 'Measured Pitch')
ax.plot(t, v1[:,4], c=(56/255.,192/255.,255/255.),label = 'Unfiltered Gyro Angle from T-Bot')
ax.plot(t, v1[:,3], c=(255/255.,0/255.,0/255.),label = 'Filtered Angle by T-Bot')
ax.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle')
plt.axis('tight')
ax = plt.subplot(212)
plt.title('From Python Code')
ax.plot(t, v1[:,1], 'g',label = 'Measured Pitch')
ax.plot(t, gyroangle, 'k',label = 'Unfiltered Gyro Angle')
ax.plot(t, angleKF, 'b',label = 'Kalman Filter')
ax.plot(t, angleCF, 'm',label = 'Combination Filter')

ax.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle')
plt.axis('tight')
plt.subplots_adjust(hspace=0.3)


