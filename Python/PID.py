import numpy as np
import matplotlib.pyplot as plt
plt.ion()


##################   Functions  #########################

def integrate(setpoint, Ki, ydata, dt):
    integ = np.cumsum(Ki*(setpoint-ydata)*dt)
    return integ

def derivative(setpoint, Kd, ydata, dt):
    deriv = Kd*((setpoint-ydata[:-1])-(setpoint-ydata[1:]))/dt
    return deriv


###############   Create data  ########################

xdata = np.linspace(0,360*3.25,360)
noise = (1+((np.random.rand(xdata.shape[0])-0.5)*0.1))
ydata = ((np.cos(xdata*np.pi/180))*(xdata))*noise
#ydata = np.cos(xdata*np.pi/180)
setpoint = 0
Kp, Ki, Kd = 0.5,0.01,10
dt = xdata[1] - xdata[0]
py = Kp*(setpoint - ydata)
iiy = (setpoint - ydata)
iy = integrate(setpoint, Ki, ydata, dt)
dy = derivative(setpoint, Kd, ydata, dt)
#upid = py[2:]+iy[2:]+dy[1:]
#upi = py[2:]+iy[2:]

###############   Plot data    ########################

plt.figure(figsize=(10, 4))

plt.title('PID')
plt.plot(xdata, ydata, c=(91/255.,111/255.,189/255.), label = 'Signal')
plt.plot(xdata, py, c=(56/255.,192/255.,255/255.),label = 'Proportional Kp = '+str(Kp))
plt.fill_between(xdata, 0, iiy,facecolor=(191/255.,211/255.,255/255.),edgecolor=(191/255.,211/255.,255/255.), alpha = 0.6,label = 'Error')

plt.plot(xdata, iy, c=(255/255.,0/255.,0/255.),label = 'Integral Ki = '+str(Ki))
plt.plot(xdata[2:], dy[1:], c=(255/255.,150/255.,0/255.),label = 'Derivitave Kd = '+str(Kd))
#plt.plot(xdata[2:], upid, 'g',label = 'u PID')
#plt.plot(xdata[2:], upi, 'b',label = 'u PI')
plt.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('t (s)')
plt.ylabel('Deviation (Arb. Units)')
plt.axis('tight')
plt.subplots_adjust(bottom=0.15)
plt.savefig('PID.svg')

