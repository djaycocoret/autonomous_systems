import random
from enum import Enum, auto
from time import time

import pandas as pd

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
    def __init__(self, robot):
        self.robot = robot
        self.state = State.IDLE
        self.wander_state = Wander_state.START
        self.last_state_change = time()

        self.offset = 0

    @classmethod
    def from_config(cls, config_path):
        robot = Robot.from_config(config_path)
        return cls(robot)

    @classmethod
    def dummy_config(
        cls,
        dummy_img="files/test images/cat.jpg",
        webcam=False,
        yolo="yolo26n.pt",
        distance=0.2,
    ):
        robot = Robot.dummy_config(
            dummy_image=dummy_img,
            yolo_model="yolo26n.pt",
            webcam=webcam,
            distance=0.1,
        )
        return cls(robot)

    def stop(self):
        self.robot.stop(stop_cam=True)

    def update(self, verbose=False):
        frame = self.robot.capture_image()
        df = self.robot.perceive(frame)
        safe = self.robot.can_move_fwd()

        self._state_logic(df, safe)
        if verbose:
            print(f"Current State: {self.state}")

        self.execute_behaviour(self.offset)

    def _state_logic(self, df, safe):
        found = self.class_in_frame(df, "cat")
        if not safe:
            self.state = State.BLOCKED
            return

        if self.state == State.BLOCKED and found:
            self.state = State.BARKING

        if self.state == State.BLOCKED and safe:
            self.state = State.IDLE

        elif self.state == State.IDLE and not found:
            self.state = State.SEARCHING

        elif found:
            self.state = State.CHASING

        elif self.state == State.CHASING and not found:
            self.state = State.SEARCHING

    def execute_behaviour(self, offset):
        if self.state == State.IDLE:
            self.robot.stop()

        elif self.state == State.CHASING:
            self.last_state_change = time()
            self.robot.chase(self.offset)

<<<<<<< HEAD
        elif self.state == State.BARKING:
            self.robot.bark()
=======
        elif self.state == State.LOST_TARGET:
            left_speed, right_speed = self.robot.return_motor_speeds()
            left_speed = left_speed - 0.05
            right_speed = right_speed - 0.05
            self.robot.forward([left_speed, right_speed])

        elif self.state == State.SEARCHING:
            if (
                self.wander_state == Wander_state.START
                or time() - self.last_state_change > 2
            ):
                possible_states = list(Wander_state)[1:]  # excludes start state
                self.wander_state = random.choice(possible_states)
                self.last_state_change = time()

            if self.wander_state == Wander_state.TURN_LEFT:
                self.robot.turn("L", 0.4)
            elif self.wander_state == Wander_state.TURN_RIGHT:
                self.robot.turn("R", 0.4)
            elif self.wander_state == Wander_state.FORWARD:
                self.robot.forward(0.4)
            elif self.wander_state == Wander_state.BACKWARD:
                self.robot.backward(0.4)
            elif self.wander_state == Wander_state.SPIN:
                left = int(bool(random.random() > 0.5))
                direction = ["L", "R"][left]
                self.robot.spin(direction, 0.4)
            elif self.wander_state == Wander_state.STOP:
                self.robot.stop()
>>>>>>> 318919d7cfe341a63b847a218bd5fc52dbd15b8b

        if self.state == State.BLOCKED:
            self.robot.stop()
            if time() - self.last_state_change > 2:
                self.robot.growl()
                self.last_state_change = time()

    def class_in_frame(self, df, class_: str):
        return df["class"].str.contains(class_).any()

    def class_offset(self, df, class_: str):
        if self.class_in_frame(df, class_):
            return df[df["class"] == class_][0]
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
