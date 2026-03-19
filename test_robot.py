from time import sleep

from gpiozero import DigitalOutputDevice, PWMOutputDevice


class Wheel:
    """A class representing a wheel

    Attributes
    __________
    PWM : PWMOutputDevice
        The pin connected to the Pulse Width Modulation connection on the L293D chip.
        This pin changes the speed of the wheel.
    forward_pin : DigitalOutputDevice
        The pin connected to the forward connection on the L293D chip
    backward_pin : DigitalOutputDevice
        The pin connected to the backward connection on the L293D chip
    """

    def __init__(self, forward_pin, backward_pin, PWM):
        """Initialise the Wheel class

        Parameters
        __________
        PWM : PWMOutputDevice
            The pin connected to the Pulse Width Modulation connection on the L293D chip.
            This pin changes the speed of the wheel.
        forward_pin : DigitalOutputDevice
            The pin connected to the forward connection on the L293D chip
        backward_pin : DigitalOutputDevice
            The pin connected to the backward connection on the L293D chip
        """
        self.PWM = PWM
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin

    def __repr__(self):
        return f"Wheel object: forward pin: {self.forward_pin}, backward pin: {self.backward_pin}, PWM: {self.PWM}, speed: {self.PWM.value}"

    def forward(self, speed=1):
        """Makes the wheel move in the direction such that the agent moves forward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the wheel moves
        """
        self.PWM.value = speed
        self.backward_pin.off()
        self.forward_pin.on()

    def stop(self):
        """Makes the wheel stop"""
        self.backward_pin.off()
        self.forward_pin.off()

    def backward(self, speed=1):
        """Makes the wheel move in the direction such that the agent moves backward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the wheel moves
        """
        self.PWM.value = speed
        self.forward_pin.off()
        self.backward_pin.on()


class Robot:
    """A class representing a robot for the autonomous systems course 2026

    Attributes
    __________
    left wheel : Wheel
        The left wheel of the robot, oriented with the raspberry facing forwards
    right wheel : Wheel
        The right wheel of the robot, oriented with the raspberry facing forwards

    """

    def __init__(self, left_wheel, right_wheel):
        """Initialises the robot

        Parameters
        __________
        left wheel : Wheel
            The left wheel of the robot, oriented with the raspberry facing forwards
        right wheel : Wheel
            The right wheel of the robot, oriented with the raspberry facing forwards

        TO BE CONTINUED
        """
        self.left_wheel = left_wheel
        self.right_wheel = right_wheel

    def return_wheels(self) -> list[Wheel]:
        """Return the wheels of the robot in a list"""
        return [self.left_wheel, self.right_wheel]

    def forward(self, speed=1):
        """Changes the state of the robot to going forward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the agent will go forward"""
        for wheel in self.return_wheels():
            wheel.forward(speed)

    def stop(self):
        """Changes the state of the robot to stopped"""
        for wheel in self.return_wheels():
            wheel.stop()

    def backward(self, speed=1):
        """Changes the state of the robot to going backward

        Parameters
        __________
        speed : float [0 , 1]
            The speed at which the agent will go backward"""
        for wheel in self.return_wheels():
            wheel.backward(speed)

    def slow_down(self, max=100, min=50):
        """Chances the state of the robot to slowing down.

        Parameters
        __________
        max : int [0, 100]
            The maximum speed, at which the slowing down starts.
        min : int [0, 100]
            The minimum speed, which will be achieved after having slowed down.
        """
        for i in range(max, min, -1):  # iterates from max to min with increments of 1.
            for wheel in self.return_wheels():
                wheel.forward(speed=i / 100)
            sleep(0.5)  # TODO fix this.

    def speed_up(self, max=100, min=50):
        """Chances the state of the robot to speeding up.

        Parameters
        __________
        max : int [0, 100]
            The maximum speed, which will be achieved after having sped up.
        min : int [0, 100]
            The minimum speed, at which the speeding up begins.
        """
        for i in range(min, max, 1):
            print(i / 100)
            for wheel in self.return_wheels():
                wheel.forward(speed=i / 100)
            sleep(0.5)  # TODO fix this.

    def turn_left(self, speed=1, duration=0.5):
        """Makes the robot turn left for a specified duration

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the robot will turn
        duration : float
            The duration of the turn movement in seconds
        """
        self.left_wheel.forward()
        self.right_wheel.stop()
        sleep(duration)
        self.stop()

    def spin(self, direction, duration=0.5):
        """Makes the robot spin for a specified duration

        Parameters
        __________
        direction : str ('L', 'R')
            The direction how the robot will spin
        duration : float
            The duration of the spin movement in seconds
        """
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


# ugly test code

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
