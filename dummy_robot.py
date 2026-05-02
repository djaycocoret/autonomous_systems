import cv2


class Dummy_motor:
    """A class representing a motor, which does not require hardware

    The class prints updates by printing commands to the console.
    This class uses the same structure as the other motor class.

    Parameters
    __________
    name: str
        the name of the motor (e.g., right_wheel)"""

    def __init__(self, name):
        self.name = name
        self.speed = 0

    def forward(self, speed=1):
        self.speed = speed
        print(f"{self.name} Motor speed: {speed}")

    def stop(self):
        print(f"{self.name} Motor: stopped")

    def backward(self, speed=1):
        self.speed = speed
        print(f"{self.name} Motor speed: {-speed}")


class Dummy_distance_sensor:
    def __init__(self, distance=1.0):
        self.distance = distance

    def safe_distance(self, safe_distance):
        print(f"simulated distance: {self.distance}, {self.distance > safe_distance}")
        return self.distance > safe_distance


class Dummy_audio:
    def __init__(self):
        pass

    def bark(self):
        print("bark")

    def growl(self):
        print("growl")


class Dummy_camera:
    def __init__(self, img_path):
        self.img_path = img_path
        self.img = cv2.imread(img_path)

    def capture(self, file_name=None):
        print(f"captured image: {self.img_path}")
        return self.img

    def stop(self):
        print("camera stopped")


class Webcam:
    def __init__(self) -> None:
        self.cam = cv2.VideoCapture(0)

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cam.isOpened():
            raise RuntimeError("Could not open webcam.")

    def capture(self, file_name=None):
        ret, frame = self.cam.read()

        if not ret:
            print("Failed to grab frame")
            return None

        if file_name:
            cv2.imwrite(f"{file_name}.jpg", frame)

        return frame

    def stop(self):
        self.cam.release()
