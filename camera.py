import cv2
from picamera2 import Picamera2


class Camera:
    def __init__(self) -> None:
        self.cam = Picamera2()
        config = self.cam.create_still_configuration(
            main={"format": "RGB888", "size": (1280, 720)}
        )
        self.cam.configure(config)
        self.cam.start()

    def capture(self, file_name=None):
        frame = self.cam.capture_array()

        frame_rotate = cv2.flip(frame, -1)

        if file_name:
            cv2.imwrite(f"{file_name}.jpg", frame_rotate)

        return frame_rotate

    def stop(self):
        self.cam.stop()
