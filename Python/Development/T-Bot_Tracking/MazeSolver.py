import cv2
import numpy as np


img = cv2.imread('maze2.png')
# Binary conversion
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

# Contours
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
#contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(thresh, contours, 0, (255, 255, 255), -1)

ret, thresh = cv2.threshold(thresh, 240, 255, cv2.THRESH_BINARY)

# Dilate
kernel = np.ones((25, 25), np.uint8)
dilation = cv2.dilate(thresh, kernel, iterations=1)

# Erosion
erosion = cv2.erode(dilation, kernel, iterations=1)

diff = cv2.absdiff(dilation, erosion)

# splitting the channels of maze
b, g, r = cv2.split(img)
mask_inv = cv2.bitwise_not(diff)

# masking out the green and red colour from the solved path
r = cv2.bitwise_and(r, r, mask=mask_inv)
g = cv2.bitwise_and(g, g, mask=mask_inv)

res = cv2.merge((b, g, r))
#cv2.imshow('dilation', dilation)
#cv2.imshow('erosion', erosion)
#cv2.imshow('diff', diff)
cv2.imshow('Solved Maze', res)
#cv2.imshow('thresh', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
