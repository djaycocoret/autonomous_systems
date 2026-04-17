import cv2 as cv
import numpy as np

from visual_processing import Visual_processing

ventral_Stream = Visual_processing("yolo26n.pt")

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    print(ventral_Stream.locate_cat(gray))

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
