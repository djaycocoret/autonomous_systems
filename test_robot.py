from time import sleep

from gpiozero import DigitalOutputDevice, PWMOutputDevice


def check_speed(speed):
    """A function that return a value between 0 and 1, which has predictable behaviour with the motor class

    Parameters
    __________

    speed : float
        The input speed

    Returns
    _______
    float
        The output speed, which is limited to a range of [0, 1]
    """

    return max(0, min(1, speed))


class Motor:
    """A class representing a motor

    Attributes
    __________
    PWM : PWMOutputDevice
        The pin connected to the Pulse Width Modulation connection on the L293D chip.
        This pin changes the speed of the motor.
    forward_pin : DigitalOutputDevice
        The pin connected to the forward connection on the L293D chip
    backward_pin : DigitalOutputDevice
        The pin connected to the backward connection on the L293D chip
    """

    def __init__(self, forward_pin, backward_pin, PWM):
        """Initialise the motor class

        Parameters
        __________
        PWM : PWMOutputDevice
            The pin connected to the Pulse Width Modulation connection on the L293D chip.
            This pin changes the speed of the motor.
        forward_pin : DigitalOutputDevice
            The pin connected to the forward connection on the L293D chip
        backward_pin : DigitalOutputDevice
            The pin connected to the backward connection on the L293D chip
        """
        self.PWM = PWM
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin

    def __repr__(self):
        return f"Motor object: forward pin: {self.forward_pin}, backward pin: {self.backward_pin}, PWM: {self.PWM}, speed: {self.PWM.value}"

    def forward(self, speed=1.0):
        """Makes the motor move in the direction such that the agent moves forward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the motor moves
        """
        self.PWM.value = check_speed(speed)
        self.backward_pin.off()
        self.forward_pin.on()

    def stop(self):
        """Makes the motor stop"""
        self.backward_pin.off()
        self.forward_pin.off()

    def backward(self, speed=1):
        """Makes the motor move in the direction such that the agent moves backward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the motor moves
        """
        self.PWM.value = check_speed(speed)
        self.forward_pin.off()
        self.backward_pin.on()


class Robot:
    """A class representing a robot for the autonomous systems course 2026

    Attributes
    __________
    left motor : Motor
        The left motor of the robot, oriented with the raspberry facing forwards
    right motor : Motor
        The right motor of the robot, oriented with the raspberry facing forwards

    """

    def __init__(self, left_motor, right_motor):
        """Initialises the robot

        Parameters
        __________
        left motor : Wheel
            The left motor of the robot, oriented with the raspberry facing forwards
        right motor : Wheel
            The right motor of the robot, oriented with the raspberry facing forwards

        TO BE CONTINUED
        """
        self.left_motor = left_motor
        self.right_motor = right_motor

    def return_motors(self) -> list[Motor]:
        """Return the wheels of the robot in a list"""
        return [self.left_motor, self.right_motor]

    def forward(self, speed=1):
        """Changes the state of the robot to going forward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the agent will go forward"""
        for motor in self.return_motors():
            motor.forward(speed)

    def stop(self):
        """Changes the state of the robot to stopped"""
        for motor in self.return_motors():
            motor.stop()

    def backward(self, speed=1):
        """Changes the state of the robot to going backward

        Parameters
        __________
        speed : float [0 , 1]
            The speed at which the agent will go backward"""
        for motor in self.return_motors():
            motor.backward(speed)

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
            for motor in self.return_motors():
                motor.forward(speed=i / 100)
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
            for wheel in self.return_motors():
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
        self.left_motor.forward()
        self.right_motor.stop()
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
            self.left_motor.forward()
            self.right_motor.backward()
            sleep(duration)
            self.stop()
        elif direction.upper() == "R":
            self.right_motor.forward()
            self.left_motor.backward()
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


right_wheel = Motor(forward_pin, backward_pin, PWM_pin)
left_wheel = Motor(forward_pin_2, backward_pin_2, PWM_pin_2)

angry_dog = Robot(left_wheel, right_wheel)

# comment


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
