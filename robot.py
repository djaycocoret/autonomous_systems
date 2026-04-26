import json
import time
from time import sleep

from dummy_robot import Dummy_audio, Dummy_camera, Dummy_distance_sensor, Dummy_motor
from helper_functions import get_wav_files
from visual_processing import Visual_processing


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
    camera : Camera
        The camera sensor of the robot
    safety_distance : float
        The minimum distance between the robot and the object detected by the distance senser
    """

    def __init__(
        self, left_motor, right_motor, audio_proc, vis_proc, distance_sensor, camera
    ):
        """Initialises the robot

        Parameters
        __________
        left motor : Wheel
            The left motor of the robot, oriented with the raspberry facing forwards
        right motor : Wheel
            The right motor of the robot, oriented with the raspberry facing forwards
        audio : Audio_processing
            The audio interface of the robot.
        visual_processing : Visual_processing
            The visual processing part of the robot.
        distance_sensor : Distance_sensor
            The depth measuring capabilities of the robot.
        camera : Camera
            The camera of the robot.

        TO BE CONTINUED
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.audio = audio_proc
        self.visual_proc = vis_proc
        self.distance_sensor = distance_sensor
        self.camera = camera

        self.safety_distance = 0.2

    @classmethod
    def from_config(cls, json_path):
        # imports inside the config because otherwise it does not run on laptops
        from camera import Camera
        from sensors_actuator_wrappers import Audio_processing, Distance_sensor, Motor

        with open(json_path, "r") as file:
            gpio_settings = json.load(file)

        right_motor = Motor(
            gpio_settings["forward_pin_right"],
            gpio_settings["backward_pin_right"],
            gpio_settings["enable_pin_right"],
        )

        left_motor = Motor(
            gpio_settings["forward_pin_left"],
            gpio_settings["backward_pin_left"],
            gpio_settings["enable_pin_left"],
        )

        distance_sensor = Distance_sensor(
            gpio_settings["distance_trigger_pin"], gpio_settings["distance_echo_pin"]
        )

        barks = get_wav_files(gpio_settings["bark_dir"])
        growls = get_wav_files(gpio_settings["growl_dir"])
        audio = Audio_processing(barks, growls)

        visual_proc = Visual_processing(gpio_settings["yolo_model"])

        camera = Camera()

        return cls(left_motor, right_motor, audio, visual_proc, distance_sensor, camera)

    @classmethod
    def dummy_config(cls, dummy_image, yolo_model):
        right_motor = Dummy_motor("right")
        left_motor = Dummy_motor("left")

        distance_sensor = Dummy_distance_sensor(0.6)

        audio = Dummy_audio()

        visual_proc = Visual_processing(yolo_model)

        camera = Dummy_camera(dummy_image)

        return cls(left_motor, right_motor, audio, visual_proc, distance_sensor, camera)

    def return_motors(self) -> list:
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

    def stop(self, stop_cam=False):
        """Changes the state of the robot to stopped"""
        for motor in self.return_motors():
            motor.stop()

        if stop_cam:
            self.camera.stop()

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

    def locate_cat(self, frame):
        offset, found = self.visual_proc.locate_cat(frame)
        return offset, found

    def capture_image(self):
        frame = self.camera.capture()
        return frame

    def can_move_fwd(self):
        return self.distance_sensor.safe_distance(self.safety_distance)

    ######

    def slowing_down(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (end - time.time()) / duration
            for motor in self.return_motors():
                motor.forward(speed=max_speed * ratio)

    def speeding_up(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (start + time.time()) / duration
            for motor in self.return_motors():
                motor.forward(speed=max_speed * ratio)

    def turning_forward_left(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (start + time.time()) / duration
            self.left_motor.forward(speed=max * ratio)

    def turning_forward_right(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (start + time.time()) / duration
            self.right_motor.forward(speed=max * ratio)

    def turning_backwards_left(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (start + time.time()) / duration
            self.left_motor.backward(speed=max * ratio)

    def turning_backwards_right(self, duration, min_speed=0, max_speed=1):
        start = time.time()
        end = start + duration
        while time.time() < end:
            ratio = (start + time.time()) / duration
            self.right_motor.backward(speed=max * ratio)


if __name__ == "__main__":
    print("this contains only class definitions. to run the robot run something else")

    bitch = Robot.dummy_config(
        dummy_image="/home/group3/autonomous_systems/files/test images/cat.jpg",
        yolo_model="/home/group3/autonomous_systems/yolo26n.pt",
    )

    bitch.forward()
