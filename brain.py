import json
import random
from enum import Enum, auto
from time import time

import pandas as pd

from helper_functions import softmax
from robot import Robot


class State(Enum):
    IDLE = auto()
    WANDERING = auto()
    CHASING = auto()
    BARKING = auto()
    BLOCKED = auto()
    TARGETTING = auto()
    LOST_TARGET = auto()


class Wander_state(Enum):
    START = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    SPIN = auto()


class Brain:
    """
    A class representing the brain of the robot for the Autonomous Systems course 2026.

    The Brain class represents the controller part of the robot.
    The class is responsible for perception, state changes, and executing behaviour.

    Attributes
    __________
    robot : Robot
        The robot (body) that the brain is controlling
    state : State
        The current state of the robot
    wander_state : Wander_state
        The current wander state
    wander_state_probs : list[float]
        A list of floating point decimals that contain logits which corresponds to most wandering states
    last_state_change : time.time()
        The last time when a state change was updated (inconsitent: does not update with every state change)
    learning_rate : float
        The learning rate of the brain; used to update the wander_state_probs
    state_duration_change : float
        How long is will take for it to stay in a certain state (wandering behaviour)
    target_in_centre : bool
        Boolean that returns if the target is in the centre of the frame
    """

    def __init__(self, robot, learning_rate):
        """
        Initialises the brain

        Parameters
        __________
        robot : Robot
            The robot (body) that the brain is controlling
        learning_rate : float
             The learning rate of the brain; used to update the wander_state_probs
        """
        self.robot = robot
        self.state = State.IDLE
        self.wander_state = Wander_state.START
        self.wander_state_probs = [random.random() for _ in range(1, len(Wander_state))]
        self.last_state_change = time()
        self.learning_rate = learning_rate
        self.state_duration_change = 1.5
        self.target_in_centre = False

    @classmethod
    def from_config(cls, config_path):
        """
        Initialeses the brain from a configuration file

        Parameters
        __________
        config_path : string
            The path to the json file in which the gpio and settings are described

        Returns
        _______
        cls : Brain
            A preconfigured brain class
        """
        robot = Robot.from_config(config_path)

        with open(config_path, "r") as file:
            config = json.load(file)
        learning_rate = config["learning_rate"]
        return cls(robot, learning_rate)

    @classmethod
    def dummy_config(
        cls,
        dummy_img="files/test images/cat.jpg",
        webcam=False,
        yolo="yolo26n.pt",
        distance=0.2,
        learning_rate=0.05,
    ):
        """
        Initialises the brain with a dummy configuration, capable of running on non gpio devices

        Parameters
        __________
        dummy_img : string
            An image that will be used to simulate the camera of the brain
        webcam: bool
            True iff you want to use your webcam as camera input for the dummy brain
        yolo : string
            Path containing the yolo model which will be used for inference
        distance : float
            The simulated distance the distance sensor picks up

        Returns
        _______
        cls : Brain
            A dummy configured brain
        """
        robot = Robot.dummy_config(
            dummy_image=dummy_img,
            yolo_model=yolo,
            webcam=webcam,
            distance=distance,
        )
        return cls(robot, learning_rate)

    def stop(self):
        """
        A method that stops the brain entirely, also saves weights to a json file"""
        self.robot.stop(stop_cam=True)
        self.save_weights("files/data/weights.json")

    def load_weights(self, path):
        """
        A method that load the weights from a json file

        Parameters
        __________
        path : string
            The path containing the json file
        """
        with open(path, "r") as file:
            weights = json.load(file)
        if len(weights) == len(Wander_state) - 1:
            self.wander_state_probs = list(weights)
        else:
            print("wrong size")

    def save_weights(self, path):
        """
        A method that save the weights to a json file

        Parameters
        __________
        path : string
            The path containing the json file
        """
        with open(path, "w") as file:
            json.dump(self.wander_state_probs, file)

    def update(self, verbose=False):
        """
        Method for the perception - action cycle

        Parameters
        __________
        Verbose : bool
            True iff you want to see in what states the bot is, by default False for easier programming
        """
        df, safe = self._perceive()

        self._state_logic(df, safe)

        if verbose:
            print(f"Current State: {self.state}")
            print(f"Wander State: {self.wander_state}")

        self._execute_behaviour(df)

    def _perceive(self):
        """
        The method that is responsible for capturing the external environment

        Returns
        _______
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        safe : bool
            True iff captured distance greater than safe distance (when nothing is in front)
        """
        frame = self.robot.capture_image()
        df = self.robot.perceive(frame, conf_threshold=0.6)
        safe = self.robot.can_move_fwd()

        return df, safe

    def _state_logic(self, df, safe):
        """
        A method for transitioning to the right states.

        [full explanation here]

        Parameters
        __________
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        safe : bool
            True iff captured distance greater than safe distance (when nothing is in front)
        """
        found = self.class_in_frame(df, "cat")

        print(found)
        if not safe:
            self.state = State.BLOCKED
            return

        if self.state == State.BLOCKED and found:
            self.state = State.BARKING

        elif self.state == State.BLOCKED and safe:
            self.state = State.IDLE

        elif self.state == State.IDLE and found and not self.target_in_centre:
            self.state = State.TARGETTING

        elif self.state == State.TARGETTING and self.target_in_centre:
            self.state = State.CHASING

        elif (
            self.state == State.LOST_TARGET
            and not found
            and time() - self.state_duration_change > self.last_state_change
        ):
            self.state = State.WANDERING

        elif (
            self.state == State.IDLE
            and not found
            and time() - self.state_duration_change > self.last_state_change
        ):
            self.state = State.WANDERING
            self.last_state_change = time()

        elif self.state == State.WANDERING and found:
            self.state = State.TARGETTING
            self.last_state_change = time()

        elif self.state == State.IDLE and found:
            # wander_states = list(Wander_state)
            # if self.wander_state != Wander_state.START:
            #     state_in_which_found = (
            #         wander_states.index(self.wander_state) - 1
            #     )  # exclude start state
            #     self.wander_state_probs[state_in_which_found] += self.learning_rate
            self.state = State.CHASING
            self.last_state_change = time()

        elif self.state == State.CHASING and not found:
            self.state = State.LOST_TARGET

        elif found:
            self.offset = self.class_offset(df, "cat")
            print(self.offset)
            self.state = State.CHASING

        elif self.state == State.CHASING and not found:
            self.state = State.WANDERING

    def _execute_behaviour(self, df):
        """
        Method that executes the behaviour based on the current state (state is an implicit parameter)

        Parameters
        __________
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        """
        if self.state == State.IDLE:
            self.robot.stop()
            self.wander_state = Wander_state.START

        elif self.state == State.CHASING:
            self.last_state_change = time()
            offset = self.class_offset(df, "cat")
            self.robot.chase(offset)

        elif self.state == State.BARKING:
            self.robot.growl()

        elif self.state == State.LOST_TARGET:
            self.robot.bark()
            left_speed, right_speed = self.robot.return_motor_speeds()
            self.robot.forward([left_speed, right_speed])

        elif self.state == State.TARGETTING:
            offset = self.class_offset(df, "cat")
            if offset < 0:
                self.robot.spin("L", 0.8)
            else:
                self.robot.spin("R", 0.8)

            if abs(offset) < 0.05:
                self.target_in_centre = True
            else:
                self.target_in_centre = False

        elif self.state == State.WANDERING:
            if time() - self.last_state_change > self.state_duration_change:
                self.state = State.IDLE
                self.last_state_change = time()
                return

            if self.wander_state == Wander_state.START:
                possible_states = list(Wander_state)[1:]  # excludes start state
                self.wander_state = random.choices(
                    possible_states, weights=softmax(self.wander_state_probs)
                )[0]
                self.last_state_change = time()

            if self.wander_state == Wander_state.TURN_LEFT:
                self.robot.turn("L", 0.95)
            elif self.wander_state == Wander_state.TURN_RIGHT:
                self.robot.turn("R", 0.95)
            elif self.wander_state == Wander_state.FORWARD:
                self.robot.forward(0.95)
            elif self.wander_state == Wander_state.BACKWARD:
                self.robot.backward(0.95)
            elif self.wander_state == Wander_state.SPIN:
                right = int(random.random() > 0.5)
                direction = ["L", "R"][right]
                self.robot.spin(direction, 0.8)
            elif self.wander_state == Wander_state.STOP:
                self.robot.stop()

        elif self.state == State.BLOCKED:
            if time() - self.last_state_change > self.state_duration_change:
                self.robot.growl()
                self.last_state_change = time()
                self.robot.backward(0.6)

    def class_in_frame(self, df, class_: str):
        """
        A method that return iff there is an object of a prespecified class in the dataframe.

        Parameters
        __________
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        class_ : str
            The class which will be detected

        Returns
        _______
        value : bool
            True iff there is a class_ in the dataframe
        """

        value = df["class"].str.contains(class_).any()

        return value

    def class_offset(self, df, class_: str):
        """
        A method that returns the offset of the first object of a prespecified class in the dataframe.

        Parameters
        __________
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        class_ : str
            The class which will be detected

        Returns
        _______
        offset : float
            The offset of the first row containing that class
        """
        if self.class_in_frame(df, class_):
            return float(df[df["class"] == class_].iloc[0]["offset"])
        else:
            return 0


if __name__ == "__main__":
    brain = Brain.from_config("gpio_settings.json")
    # brain = Brain.dummy_config(webcam=False)

    try:
        while True:
            brain.update(verbose=True)

    except KeyboardInterrupt:
        brain.stop()
