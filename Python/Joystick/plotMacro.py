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
        dt = float(data[0])
        data = data[1].split('\n')[0]
        X = (int(data[:3])-200)*s1
        Y = (int(data[3:-1])-200)*s2
        w1 = (-X/2.+(Y))*dt
        w2 = (X/2.+(Y))*dt
        w_average = (w1+w2)/2.0
        if w_average == 0:
            w_average = 0.0001
        if (w1-w2) != 0:
            angle = 2.0*(w1-w2)/73.E-3
        else:
            angle = 0
        vo = vo/np.linalg.norm(vo)
        v = np.array(rotxy(angle,vo*w_average))
        vo = v
        v1 = np.vstack((v1,v))
    return v1



s1,s2 = 0.00268,3.5
  
v2 = vbuilder(s1,s2,cmd_data)
xdata = np.cumsum(v2[:,0])
ydata = np.cumsum(v2[:,1])




fig, ax = plt.subplots(figsize=(5, 6))
p, = plt.plot(xdata,ydata)
plt.plot(xdata[0],ydata[0],'o')
p2, = plt.plot(xdata[-1],ydata[-1],'o')
plt.title('T-Bot Macro Plotter')
plt.xlabel('Displacement (mm)')
plt.ylabel('Displacement (mm)')

fig.subplots_adjust(bottom=0.23)
fig.subplots_adjust(left=0.165)
fig.subplots_adjust(right=0.94)

if xdata.min() < ydata.min():
    minval = xdata.min()
else:
    minval = ydata.min()
    
if xdata.max() > ydata.max():
    maxval = xdata.max()
else:
    maxval = ydata.max()
ax.set_xlim(minval,maxval)
ax.set_ylim(minval,maxval)

spacing = np.linspace(0.08,0.04,2)
thickness = 0.02

ax_a = plt.axes([0.3,spacing[0], 0.5, thickness], facecolor='white')
ax_b = plt.axes([0.3, spacing[1], 0.5, thickness], facecolor='white')

sldr_a = plt.Slider(ax_a, 'Rotation Rate', s1-0.01, s1+0.01,valinit=s1,valfmt = '%0.5f',color='gray')
sldr_b = plt.Slider(ax_b, 'Speed Factor', s2-2, s2+2,valinit=s2,valfmt = '%0.5f',color='gray')

def update(val):
        s1 = sldr_a.val
        s2 = sldr_b.val
        v2 = vbuilder(s1,s2,cmd_data)
        xdata = np.cumsum(v2[:,0])
        ydata = np.cumsum(v2[:,1])
        p.set_data(xdata,ydata)
        p2.set_data(xdata[-1],ydata[-1])
        if xdata.min() < ydata.min():
            minval = xdata.min()
        else:
            minval = ydata.min()
        if xdata.max() > ydata.max():
            maxval = xdata.max()
        else:
            maxval = ydata.max()
        ax.set_xlim(minval,maxval)
        ax.set_ylim(minval,maxval)

     
sldr_a.on_changed(update)
sldr_b.on_changed(update)


plt.ion()
plt.show()
