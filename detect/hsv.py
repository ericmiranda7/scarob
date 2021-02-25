from robot.motor import *
from robot.check_us import move_safely
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
from time import sleep

camera = PiCamera()
image_width = 640
image_height = 480
camera.resolution = (image_width, image_height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(image_width, image_height))
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 250
maximum_area = 100000

forward_speed = 100
turn_speed = 55

HUE_VAL = 65

#lower_color = np.array([HUE_VAL-10, 100, 100])
#upper_color = np.array([HUE_VAL+10, 255, 255])

lower_color = np.array([76, 135, 49])
upper_color = np.array([103, 255, 255])


def start_tracking():
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        color_mask = cv2.inRange(hsv, lower_color, upper_color)

        contours, hierarchy = cv2.findContours(
            color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        object_area = 0
        object_x = 0
        object_y = 0

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            found_area = width * height
            center_x = x + (width / 2)
            center_y = y + (height / 2)
            if object_area < found_area:
                object_area = found_area
                object_x = center_x
                object_y = center_y
                cv2.rectangle(image, (x,y), (x+width,y+height), (0,255,0), 2)
                cv2.putText(image, 'Object detected', (x+width+10, y+height), 0, 0.3,(0,255,0))
        if object_area > 0:
            ball_location = [object_area, object_x, object_y]
        else:
            ball_location = None

        main_contour = None
        if ball_location:
            if (ball_location[0] > minimum_area) and (ball_location[0] < maximum_area):
                if ball_location[1] > (center_image_x + (image_width/3)):
                    move_safely()
                    right(turn_speed)
                    print("Turning right")
                elif ball_location[1] < (center_image_x - (image_width/3)):
                    move_safely()
                    left(turn_speed)
                    print("Turning left")
                else:
                    move_safely()
                    forward(forward_speed)
                    sleep(0.2)
                    print("Forward")
            elif (ball_location[0] < minimum_area):
                move_safely()
                left(turn_speed)
                print("Target isn't large enough, searching left")
            else:
                stopMotor()
                print("Target large enough, stopping")
        else:
            left(turn_speed)

        cv2.imshow("feed", image)
        rawCapture.truncate(0)
        k = cv2.waitKey(5) #& 0xFF
        if "q" == chr(k & 255):
            break
