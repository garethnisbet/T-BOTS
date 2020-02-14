import numpy as np
from time import sleep
import serial

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
    ser = serial.Serial('/dev/ttyUSB0', 38400)
except:
    print('Trying ttyUSB1')
    ser = serial.Serial('/dev/ttyUSB1', 38400)
ii=1
sleep(2)
t=0
def serial2v():
    v1=ser.readline().decode('utf-8')
    a=np.array(list(map(float,v1.split('\t')[:-1])))
    return a
v1=np.array([[]]*4).T # expecting 5 columns 
for ii in range(200):
    try:
        v1 = np.vstack([v1,serial2v()])       
    except:
        v1 = np.vstack([v1,serial2v()])
    print(serial2v())


np.savetxt('T-Bot_Raw_Data.dat',v1)


