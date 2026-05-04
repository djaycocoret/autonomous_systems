import json
import random
from enum import Enum, auto
from time import time

import pandas as pd

from helper_functions import softmax
from robot import Robot


class State(Enum):
    IDLE = auto()
    SEARCHING = auto()
    CHASING = auto()
    BARKING = auto()
    BLOCKED = auto()
    LOST_TARGET = auto()


class Wander_state(Enum):
    START = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    SPIN = auto()
    STOP = auto()


class Brain:
    def __init__(self, robot, learning_rate):
        self.robot = robot
        self.state = State.IDLE
        self.wander_state = Wander_state.START
        self.wander_state_probs = [random.random() for _ in range(1, len(Wander_state))]
        self.last_state_change = time()
        self.learning_rate = learning_rate
        self.state_duration_change = 2

        self.offset = 0

    @classmethod
    def from_config(cls, config_path):
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
        robot = Robot.dummy_config(
            dummy_image=dummy_img,
            yolo_model=yolo,
            webcam=webcam,
            distance=distance,
        )
        return cls(robot, learning_rate)

    def stop(self):
        self.robot.stop(stop_cam=True)

    def update(self, verbose=False):
        frame = self.robot.capture_image()
        df = self.robot.perceive(frame, conf_threshold=0.6)
        safe = self.robot.can_move_fwd()

        self._state_logic(df, safe)
        if verbose:
            print(f"Current State: {self.state}")
            print(f"Wander State: {self.wander_state}")
            # print(f"Pdf: {softmax(self.wander_state_probs)}") #maybe a bit cpu intens

        self.execute_behaviour(self.offset)

    def _state_logic(self, df, safe):
        found = self.class_in_frame(df, "cat")

        print(found)
        if not safe:
            self.state = State.BLOCKED
            return

        if self.state == State.BLOCKED and found:
            self.state = State.BARKING

        if self.state == State.BLOCKED and safe:
            self.state = State.IDLE

        if (
            self.state == State.LOST_TARGET
            and not found
            and time() - self.state_duration_change > self.last_state_change
        ):
            self.state = State.SEARCHING

        elif self.state == State.IDLE and not found:
            self.state = State.SEARCHING

        elif self.state == State.SEARCHING and found:
            wander_states = list(Wander_state)
            if self.wander_state != Wander_state.START:
                state_in_which_found = (
                    wander_states.index(self.wander_state) - 1
                )  # exclude start state
                self.wander_state_probs[state_in_which_found] += self.learning_rate
            self.state = State.CHASING
            self.last_state_change = time()

        elif self.state == State.CHASING and not found:
            self.state = State.LOST_TARGET

        elif found:
            self.offset = self.class_offset(df, "cat")
            print(self.offset)
            self.state = State.CHASING

        elif self.state == State.CHASING and not found:
            self.state = State.SEARCHING

    def execute_behaviour(self, offset):
        if self.state == State.IDLE:
            self.robot.stop()

        elif self.state == State.CHASING:
            self.last_state_change = time()
            self.robot.chase(self.offset)

        elif self.state == State.BARKING:
            self.robot.bark()

        elif self.state == State.LOST_TARGET:
            left_speed, right_speed = self.robot.return_motor_speeds()
            left_speed = left_speed - 0.05
            right_speed = right_speed - 0.05
            self.robot.forward([left_speed, right_speed])

        elif self.state == State.SEARCHING:
            if (
                self.wander_state == Wander_state.START
                or time() - self.last_state_change > self.state_duration_change
            ):
                possible_states = list(Wander_state)[1:]  # excludes start state
                self.wander_state = random.choices(
                    possible_states, weights=softmax(self.wander_state_probs)
                )[0]
                self.last_state_change = time()

            if self.wander_state == Wander_state.TURN_LEFT:
                self.robot.turn("L", 0.65)
            elif self.wander_state == Wander_state.TURN_RIGHT:
                self.robot.turn("R", 0.65)
            elif self.wander_state == Wander_state.FORWARD:
                self.robot.forward(0.65)
            elif self.wander_state == Wander_state.BACKWARD:
                self.robot.backward(0.65)
            elif self.wander_state == Wander_state.SPIN:
                right = int(random.random() > 0.5)
                direction = ["L", "R"][right]
                self.robot.spin(direction, 0.4)
            elif self.wander_state == Wander_state.STOP:
                self.robot.stop()

        elif self.state == State.BLOCKED:
            BACK_CLEAR = True

            if time() - self.last_state_change > self.state_duration_change:
                self.robot.growl()
                self.last_state_change = time()
                if BACK_CLEAR:
                    self.robot.backward(0.6)

    def class_in_frame(self, df, class_: str):
        return df["class"].str.contains(class_).any()

    def class_offset(self, df, class_: str):
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
