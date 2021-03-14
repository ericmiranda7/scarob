import RPi.GPIO as GPIO
from motor import *
import time

LEFT_TRIG = 15
LEFT_ECHO = 3
RIGHT_TRIG = 14
RIGHT_ECHO = 2
TOP_TRIG = 18
TOP_ECHO = 4


GPIO.setup(LEFT_TRIG, GPIO.OUT)
GPIO.setup(LEFT_ECHO, GPIO.IN)
GPIO.setup(RIGHT_TRIG, GPIO.OUT)
GPIO.setup(RIGHT_ECHO, GPIO.IN)
GPIO.setup(TOP_TRIG, GPIO.OUT)
GPIO.setup(TOP_ECHO, GPIO.IN)

#calibrate
GPIO.output(LEFT_TRIG, False)
GPIO.output(RIGHT_TRIG, False)
GPIO.output(TOP_TRIG, False)
time.sleep(1)

def get_distance(trigger, echo):
    while True:
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
            continue

        while GPIO.input(echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration / 2) * 34300
        distance = round(distance, 1)
        break
    print(trigger, " distance: ", distance)
    return distance

while True:
    """ dist = get_distance(LEFT_TRIG, LEFT_ECHO)
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
        time.sleep(0.05) """


    dist = get_distance(TOP_TRIG, TOP_ECHO)
    if (dist <= 30):
        l_dist = get_distance(LEFT_TRIG, LEFT_ECHO)
        r_dist = get_distance(RIGHT_TRIG, RIGHT_ECHO)
        if (l_dist + r_dist <= 60):
            backward(40)
            time.sleep(1.5)
        if (l_dist > r_dist):
            left()
            time.sleep(0.2)
        else:
            right()
            time.sleep(0.2)
    else:
        forward(40)
        time.sleep(0.05)
        

