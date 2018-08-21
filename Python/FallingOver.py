import numpy as np
import matplotlib.pyplot as plt
plt.ion()

g_earth = 9.81
g_moon = 1.62

################     Functions    ####################

def fallingtime(l,g,theta,theta2,dt):
	'''Calculates angular acceleration, angular velocity, velocity, and falling time for an inverted pendulum between two angles(in degrees) for a given length.
       \nUsage fallingtime(l,g,theta,theta2,dt)
       \nReturns angular acceleration, angular velocity, velocity, time.'''
	theta = theta*np.pi/180
	theta2 = theta2*np.pi/180
	omega = 0
	t=0
	while theta < theta2:
		alpha =  np.sin(theta)*g/l      # angular acceleration
		omega += alpha*dt               # integrate angular acceleration to get angular velocity
		theta += omega*dt               # integrate angular velocity to get angle
		t += dt                         # integrate dt to get time
	return(alpha,omega,l*omega,t)       # angular acceleration, angular velocity, velocity, time

def v(l,g,theta):
    if theta != 0:
        return np.sqrt(2*g*(l-l*np.cos(theta*np.pi/180)))*theta/np.abs(theta)
    else:
        return 0.0


def falling(l,g,theta,theta2,dt):
	'''Calculates angular acceleration, angular velocity, velocity, and falling time for an inverted pendulum between two angles(in degrees) for a given length.
       \nUsage fallingtime(l,g,theta,theta2,dt)
       \nReturns angular acceleration, angular velocity, velocity, theta, and time up to each step in an array'''
	alpha_omega_v = np.array([[]]*5).T
	theta = theta*np.pi/180
	theta2 = theta2*np.pi/180
	omega = 0
	t=0
	while theta < theta2:
		alpha =  np.sin(theta)*g/l      # angular acceleration
		omega += alpha*dt               # integrate angular acceleration to get angular velocity
		theta += omega*dt               # integrate angular velocity to get angle
		t += dt                         # integrate dt to get time
		alpha_omega_v = np.vstack((alpha_omega_v,[alpha, omega, omega*l,theta*180/np.pi,t]))                     
	return(alpha_omega_v)       # angular acceleration, angular velocity, velocity, time


def v(l,g,theta):
    if theta != 0:
        return np.sqrt(2*g*(l-l*np.cos(theta*np.pi/180)))*theta/np.abs(theta)
    else:
        return 0.0

################   Create Data   ####################
xdata = list(np.linspace(1.E-11, 50.e-7, 500))+list(np.linspace(60.E-7, 15.e-5,500))
ydata_earth = [fallingtime(0.08, g_earth,np.arcsin(x/8e-2)*180/np.pi, 90, 0.001)[3] for x in xdata]
ydata_moon = [fallingtime(0.08, g_moon,np.arcsin(x/8e-2)*180/np.pi, 90, 0.001)[3] for x in xdata]


###############     Plot data    ####################

plt.figure(figsize=(10, 4))

plt.title('Inverted Pendulum')
plt.plot(xdata, ydata_moon, c=(50/255.,50/255.,250/255.),linewidth = 2, label = 'Moon g = '+str(g_moon)+' ms^2')
plt.plot(xdata, ydata_earth,  c=(255/255.,10/255.,10/255.),linewidth = 2, label = 'Earth g = '+str(g_earth)+' ms^2')

plt.fill_between(xdata, 0, ydata_earth,facecolor=(100/255.,0/255.,0/255.),edgecolor=(191/255.,211/255.,255/255.), alpha = 0.6)
plt.fill_between(xdata, 0, ydata_moon,facecolor=(0/255.,0/255.,100/255.),edgecolor=(191/255.,211/255.,255/255.), alpha = 0.6)

plt.annotate('Atomic vibrational amplitude (10 pm)\nFalling time 2.17 s',xy=(1.E-11,2.16),xytext = (1.e-5,5), arrowprops = dict(facecolor=(0/255.,255/255.,63/255.),width=1,headwidth=7,shrink=0.01),)

plt.annotate('Width of H atom (100 pm)\nFalling time 1.96 s',xy=(1.E-10,2),xytext = (1.e-5,2.5), arrowprops = dict(facecolor='white',width=1,headwidth=7,shrink=0.01),)

plt.annotate('Average width of human hair (100 microns)\nFalling time 0.712 s',xy=(100.E-6,0.712),xytext = (60.e-6,3), arrowprops = dict(facecolor='orange',width=1,headwidth=7,shrink=0.01),)

plt.legend(loc = 'best',prop={ 'size': 8})
plt.xlabel('Initial horizontal displacement (m)')
plt.ylabel('Falling Time (s)')
#plt.axis('tight')
plt.xlim((xdata[0]-xdata[100]),(xdata[-1]+xdata[100]))
plt.subplots_adjust(bottom=0.15)
plt.savefig('Falling.svg')
#record 1.14 s 0.05e-6 m
#second best 1.11 s

