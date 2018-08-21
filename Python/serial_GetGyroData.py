import numpy as np
import matplotlib.pyplot as plt
from matplotlib import interactive
interactive(True)
from time import sleep
import time
import serial
import numpy as np

########## Prepare Arduino code for data output ##################
# 
#  remove the /* and */ around the print commands in functions.ino
#
#  /*
#  Serial.print(dt); Serial.print("\t");
#  Serial.print(pitch); Serial.print("\t");
#  Serial.print(gyroYrate); Serial.print("\t");
#  Serial.print(CFilteredlAngleY); Serial.print("\t");
#  Serial.print(gyroYangle); Serial.print("\t");
#  Serial.print("\n");
#  */
#
#  Remember to put them back or the T-Bot won't be able to balance
#  because there will be too much latency
#
##################################################################

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200)
except:
    ser = serial.Serial('/dev/ttyUSB1', 115200)
ii=1
sleep(2)
t=0
def serial2v():
    v1=ser.readline()
    a=np.array(list(map(float,v1.split('\t')[:-1])))
    return a
v1=np.array([[]]*5).T # expecting 5 columns 
for ii in range(1000):
    try:
        v1 = np.vstack([v1,serial2v()])
    except:
        v1 = np.vstack([v1,serial2v()])
    print(serial2v())

t = np.cumsum(v1[:,0]) # accumulate dt

##################   Plot the data  ########################

plt.figure()
ax = plt.subplot(111)
ax.plot(t,v1[:,1], 'g',label = 'Pitch (acc)')
ax.plot(t,v1[:,2], 'b',label = 'gyrorate')
ax.plot(t,v1[:,3], 'r',label = 'Filtered Angle')
ax.legend()
#plt.xlabel('t (s)')
plt.ylabel('Angle (deg)')

############  This file will be read by CombinationFilter.py

np.savetxt('T-Bot_FilteredData.dat',v1)


