import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
plt.ion()


t = np.linspace(0, 1, 2000)

sig = np.sin(2 * np.pi * t)
pwm = signal.square(2 * np.pi * 30 * t, duty=(sig + 1)/2)
pwm15 = signal.square(2 * np.pi * 30 * t, 0.15)
effectiveV15 = pwm15*0+0.15*5 
pwm85 = signal.square(2 * np.pi * 30 * t, 0.85)
effectiveV85 = pwm15*0+0.85*5

plt.figure(figsize=(10, 8))
plt.subplot(3, 1, 1)
plt.plot(t, effectiveV15,'b',label = 'Effective Voltage')
plt.plot(t, pwm15*2.5+2.5,c=(255/255.,117/255.,0/255.),label = 'Voltage')
plt.ylim(-0.2, 5.2)
plt.xlim(0, 0.5)
plt.title('15% Duty Cycle')
plt.ylabel('Voltage (V)')
plt.legend(loc = 'best',prop={ 'size': 8})

plt.subplot(3, 1, 2)
plt.plot(t, effectiveV85,'b',label = 'Effective Voltage')
plt.plot(t, pwm85*2.5+2.5,c=(255/255.,117/255.,0/255.),label = 'Voltage')
plt.ylim(-0.2, 5.2)
plt.xlim(0, 0.5)
plt.title('85% Duty Cycle')
plt.ylabel('Voltage (V)')
plt.legend(loc = 'best',prop={ 'size': 8})

plt.subplot(3, 1, 3)
plt.plot(t, sig*2.5+2.5, 'b',label = 'Effective Voltage')
plt.plot(t, pwm*2.5+2.5, c=(255/255.,117/255.,0/255.),label = 'Voltage')
plt.ylim(-0.2, 5.2)
plt.xlabel('t (s)')
plt.ylabel('Voltage (V)')
plt.title('Variable Duty Cycle')
plt.legend(loc = 'best',prop={ 'size': 8})
plt.subplots_adjust(hspace=0.35)
plt.savefig('PWM.svg')
