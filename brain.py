from enum import Enum, auto
from time import time

import pandas as pd

from robot import Robot


class State(Enum):
    IDLE = auto()
    SEARCHING = auto()
    CHASING = auto()
    BLOCKED = auto()


class Brain:
    def __init__(self, robot):
        self.robot = robot
        self.state = State.IDLE
        self.last_state_change = time()

        self.offset = 0

    @classmethod
    def from_config(cls, config_path):
        robot = Robot.from_config(config_path)
        return cls(robot)

    @classmethod
    def dummy_config(cls, webcam):
        robot = Robot.dummy_config(
            dummy_image="files/test images/cat.jpg",
            yolo_model="yolo26n.pt",
            webcam=webcam,
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

        elif self.state == State.SEARCHING:
            self.robot.spin("R", duration=0.1)

        elif self.state == State.CHASING:
            self.robot.chase(self.offset)

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
    # brain = Brain.from_config("gpio_settings.json")
    brain = Brain.dummy_config(webcam=False)

    try:
        while True:
            brain.update(verbose=True)

    except KeyboardInterrupt:
        brain.stop()
