import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
L_Forward=27
L_Backward=22
R_Backward=23
R_Forward=24
ENA=13
ENB=12

GPIO.setup(L_Forward, GPIO.OUT)
GPIO.setup(L_Backward, GPIO.OUT)
GPIO.setup(R_Forward, GPIO.OUT)
GPIO.setup(R_Backward, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

GPIO.output(ENA, 1)
GPIO.output(ENB, 1)

pwmL=GPIO.PWM(ENA,1000)
pwmR=GPIO.PWM(ENB, 1000)
pwmL.start(75)
pwmR.start(75)

def stopMotor():
    GPIO.output(L_Backward,False)
    GPIO.output(R_Backward,False)
    GPIO.output(L_Forward,False)
    GPIO.output(R_Forward,False)

stopMotor()

def left(ts=75):
    pwmR.ChangeDutyCycle(ts)
    pwmL.ChangeDutyCycle(ts)
    GPIO.output(R_Forward, True)
    GPIO.output(R_Backward,False)
    GPIO.output(L_Backward,True)
    GPIO.output(L_Forward, False)


def right(ts=75):
    pwmL.ChangeDutyCycle(ts)
    pwmR.ChangeDutyCycle(ts)
    GPIO.output(L_Forward, True)
    GPIO.output(R_Forward, False)
    GPIO.output(R_Backward, True)
    GPIO.output(L_Backward, False)


def forward(fs=100):
    pwmR.ChangeDutyCycle(fs)
    pwmL.ChangeDutyCycle(fs)
    GPIO.output(L_Forward,True)
    GPIO.output(R_Forward,True)

def backward(fs=100):
    pwmR.ChangeDutyCycle(fs)
    pwmL.ChangeDutyCycle(fs)
    GPIO.output(L_Backward,True)
    GPIO.output(R_Backward,True)

