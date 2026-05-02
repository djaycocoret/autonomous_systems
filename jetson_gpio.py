from time import sleep

import Jetson.GPIO as GPIO


def init_gpio():
    if GPIO.getmode() is None:
        GPIO.setmode(GPIO.BOARD)


def clean_up():
    GPIO.cleanup()


class DigitalOutputDevice:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)


class PWMOutputDevice:
    def __init__(self, pin):
        self.pin = pin
        self.frequency = 1000

        GPIO.setup(self.pin, GPIO.OUT)

        self.motor = GPIO.PWM(self.pin, self.frequency)

        self.motor.start(0)

    def change_value(self, precentage):
        self.motor.ChangeDutyCycle(precentage)


if __name__ == "__main__":
    try:
        print("hello")

        init_gpio()

        forward_pin = DigitalOutputDevice(33)
        backward_pin = DigitalOutputDevice(31)
        PWM_pin = DigitalOutputDevice(15)

        PWM_pin.on()

        forward_pin.on()
        sleep(100)
        # PWM_pin = PWMOutputDevice(15)

    finally:
        clean_up()
