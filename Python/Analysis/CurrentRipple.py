import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
plt.ion()
dutycycle = 128./256
v1 = np.loadtxt('WaveData698.csv')[200:2000,:]
measuredI = 0.025
stalledI = 0.25
Vemf = 3.63
Hz = 31399.
Hz2 = Hz/2
dutycycle = 127./256
Vemf = Vemf*dutycycle
veff=v1[:,1]*(v1[:,1].max()-Vemf)/v1[:,1].max()
veff = veff - np.percentile(veff,90)/2
veff = veff
mean = np.percentile(v1[:,1],90)/2

R=10
L1 = 8.5E-6
L2 = 8.5E-6

I = np.cumsum(((veff)/L1)*np.gradient(v1[:,0]))/R
I2 = np.cumsum(((veff)/L2)*np.gradient(v1[:,0]*Hz/Hz2))/R

###############   Plot the data  ########################

fig, ax1 = plt.subplots(figsize=(10, 4))

plt.title('Current Ripple',color = (1,1,1))
ax1.plot(v1[:,0], v1[:,1], c=(255./255.,176./255.,0/255.), label = 'Scope Signal')
ax1.set_ylabel('Voltage (V)')
ax1.set_xlabel('t (s)')
ax1.xaxis.label.set_color('white')
ax1.tick_params(axis='x', colors='white')
ax1.yaxis.label.set_color('white')
ax1.tick_params(axis='y', colors='white')
ax1.set_axis_bgcolor((0,0,0))

ax2 = ax1.twinx()
ax2.plot(v1[:,0], I, c=(4./255.,204./255.,208/255.), label = 'PWM Frequency = '+str(Hz)+'Hz')
ax2.plot(v1[:,0], I2, c=(255./255.,16./255.,208/255.), label = 'PWM Frequency = '+str(Hz2)+'Hz')
ax2.set_ylabel('Current (A)')
ax2.legend(loc = 'best',prop={ 'size': 8})
ax2.yaxis.label.set_color('white')
ax2.tick_params(axis='y', colors='white')

plt.subplots_adjust(bottom=0.15)

plt.axis('tight')
plt.ylim([-1,1])
fig.set_facecolor((0.1, 0.1, 0.1))

plt.show()
plt.savefig('CurrentRipple.svg')

