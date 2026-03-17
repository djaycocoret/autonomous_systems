from time import sleep

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class Wheel:
    def __init__(self, forward_pin, backward_pin, PWM):
        self.PWM = PWM
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin

    def __repr__(self):
        return f"Wheel object"

    def forward(self, speed=1):
        self.PWM.value = speed
        self.backward_pin.off()
        self.forward_pin.on()

    def stop(self):
        self.backward_pin.off()
        self.forward_pin.off()

    def backward(self, speed=1):
        self.PWM.value = speed
        self.forward_pin.off()
        self.backward_pin.on()


class Robot:
    def __init__(self, left_wheel, right_wheel):
        self.left_wheel = left_wheel
        self.right_wheel = right_wheel

    def return_wheels(self) -> list[Wheel]:
        return [self.left_wheel, self.right_wheel]

    def forward(self):
        for wheel in self.return_wheels():
            wheel.forward()

    def stop(self):
        for wheel in self.return_wheels():
            wheel.stop()

    def backward(self):
        for wheel in self.return_wheels():
            wheel.backward()

    def slow_down(self, max=100, min=50):
        for i in range(max, min, -1):
            print(i / 100)
            for wheel in self.return_wheels():
                wheel.forward(speed=i / 100)
            sleep(0.5)

    def speed_up(self, max=100, min=50):
        for i in range(min, max, 1):
            print(i / 100)
            for wheel in self.return_wheels():
                wheel.forward(speed=i / 100)
            sleep(0.5)

    def turn_left(self, speed=1, duration=0.5):
        self.left_wheel.forward()
        self.right_wheel.stop()
        sleep(duration)
        self.stop()

    def spin(self, direction, duration=0.5):
        if direction.upper() == "L":
            self.left_wheel.forward()
            self.right_wheel.backward()
            sleep(duration)
            self.stop()
        elif direction.upper() == "R":
            self.right_wheel.forward()
            self.left_wheel.backward()
            print("spinning")
            sleep(duration)
            self.stop()
        else:
            raise ValueError("Direction must be either left or right")


forward_pin = DigitalOutputDevice(17)
backward_pin = DigitalOutputDevice(27)
PWM_pin = PWMOutputDevice(12)

forward_pin_2 = DigitalOutputDevice(23)
backward_pin_2 = DigitalOutputDevice(24)
PWM_pin_2 = PWMOutputDevice(13)

delay_time = 2.0  # seconds


right_wheel = Wheel(forward_pin, backward_pin, PWM_pin)
left_wheel = Wheel(forward_pin_2, backward_pin_2, PWM_pin_2)

angry_dog = Robot(left_wheel, right_wheel)


try:
    while True:
        angry_dog.turn_left(duration=2)

    while False:
        angry_dog.stop()
        print("Stop")
        sleep(delay_time)

        angry_dog.forward()
        print("Forward")
        sleep(delay_time)

        angry_dog.stop()
        print("Stop")
        sleep(delay_time)

        angry_dog.backward()
        print("Backward")
        sleep(delay_time)

except KeyboardInterrupt:
    angry_dog.stop()
