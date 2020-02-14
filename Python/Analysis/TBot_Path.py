import numpy as np
import matplotlib.pyplot as plt
plt.ion()

###############   Get data  ########################

v1 = np.loadtxt('T-Bot_UltrasoundData.dat')
xdata = range(v1.shape[0])

###############   Plot data    ########################

plt.figure(figsize=(10, 4))
plt.title('Ultrasound Data')

plt.plot(xdata,v1[:,0],'o-', c=(91/255.,111/255.,189/255.), label = 'Raw Signal')
plt.fill_between(xdata, 0, v1[:,0],facecolor=(126/255.,40/255.,255/255.),edgecolor=(191/255.,211/255.,255/255.), alpha = 0.6)

plt.plot(xdata,v1[:,1], linewidth = 2, c=(255/255.,11/255.,211/255.), label = 'Rolling Average\nIgnoring Zeros')

plt.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('Distance (cm)')
plt.axis('tight')
plt.subplots_adjust(bottom=0.15)
plt.savefig('Ultrasound.svg')

