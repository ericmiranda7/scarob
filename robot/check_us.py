import RPi.GPIO as GPIO
from robot.motor import *
import time

LEFT_TRIG = 15
LEFT_ECHO = 3
RIGHT_TRIG = 14
RIGHT_ECHO = 2


GPIO.setup(LEFT_TRIG, GPIO.OUT)
GPIO.setup(LEFT_ECHO, GPIO.IN)
GPIO.setup(RIGHT_TRIG, GPIO.OUT)
GPIO.setup(RIGHT_ECHO, GPIO.IN)

#calibrate
GPIO.output(LEFT_TRIG, False)
GPIO.output(RIGHT_TRIG, False)
time.sleep(0.5)

def get_distance(trigger, echo):
    counter = 0
    has_failed = False

    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    while GPIO.input(echo) == 0:
        counter += 1
        if counter == 5000:
            has_failed = True
            break
        pulse_start = time.time()

    if has_failed:
        return False

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration / 2) * 34300
    distance = round(distance, 1)
    return distance

def is_unsafe():
    dist = get_distance(LEFT_TRIG, LEFT_ECHO)
    if not dist:
        return True
    if dist <= 30:
        return 'r'
    dist = get_distance(RIGHT_TRIG, RIGHT_ECHO)
    if dist <= 30:
        return 'l'

    return False

def move_safely():
    while is_unsafe() != False:
        if is_unsafe() == 'r':
            left()
            time.sleep(0.2)
        elif is_unsafe() == 'l':
            right()
            time.sleep(0.2)
    forward(35)
    time.sleep(0.1)






    dist = get_distance(LEFT_TRIG, LEFT_ECHO)
    if dist <= 30:
        right()
        time.sleep(0.2)
    else:
        forward(40)
        time.sleep(0.05)
    dist = get_distance(RIGHT_TRIG, RIGHT_ECHO)
    if dist <= 30:
        left()
        time.sleep(0.2)
    else:
        forward(40)
        time.sleep(0.05)