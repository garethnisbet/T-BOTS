import cv2


def callback(value):
    pass

cv2.namedWindow("Tuning",cv2.WINDOW_NORMAL)
skp = 1
cv2.createTrackbar('s_KP', "Tuning", skp, 255, callback)
ski = 1
cv2.createTrackbar('s_KI', "Tuning", ski, 255, callback)
skd = 1
cv2.createTrackbar('s_KD', "Tuning", skd, 255, callback)

akp = 1
cv2.createTrackbar('a_KP', "Tuning", akp, 255, callback)
aki = 1
cv2.createTrackbar('a_KI', "Tuning", aki, 255, callback)
akd = 1
cv2.createTrackbar('a_KD', "Tuning", akd, 255, callback)
fw = 1
cv2.createTrackbar('FW', "Tuning", fw, 255, callback)




done = 0

while not done:
    skp = cv2.getTrackbarPos('s_KP', "Tuning")
    ski = cv2.getTrackbarPos('s_KI', "Tuning")
    skd = cv2.getTrackbarPos('s_KD', "Tuning")
    akp = cv2.getTrackbarPos('a_KP', "Tuning")
    aki = cv2.getTrackbarPos('a_KI', "Tuning")
    akd = cv2.getTrackbarPos('a_KD', "Tuning")
    fw = cv2.getTrackbarPos('FW', "Tuning")
    print('s_KP = '+str(skp)+' s_KI = '+str(ski)+' s_KD = '+str(skd))
    if cv2.waitKey(1) & 0xFF is ord('q'):
        done = 1
cv2.destroyAllWindows()
    
