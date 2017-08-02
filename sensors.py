import RPi.GPIO as GPIO

class sensors:

    openswitch = 27  # Input pin for switch
    closeswitch = 17
    lightgrid = 19

    def __init__(self):

        GPIO.setup(self.openswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.closeswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.lightgrid, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.openswstate = GPIO.input(self.openswitch)
        self.closeswstate = GPIO.input(self.closeswitch)
        self.lightgridstate = GPIO.input(self.lightgrid)

    def update(self):

        self.openswstate = GPIO.input(self.openswitch)
        self.closeswstate = GPIO.input(self.closeswitch)
        self.lightgridstate = GPIO.input(self.lightgrid)