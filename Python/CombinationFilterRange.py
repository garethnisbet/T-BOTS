import numpy as np
import matplotlib.pyplot as plt
from matplotlib import interactive
interactive(True)


v1 = np.loadtxt('T-Bot_FilteredData.dat')
v1[np.where(v1[:,0]<0.001),0]=0.013



################   Simple Combination Filter    ################
'''
This code serves as a guide to show how the filters work. 
A filter_weighting of 0 zero will be equivalent to using
the gyro only. A value of 1 will be equivalent to using the accelerometer  
only. You can use serial_GetData.py to collect the data from the T-BOT
to see how effective your filter is.
'''

angle = 0
filter_weighting = 0.04

def getAngleCFilter(pitch, gyro_rate, dt, filter_weighting):
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
Q_angle = 0.1 # process noise 
Q_bias = 0.3 # 
R_measure = 1 # measurement noise
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


gyroangle = np.cumsum(v1[:,2]*v1[:,0])

angle = 0

t = np.cumsum(v1[:,0])

###############   Plot the data  ########################

plt.figure(figsize=(12, 6))

plt.title('Filter Weightings')
plt.plot(t, v1[:,1], '.', c=(91/255.,111/255.,18/255.),label = 'Measured Pitch')
plt.plot(t, gyroangle, '.' ,c=(56/255.,19/255.,255/255.),label = 'Unfiltered Gyro Angle')
for filter_weighting in np.arange(1,0-0.1,-0.1):
    angle = 0
    angleCF = np.array([getAngleCFilter(v1[x,1],v1[x,2],v1[x,0],filter_weighting**3) for x in range(v1.shape[0])])
    plt.plot(t, angleCF,label = 'fw = '+'{:.4f}'.format(filter_weighting**3),linewidth=1)

plt.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle (deg)')
plt.axis('tight')
plt.subplots_adjust(hspace=0.3)


