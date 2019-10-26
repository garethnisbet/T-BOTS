import sys
import cv2
import PID
from random import randint
import matplotlib.pyplot as plt
plt.ion()
import numpy as np
from time import sleep

       


#########  Get image and set coordinates  ##################

tracker = cv2.TrackerCSRT_create()
cap = cv2.VideoCapture(0)
sleep(0.2)

############   Start main loop #############################

if __name__ == '__main__':

    # Read first frame to select ROI
    success, frame = cap.read()
    success, frame = cap.read()
    # quit if unable to read the from camera
    if not success:
        print('Failed to capture video')
        sys.exit(1)

    ## Select boxes
    bboxes = []
    colors = [] 

    # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
    # So we will call this function in a loop till we are done selecting all objects

    while True:
        # draw bounding boxes over objects
        # selectROI's default behaviour is to draw box starting from the center
        # when fromCenter is set to false, you can draw box starting from top left corner
        bbox = cv2.selectROI('MultiTracker', frame)
        bboxes.append(bbox)
        #colors.append((randint(64, 255), randint(64, 255), randint(64, 255)))
        colors.append((0,0,0))
        print("Press q to quit selecting boxes and start tracking")
        print("Press any other key to select next object")
        k = cv2.waitKey(0) & 0xFF
        if (k == 113):    # q is pressed
            break
    
    print('Selected bounding boxes {}'.format(bboxes))

    ## Initialize MultiTracker
    multiTracker = cv2.MultiTracker_create()

    for bbox in bboxes:
        multiTracker.add(tracker, frame, bbox)


    # Process video stream and track objects
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # get updated location of objects in subsequent frames
        success, boxes = multiTracker.update(frame)

        # draw tracked objects
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)

            #extract coordinates from tracker
            v0 = [(p1[0]+p2[0])/2.0,(p1[1]+p2[1])/2.0]

        # show frame
        cv2.imshow('MultiTracker', frame)

        #extract coordinates from tracker 
        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:    # Esc pressed
            
            break

