import RPi.GPIO as GPIO
import time
import math

class motor:

    step_pin = 2  # Step input
    dir_pin = 3  # Direction input
    en_pin = 4  # Enable input

    openswitch = 17  # Input pin for switch
    closeswitch = 27
    lightgrid = 19

    speedHi = 200  # mm/s
    speedLo = 80  # mm/s
    microSteps = 2
    stepsPermm = (360 / 105) * (microSteps / 1.8)

    pulseLength = 0.0000001

    def __init__(self):

        self.enabled = False  #

        self.direction = 0  # 0 for closing, 1 for opening
        self.position = 99  # Position unknown,
        self.endposition = 99
        self.slowposition = 0

        self.totaldist = 0  # Distance unknown
        self.speed = 0  # The desired speed for the motor in mm/s
        self.time = time.clock()
        self.rampTime = 0
        self.minSpeed = 20
        self.maxSpeed = 500
        self.slopeup = 500  # mm/s^2
        self.slopedown = 500  # mm/s^2

        # Initializing Pins

        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)

        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.output(self.dir_pin, GPIO.LOW)

        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.output(self.en_pin, GPIO.LOW)

        GPIO.setup(self.openswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.closeswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.lightgrid, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Move the motor linearly to one limit, back off

        self.direction = 0  # opening door
        self.enable()

        pulps = self.speedLo * (360 / 105) * (self.microSteps / 1.8)
        period = 1 / pulps  # Period in seconds
        timebetween = period - self.pulseLength

        # while True:
        #     sw_st1 = GPIO.input(self.openswitch)
        #     sw_st2 = GPIO.input(self.closeswitch)
        #
        #     if sw_st1 == 0:
        #         print('open switch pressed')
        #         time.sleep(0.3)
        #
        #     if sw_st2 == 0:
        #         print('close switch pressed')
        #         time.sleep(0.3)

        while (GPIO.input(self.closeswitch)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.pulseLength)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(timebetween)
        print("Limit found")

        self.disable()
        self.enable()

        time.sleep(2)

        self.direction = 1  # opening door
        GPIO.output(self.dir_pin, GPIO.HIGH)

        stepnumber = 0

        while (GPIO.input(self.openswitch)):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.pulseLength)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(timebetween)
            stepnumber += 1
        print("Limit found")
        print("Calibration finished")

        self.position = stepnumber
        self.endposition = stepnumber

        self.totaldist = stepnumber

        self.stop_dist = self.speedHi^2 / (2 * self.slopedown)

        self.disable()
        self.direction = 0
        GPIO.output(self.dir_pin, GPIO.LOW)

        self.time = time.clock()

    def step(self):
        if not(GPIO.input(self.closeswitch)) and self.direction == 0:
            return
        elif not(GPIO.input(self.openswitch)) and self.direction == 1:
            return

        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(self.pulseLength)
        GPIO.output(self.step_pin, GPIO.LOW)

        self.time = time.clock()

        if self.direction == 1:  # opening door, position increasing
            self.position += 1
        elif self.direction == 0:  # closing door, position decreasing
            self.position -= 1

    def run(self):

        # Check in position is at target position

        if self.speed != 0:
            pulps = abs(self.speed) * (360 / 105) * (self.microSteps / 1.8)
            period = 1 / (pulps)  # Period in seconds
            timebetween = period - self.pulseLength

        else:
            timebetween = float('inf')

        diff = time.clock() - self.time

        if diff > timebetween:
            self.step()

        self.setspeed()

    def setspeed(self):
        # Update the time for calculating acceleration
        newTime = time.clock()
        deltaT = newTime - self.rampTime
        self.rampTime = newTime

        # Setting speed based on position
        if self.direction == 0: #closing
            if self.position > self.slowposition:
                self.speed = self.speed + self.slopeup * deltaT
                if self.speed < -self.maxSpeed:
                    self.speed = -self.maxSpeed
            elif self.position > self.endposition:
                self.speed = self.speed + self.slopedown * deltaT
                if self.speed > -self.minSpeed:
                    self.speed = -self.minSpeed
            else: # At or past the target
                self.speed = 0

        else: #opening
            if self.position < self.slowposition:
                self.speed = self.speed + self.slopeup * deltaT
                if self.speed > self.maxSpeed:
                    self.speed = self.maxSpeed
            elif self.position < self.endposition:
                self.speed = self.speed + self.slopedown * deltaT
                if self.speed < self.minSpeed:
                    self.speed = self.minSpeed
            else: # At or past the target
                self.speed = 0
        # if self.position < self.endposition:
        #
        #     self.speed = self.speed + self.speedLo *
        #     # self.speed = 2*self.speedLo*abs(math.sin(time.clock()))
        # elif self.position > self.endposition:
        #     # self.speed = -2 * self.speedLo*abs(math.sin(time.clock()))
        # elif self.position == self.endposition:
        #     # self.speed = 0

        # Updating the direction of travel in gpio and direction variable

        if self.speed < 0 and self.direction == 1:
            self.direction = 0
            GPIO.output(self.dir_pin, GPIO.LOW)
        elif self.speed > 0 and self.direction == 0:
            self.direction = 1
            GPIO.output(self.dir_pin, GPIO.HIGH)

        # if self.position <= (self.totaldist / 2):
        #     self.speed = self.slopeup * self.position
        #
        # elif self.position > (self.totaldist / 2):
        #     self.speed = (self.slopedown * self.position) + (2 * self.speedHi)

        # Purpose: set the next desired speed based on the current position in steps

    def enable(self):
        GPIO.output(self.en_pin, GPIO.HIGH)
        self.enabled = True

    def disable(self):
        GPIO.output(self.en_pin, GPIO.LOW)
        self.enabled = False

    def setPosition(self, position):
        # Set the sign of the acceleration correctly
        if position < self.position: # closing, acceleration should be negative and deceleration should be positive
            self.slopeup = -abs(self.slopeup)
            self.slopedown = abs(self.slopedown)
        else: # Opening, acceleration positive and deceleration negative
            self.slopeup = abs(self.slopeup)
            self.slopedown = -abs(self.slopedown)

        self.endposition = position
        self.slowposition = self.endposition + self.maxSpeed**2/(2*self.slopedown) * self.stepsPermm
        self.rampTime = time.clock()