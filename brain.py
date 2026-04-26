from enum import Enum, auto
from time import time

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
        offset, found = self.robot.locate_cat(frame)
        safe = self.robot.can_move_fwd()

        self._state_logic(offset, found, safe)
        if verbose:
            print(f"Current State: {self.state}")
        self.execute_behaviour(offset)

    def _state_logic(self, offset, found, safe):
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

        # your states here

    def execute_behaviour(self, offset):
        # your behaviour here
        #
        if self.state == State.IDLE:
            self.robot.stop()

        elif self.state == State.SEARCHING:
            self.robot.spin("R", duration=0.1)

        if self.state == State.BLOCKED:
            self.robot.stop()
            if time() - self.last_state_change > 2:
                self.robot.growl()
                self.last_state_change = time()


if __name__ == "__main__":
    # brain = Brain.from_config("gpio_settings.json")
    brain = Brain.dummy_config()

    try:
        while True:
            brain.update()

    except KeyboardInterrupt:
        brain.stop()
