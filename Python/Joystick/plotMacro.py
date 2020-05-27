import matplotlib.pyplot as plt
import numpy as np


def rotxy(theta,v1):
    return (np.matrix([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])*v1.T).T

filename = '/home/pi/GitHub/T-BOTS/Python/Joystick/cmd.csv'
ff = open(filename)
cmd_data = ff.readlines()
def vbuilder(s1,s2,_cmd_data):
    v1 = np.array([[]]*2).T
    vo = np.array([[0,1]])
    for ii in range(len(cmd_data)):
        data = _cmd_data[ii].split(',')
        T = float(data[0])
        data = data[1].split('\n')[0]
        X = (int(data[:3])-200)*s2
        Y = (int(data[3:-1])-200)*s2
        w1 = (-X/2.+(Y))*T
        w2 = (X/2.+(Y))*T
        w_average = (w1+w2)/2.0
        if (w1-w2) != 0:
            angle = ((73.E-3*s1)/(w1-w2))*2*np.pi
        else:
            angle = 0
        v = np.array(rotxy(angle,vo))
        vo = v
        v1 = np.vstack((v1,v))
    return v1



s1,s2 = 0.148,1.027
  
v2 = vbuilder(s1,s2,cmd_data)
xdata = np.cumsum(v2[:,0])
ydata = np.cumsum(v2[:,1])




fig = plt.figure(figsize=(7, 7),dpi=130)
p, = plt.plot(xdata,ydata)
plt.xlim(-200,200)
plt.ylim(-200,200)

#spacing = np.linspace(0.32,0.05,14)
spacing = np.linspace(0.2,0.15,2)
thickness = 0.02

ax_a = plt.axes([0.4,spacing[0], 0.3, thickness], facecolor='white')
ax_b = plt.axes([0.4, spacing[1], 0.3, thickness], facecolor='white')



sldr_a = plt.Slider(ax_a, 'Rotation Rate', s1-0.5, s1+0.5,valinit=s1,valfmt = '%0.5f',color='gray')
sldr_b = plt.Slider(ax_b, 'Speed Factor', s2-0.5, s2+0.5,valinit=s2,valfmt = '%0.5f',color='gray')


def update(val):
        s1 = sldr_a.val
        s2 = sldr_b.val
        v2 = vbuilder(s1,s2,cmd_data)
        xdata = np.cumsum(v2[:,0])
        ydata = np.cumsum(v2[:,1])
        p.set_data(xdata,ydata)


        
        
sldr_a.on_changed(update)
sldr_b.on_changed(update)

        
plt.show()
