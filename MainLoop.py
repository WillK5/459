import RPi.GPIO as GPIO
import time
import serial
import motor
import sensors
import states



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initializing motor and sensors

Motor = motor.motor()
Sensors = sensors.sensors()

# Printing calibrated distance (steps)
print(Motor.totaldist)

Motor.enable()
time.sleep(2)
Motor.setPosition(0)

while True:
    Sensors.update()
    states.get()
    Motor.run()