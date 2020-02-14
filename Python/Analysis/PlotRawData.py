import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import xlim, ylim
plt.ion()

v1 = np.loadtxt('T-Bot_Raw_Data.dat')

plt.figure(figsize=(10, 8))
xdata = np.arange(v1.shape[0])
ax = plt.subplot(111)
plt.title('Raw Data From T-Bot')
ax.plot(xdata, v1[:,0], c=(255/255.,0/255.,0/255.),label = 'Column 1')
ax.plot(xdata, v1[:,1], c=(0/255.,255/255.,0/255.),label = 'Column 2')
ax.plot(xdata, v1[:,2], c=(0/255.,0/255.,255/255.),label = 'Column 3')
ax.plot(xdata, v1[:,3], c=(100/255.,100/255.,100/255.),label = 'Column 4')


plt.xlabel('Data Point')
plt.ylabel('Arb. Units')
plt.xlim([xdata.min(),xdata.max()])
ax.legend(loc = 'best',prop={ 'size': 8})
plt.grid()
plt.show()
plt.savefig('RawData.svg')

