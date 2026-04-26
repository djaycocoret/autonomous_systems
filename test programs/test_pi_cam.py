import cv2
import numpy as np
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"format": "RGB888", "size": (1280, 720)}
)
picam2.configure(config)
picam2.start()

frame = picam2.capture_array()

cv2.imwrite("headless_capture.jpg", frame)

print("Frame captured and saved as headless_capture.jpg")

picam2.stop()
