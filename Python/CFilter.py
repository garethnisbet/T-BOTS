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
'''

angle = 0
filter_weighting = 0.04

def getAngleCFilter(pitch, gyro_rate, dt):
    global angle
    angle += gyro_rate * dt
    angle += filter_weighting * (pitch - angle)
    return angle



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

angleCF = np.array([getAngleCFilter(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

gyroangle = np.cumsum(v1[:,2]*v1[:,0])

angle = 0
angleKF = np.array([getAngle(v1[x,1],v1[x,2],v1[x,0]) for x in range(v1.shape[0])])

t = np.cumsum(v1[:,0])

###############   Plot the data  ########################

plt.figure(figsize=(10, 4))

plt.title('Kalman Filter vs Simple Combination Filter')
plt.plot(t, v1[:,1],  c=(91/255.,111/255.,189/255.),label = 'Measured Pitch')

label_datapoint = 248
plt.annotate('Noisy accelerometer\nsignal',xy=(t[label_datapoint],v1[label_datapoint,1]),xytext = (t[label_datapoint]+0.7,v1[label_datapoint,1]-20),ha='center', arrowprops = dict(facecolor=(91/255.,111/255.,189/255.),width=1,headwidth=10,shrink=0.01),)

plt.plot(t, gyroangle, c=(56/255.,192/255.,255/255.),label = 'Unfiltered Gyro Angle')
plt.annotate('Gyro integral drift',xy=(t[700],gyroangle[700]),xytext = (t[700]-3,gyroangle[700]+7), arrowprops = dict(facecolor=(56/255.,192/255.,255/255.),width=1,headwidth=7,shrink=0.01),)



plt.plot(t, angleKF, 'g',label = 'Kalman Filter',linewidth=2)
plt.plot(t, angleCF, 'r--',label = 'Combination Filter',linewidth=2)

plt.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('angle (deg)')
plt.axis('tight')
plt.subplots_adjust(bottom=0.15)
plt.show()
plt.savefig('Filter.svg')

