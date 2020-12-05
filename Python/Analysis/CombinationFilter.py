import numpy as np
import matplotlib.pyplot as plt
plt.ion()

v1 = np.loadtxt('T-Bot_FilteredData.dat')
v1[np.where(v1[:,0]<0.001),0]=0.013

################   Simple Combination Filter    ################
'''
This code serves as a guide to show how the filters work. 
A filter_weighting of 0 zero will be equivalent to using
the gyro only. A value of 1 will be equivalent to using the accelerometer  
only. You can use serial_GetData.py to collect the data from the T-BOT
to see how effective your filter is.

This is not an efficient way of writing this in Python but the 
structure is matched to the C code on the T-Bot for illustration.  
'''

angle = 0
filter_weighting = 0.06
'''
def getAngleCFilter(pitch, gyro_rate, dt):
    global angle
    angle += gyro_rate * dt
    angle += filter_weighting * (pitch - angle)
    return angle
'''
def getAngleCFilter(pitch, gyro_rate, dt):
    global angle
    angle += filter_weighting * (pitch - (angle + gyro_rate * dt))
    return angle


class cfilter(object):
    def __init__(self,theta, angle, alpha, filter_weighting, dt):
        self.theta = theta
        self.angle = angle
        self.alpha = alpha
        self.filter_weighting = filter_weighting
        self.dt = dt
        
    def setFilterWeighting(self,filter_weighting):
        self.filter_weighting = filter_weighting
        
    def getAngleCFilter(self, theta, gyro_rate, dt):

        self.angle += self.filter_weighting * (theta - (self.angle + gyro_rate * dt))
        return self.angle


c_filter = cfilter(0,0,0,0.06,0.01)




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

angleCF1 = np.array([getAngleCFilter(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

angleCF = np.array([c_filter.getAngleCFilter(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

gyroangle = np.cumsum(v1[:,2]*v1[:,0])

angle = 0
angleKF = np.array([getAngle(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

t = np.cumsum(v1[:,0])

###############   Plot the data  ########################

plt.figure(figsize=(10, 8))

ax = plt.subplot(211)
plt.title('On-board Processing')
ax.plot(t, v1[:,1], c=(91/255.,111/255.,189/255.),label = 'Measured angle from accelerometer')
ax.plot(t, v1[:,4], c=(56/255.,192/255.,255/255.),label = 'Unfiltered Gyro Angle from T-Bot (integrated angular velocity)')
ax.plot(t, v1[:,3], c=(255/255.,0/255.,0/255.),label = 'Filtered Angle by T-Bot')
ax.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle (deg)')
plt.axis('tight')
ax = plt.subplot(212)
plt.title('From Python Code')
ax.plot(t, v1[:,1],  c=(91/255.,111/255.,189/255.),label = 'Measured angle from accelerometer')
ax.plot(t, gyroangle, c=(56/255.,192/255.,255/255.),label = 'Unfiltered Gyro Angle (integrated angular velocity)')
ax.plot(t, angleKF, 'g',label = 'Kalman Filter',linewidth=2)
ax.plot(t, angleCF1, 'r--',label = 'Combination Filter',linewidth=2)
ax.plot(t, angleCF, 'b-.',label = 'Combination Filter Class',linewidth=2)

ax.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle (deg)')
plt.axis('tight')
plt.subplots_adjust(hspace=0.3)
plt.show()
plt.savefig('Filtering.svg')

