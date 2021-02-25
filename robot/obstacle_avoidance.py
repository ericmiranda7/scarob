import RPi.GPIO as GPIO
from motor import *
import time

TRIG = 18
ECHO = 4

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

#calibrate
GPIO.output(TRIG, False)
time.sleep(0.2)

def get_distance(trigger, echo):
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration / 2) * 34300
    distance = round(distance, 1)
    print("distance: ", distance)
    return distance

while True:
    dist = get_distance(TRIG, ECHO)
    if dist <= 40:
        right()
        time.sleep(0.2)
    else:
        forward(50)
        time.sleep(0.05)
