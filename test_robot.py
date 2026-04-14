import subprocess
from random import randint
from time import sleep

import cv2
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from ultralytics import YOLO


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


def play_wav(path):
    subprocess.run(["aplay", path])


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
        max = len(self.bark_)
        index = randint(0, max - 1)
        path = self.bark_[index]
        play_wav(path)

    def growl(self):
        max = len(self.growl_)
        index = randint(0, max - 1)
        path = self.growl_[index]
        play_wav(path)


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


class Visual_processing:
    """A class representing the visual processing

    Attributes
    __________
    model : ultralytics.models.yolo.model.YOLO
        The model that will classify the images.
    """

    def __init__(self, model):
        """Initialises the visual processing class"""
        self.model = YOLO(model)
        print(type(self.model))

    def locate_cat(self, input):
        """Locates a cat, if found,

        Parameters
        __________
        input : np.array
            The captured image as a numpy array

        Returns
        _______
        offset : float [-1, 1] or None
            KKKKKKK
        """

        h_img, w_img, _ = input.shape

        results = self.model.predict(input)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                cls = result.names[cls_id]
                x, y, _, _ = box.xywh[0]
                print(f"{cls} at ({x}, {y})")
                if cls == "cat":
                    offset = float((x - w_img / 2) / w_img)
                    return offset
                else:
                    continue
        return None


class Visual_perception:
    def __init__(self):
        pass


class Robot:
    """A class representing a robot for the autonomous systems course 2026

    Attributes
    __________
    left motor : Motor
        The left motor of the robot, oriented with the raspberry facing forwards
    right motor : Motor
        The right motor of the robot, oriented with the raspberry facing forwards
    audio : Audio_processing
        The audio interface of the robot
    visual_proc : Visual_processing
        The object detection pipeline
    camera : Visual_perception
        The camera sensor of the robot
    """

    def __init__(self, left_motor, right_motor, audio):
        """Initialises the robot

        Parameters
        __________
        left motor : Wheel
            The left motor of the robot, oriented with the raspberry facing forwards
        right motor : Wheel
            The right motor of the robot, oriented with the raspberry facing forwards
        audio : Audio_processing
            The audio interface of the robot.

        TO BE CONTINUED
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.audio = audio
        self.visual_proc = Visual_processing("yolo26n.pt")

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

    def bark(self):
        """Plays a randomly selected bark sample"""
        self.audio.bark()

    def growl(self):
        """Plays a randomly selected growl sample"""
        self.audio.growl()


# ugly test code
delay_time = 2.0  # seconds

forward_pin = DigitalOutputDevice(17)
backward_pin = DigitalOutputDevice(27)
PWM_pin = PWMOutputDevice(12)
right_wheel = Motor(forward_pin, backward_pin, PWM_pin)

forward_pin_2 = DigitalOutputDevice(23)
backward_pin_2 = DigitalOutputDevice(24)
PWM_pin_2 = PWMOutputDevice(13)
left_wheel = Motor(forward_pin_2, backward_pin_2, PWM_pin_2)

audio = Audio_processing(
    ["files/audio/KSHMR_Animals_12_Dog_A.wav"],
    ["files/audio/KSHMR_Animals_13_Dog_Growl.wav"],
)

angry_dog = Robot(left_wheel, right_wheel, audio)

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
