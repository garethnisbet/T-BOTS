#!/usr/bin/env python

import cv2
from pyzbar import pyzbar


range_filter = 'HSV'
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
done = 0

while not done:
    success, frame = camera.read()
    cv2.imshow("Preview", frame)
    barcodes = pyzbar.decode(frame)

    if barcodes != []:
        for barcode in barcodes:
            print(barcodes)
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            print(barcodeType)
    if cv2.waitKey(1) & 0xFF is ord('q'):
        done = 1
camera.release()
cv2.destroyAllWindows()


