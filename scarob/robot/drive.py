from robot.motor import *
from sensors.ultrasonic_sensors import get_distance
import threading

forward_speed = 40
turn_speed = 75


def pivot_left():
    left(100)
    time.sleep(0.4)
    stopMotor()


def turn_left():
    left(100)
    time.sleep(0.1)
    stopMotor()


def pivot_right():
    right(100)
    time.sleep(0.1)
    stopMotor()


def go_forward():
    forward(80)
    time.sleep(0.5)
    stopMotor()


def drive(self):
    if self.found:
        [x, obj_width] = self.get_pts()
        object_x = x + (obj_width / 2)
        center_image_x = self.image_width / 2
        if object_x > (center_image_x + (self.image_width / 5)):
            print("right")
            r = threading.Thread(target=pivot_right)
            r.start()
        elif object_x < (center_image_x - (self.image_width / 5)):
            print("left")
            l = threading.Thread(target=turn_left)
            l.start()
        else:
            if get_distance() > 30:
                f = threading.Thread(target=go_forward)
                f.start()
                print("forward")
            else:
                print("Close enough to target")
    else:
        x = threading.Thread(target=pivot_left)
        x.start()
