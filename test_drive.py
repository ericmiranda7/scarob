from robot.motor import *

print("right")
left(35)
time.sleep(2)
print("forward")
forward(35)
time.sleep(2)
GPIO.cleanup()