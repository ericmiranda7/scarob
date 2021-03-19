import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

TRIG = 18
ECHO = 4
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)

def get_distance():
    while True:
        counter = 0
        has_failed = False

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            counter += 1
            if counter == 5000:
                has_failed = True
                break
            pulse_start = time.time()

        if has_failed:
            continue
        
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration / 2) * 34300
        distance = round(distance, 1)
        print("Distance: ", distance, " cm")
        return distance