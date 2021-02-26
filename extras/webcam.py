import cv2
import numpy as np

cam1 = cv2.VideoCapture(1)

while True:
    ret, frame = cam1.read()

    cv2.imshow('cam1', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cam1.release()
cv2.destroyAllWindows()