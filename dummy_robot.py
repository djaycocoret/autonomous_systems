import cv2


class Dummy_motor:
    def __init__(self, name):
        self.name = name

    def forward(self, speed=1):
        print(f"{self.name} Motor: going forward. Speed: {speed}")

    def stop(self):
        print(f"{self.name} Motor: stopped")

    def backward(self, speed=1):
        print(f"{self.name} Motor: going backward. Speed: {speed}")


class Dummy_distance_sensor:
    def __init__(self, distance=1.0):
        self.distance = distance

    def safe_distance(self, safe_distance):
        print(f"simulated distance: {self.distance}")
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
