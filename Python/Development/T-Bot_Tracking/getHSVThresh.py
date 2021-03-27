#!/usr/bin/env python

import cv2
import numpy as np
# from scipy import ndimage
maskgridL = np.meshgrid(np.r_[0:359],np.r_[0:130])
maskgridR = np.meshgrid(np.r_[0:359],np.r_[639-130:639])

#       key value
# cam.set(3 , 640)  # width        
# cam.set(4 , 480)  # height       
# cam.set(10, 120)  # brightness     min: 0   , max: 255 , increment:1  
# cam.set(11, 50)   # contrast       min: 0   , max: 255 , increment:1     
# cam.set(12, 70)   # saturation     min: 0   , max: 255 , increment:1
# cam.set(13, 13)   # hue         
# cam.set(14, 50)   # gain           min: 0   , max: 127 , increment:1
# cam.set(15, -3)   # exposure       min: -7  , max: -1  , increment:1
# cam.set(17, 5000) # white_balance  min: 4000, max: 7000, increment:1
# cam.set(28, 0)    # focus          min: 0   , max: 255 , increment:5

def callback(value):
    pass

def setup_trackbars(range_filter):
    cv2.namedWindow("Thresholds",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Thresholds", 720, 720)
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Thresholds", v, 255, callback)

def get_trackbar_values(range_filter):
    values = []
    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Thresholds")
            values.append(v)
    return values


got_lowpass = 0
# range_filter = 'RGB'
range_filter = 'HSV'
cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cam.set(28, 0)
cam.set(cv2.CAP_PROP_GAIN,0)
cam.set(cv2.CAP_PROP_BRIGHTNESS,0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cam.set(cv2.CAP_PROP_BRIGHTNESS, 100)

setup_trackbars(range_filter)


while True:
    success, image = cam.read()
    # image[maskgridL] = 0
    # image[maskgridR] = 0
    if range_filter == 'RGB':
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
    thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
    preview = cv2.bitwise_and(image, image, mask=thresh)
    cv2.imshow("Thresholds", preview)

    if cv2.waitKey(1) & 0xFF is ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        break
