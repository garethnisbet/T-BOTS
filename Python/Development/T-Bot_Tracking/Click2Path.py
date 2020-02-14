
import cv2

import matplotlib.pyplot as plt
plt.ion()
import numpy as np

numpathpoints = 80
filename = 'pathpoints.dat'
dontoverwrite = 0
if dontoverwrite:
    try:
        aa = np.loadtxt(filename)
        nomapdata = 0
        print('pathpoints.dat already exists. Delete or rename the dat file and try again.')
    except:
        nomapdata = 1
else:
    nomapdata = 1

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)

success, frame = cap.read()
if nomapdata:
    plt.figure()
    plt.imshow(frame)
    aa = plt.ginput(numpathpoints,0)
    aa = map(list,np.array(aa).astype(int))
    np.savetxt(filename,aa)
    plt.close()
else:
    aa = aa.astype(int)
cap.release()

