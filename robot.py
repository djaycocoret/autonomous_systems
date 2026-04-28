import json
import time
from time import sleep

from dummy_robot import (
    Dummy_audio,
    Dummy_camera,
    Dummy_distance_sensor,
    Dummy_motor,
    Webcam,
)
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
        The minimum distance between the robot and the object detected by the distance sensor
    verbose : bool
        True if you want stuff printed in the console
    """

    def __init__(
        self,
        left_motor,
        right_motor,
        audio_proc,
        vis_proc,
        distance_sensor,
        camera,
        verbose=False,
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
        verbose: bool
            Verbosity
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.audio = audio_proc
        self.visual_proc = vis_proc
        self.distance_sensor = distance_sensor
        self.camera = camera

        self.safety_distance = 0.2
        self.verbose = verbose

    @classmethod
    def from_config(cls, json_path):
        """
        Initialises the robot from a config file

        Parameters
        __________
        json_path: str
            The file path of the json file (e.g., 'gpio_settings.json)'
        """
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
    def dummy_config(cls, dummy_image, yolo_model, webcam=False):
        """Initialises the robot with dummy hardware abilities, giving one the capacity to run on device other than raspberry pi.

        Parameters
        __________
        dummy_image: str
            the path of the image used as input for the fake 'camera'
            note: will not be used when using webcam
        yolo_model: str
            the path of the yolo model that will be used
        webcam: bool
            True if you want to use your own webcam
        """
        right_motor = Dummy_motor("right")
        left_motor = Dummy_motor("left")

        distance_sensor = Dummy_distance_sensor(0.6)

        audio = Dummy_audio()

        visual_proc = Visual_processing(yolo_model)

        if webcam:
            camera = Webcam()
        else:
            camera = Dummy_camera(dummy_image)

        verbose = True

        return cls(
            left_motor,
            right_motor,
            audio,
            visual_proc,
            distance_sensor,
            camera,
            verbose,
        )

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
        """Method that locates cat and if found returns offset from center.

        Parameters
        __________
        frame: NDarray
            The image in which a cat has to be located

        Returns
        _______
        offset: float
            a scaled value [-0.5, 0.5] that signals how off center the cat is.
        found: bool
            True if a cat is found; False if no cat is found.
        """
        offset, found = self.visual_proc.locate_cat(frame)

        if self.verbose:
            print(f"offset: {offset}")

        return offset, found

    def perceive(self, frame, conf_threshold=0.8):
        df = self.visual_proc.perceive(frame)
        df_threshold = df[df["confidence"] >= conf_threshold]
        return df_threshold

    def capture_image(self):
        """Method to capture image from the camera

        Returns
        _______
        frame: NDarray
            the image captured by the camera"""
        frame = self.camera.capture()
        return frame

    def can_move_fwd(self):
        """Method that checks if it is safe to move forward

        Returns
        _______
        safe: bool
            True if can move forward; False if it cannot.
        """
        safe = self.distance_sensor.safe_distance(self.safety_distance)
        return safe

    def chase(self, offset):
        """Method for chasing

        Sets the wheels to forwards and calculates speed for the wheels to steer

        Parameters
        __________
        offset : float
            the offset from center [-0.5, 0.5]
        """

        value_left, value_right = 1, 1  # will be used for smoothing

        if offset > 0:
            self.left_motor.forward(value_left)
            self.right_motor.forward(value_right - offset)
        else:
            self.left_motor.forward(value_left - offset)
            self.right_motor.forward(value_right)

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
