import numpy as np
from time import sleep
import serial


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
#  Remember to put them back!
#
##################################################################

try:
    ser = serial.Serial('/dev/ttyUSB0', 38400)
except:
    ser = serial.Serial('/dev/ttyUSB1', 38400)
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



np.savetxt('T-Bot_FilteredData.dat',v1)


