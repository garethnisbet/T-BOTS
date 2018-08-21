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
#  remove the /* and */ around the print commands in TBot.ino
#
#  /*
#  Serial.print(pingval); Serial.print("\t");
#  Serial.print(fping); Serial.print("\t");
#  Serial.print("\n");
#  */
#
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
v1=np.array([[]]*2).T # expecting 5 columns 
for ii in range(200):
    try:
        v1 = np.vstack([v1,serial2v()])
    except:
        v1 = np.vstack([v1,serial2v()])
    print(serial2v())

t = np.cumsum(v1[:,0]) # accumulate dt

##################   Plot the data  ########################

plt.figure()
plt.subplot(111)
plt.plot(t,v1[:,0], 'g',label = 'Raw')
plt.plot(t,v1[:,1], 'b',label = 'Rolling Average')

plt.legend()
#plt.xlabel('t (s)')
plt.ylabel('Angle (deg)')
plt.title('Ultrasond Signal')


np.savetxt('T-Bot_UltrasoundData.dat',v1)


