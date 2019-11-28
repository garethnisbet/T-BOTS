import sys
import os
import cv2
import numpy as np
from time import sleep
from time import time
from pyzbar import pyzbar
#########################################################
#-------        Grab frames from webcam      -----------#
#########################################################


sleeptime = 0.001
numframes = 10*30
folder = '3D'
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
def QR_read(image):
    for barcode in barcodes:
	    # extract the bounding box location of the barcode and draw the
	    # bounding box surrounding the barcode on the image
	    (x, y, w, h) = barcode.rect
	    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
     
	    # the barcode data is a bytes object so if we want to draw it on
	    # our output image we need to convert it to a string first
	    barcodeData = barcode.data.decode("utf-8")
	    barcodeType = barcode.type
     
	    # draw the barcode data and barcode type on the image
	    text = "{} ({})".format(barcodeData, barcodeType)
	    cv2.putText(image, text, (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX,
		    0.5, (0, 255, 0), 2)
     
	    # print the barcode type and data to the terminal
	    print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))


iii = 0
oldtime = time()
if __name__ == '__main__':
    success, frame = cap.read()
    if not success:
        print('Failed to capture video')
        sys.exit(1)
    while cap.isOpened():      
        success, frame = cap.read()
        if not success:
            break
        barcodes = pyzbar.decode(frame)
        QR_read(frame)
        cv2.imshow('Frames', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

cap.release()
#out.release()
cv2.destroyAllWindows()



