from robot.motor import *
from detect.hsv import start_tracking
import time
import signal

try:
    signal.signal(signal.SIGINT, signal.default_int_handler)
    start_tracking()
except KeyboardInterrupt:
    print("Cancelling")
    GPIO.cleanup()