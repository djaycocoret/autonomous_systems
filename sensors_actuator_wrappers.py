from random import randint

from gpiozero import DigitalOutputDevice, DistanceSensor, PWMOutputDevice

from helper_functions import check_speed, play_wav


class Audio_processing:
    """A class representing the audio making module of the robot

    Attributes
    __________
    barks : List[str]
        A list containing the path at which the various audio samples of barks reside
    growl : List[str]
        A list containing the path at which the various audio samples of barks reside"""

    def __init__(self, bark, growl):
        """Initialses the Audio_processing class

        Parameters
        __________
        bark : List(str)
            A list containing one or several paths of a bark audio sample in wav format
        growl : List(str)
            A list containing one or several paths of a growl audio sample in wav format
        """
        self.bark_ = list()
        self.bark_.extend(bark)

        self.growl_ = list()
        self.growl_.extend(growl)

    def bark(self):
        """Plays a random bark audio sample"""
        max = len(self.bark_)
        index = randint(0, max - 1)
        path = self.bark_[index]
        play_wav(path)

    def growl(self):
        """ "Plats a random growl audio sample"""
        max = len(self.growl_)
        index = randint(0, max - 1)
        path = self.growl_[index]
        play_wav(path)


class Distance_sensor:
    def __init__(self, trigger_pin, echo_pin):
        self.sensor = DistanceSensor(trigger_pin, echo_pin)

    def safe_distance(self, safe_distance: float):
        return self.sensor.distance > safe_distance


class Motor:
    """A class representing a motor

    Attributes
    __________
    PWM : PWMOutputDevice
        The pin number connected to the Pulse Width Modulation connection on the L293D chip.
        This pin changes the speed of the motor.
    forward_pin : DigitalOutputDevice
        The pin number connected to the forward connection on the L293D chip
    backward_pin : DigitalOutputDevice
        The pin number connected to the backward connection on the L293D chip
    """

    def __init__(self, forward_pin, backward_pin, pwm_pin):
        """Initialise the motor class

        Parameters
        __________
        pwm_pin : int
            The pin connected to the Pulse Width Modulation connection on the L293D chip.
            This pin changes the speed of the motor.
        forward_pin : int
            The pin connected to the forward connection on the L293D chip
        backward_pin : int
            The pin connected to the backward connection on the L293D chip
        """
        self.PWM = PWMOutputDevice(pwm_pin)
        self.forward_pin = DigitalOutputDevice(forward_pin)
        self.backward_pin = DigitalOutputDevice(backward_pin)

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
