import cv2
import pandas as pd
from ultralytics import YOLO


class Visual_processing:
    """
    A class representing the visual processing

    Attributes
    __________
    model : ultralytics.models.yolo.model.YOLO
        The model that will classify the images.
    confidence_threshold : float [0, 1]
        The threshold that will have to for the system to act on the classification.
    """

    def __init__(self, model, confidence_threshold=0.8):
        """
        Initialises the visual processing class

        Parameters
        __________
        model : string
            The path of the model that will classify the images.
        confidence_threshold : float [0, 1]
            The threshold that will have to for the system to act on the classification.
        """
        self.model = YOLO(model)
        self.confidence_threshold = confidence_threshold

    def perceive(self, input):
        """R
        uns YOLO and outputs dataframe of found classes.

        Parameters
        __________
        input : np.array
            The captured image as a numpy array

        Returns
        _______
        df : pandas.DataFrame
            A dataframe containing the object which have been captured by the object detection model

            * 'class' : the class of the detected object, in string format
            * 'confidence' : the assigned probability to the detection
            * 'x' : the x position of the centre of the detected object
            * 'y' : the y position of the centre of the detected object
            * 'offset' : the scaled offset from the centre of the camera frame to the centre of the detected object
        """

        _, w_img, _ = input.shape

        results = self.model.predict(input)

        frame = list()

        for result in results:
            boxes = result.boxes
            for box in boxes:
                row = dict()
                cls_id = int(box.cls[0])
                cls = result.names[cls_id]
                x, y, _, _ = box.xywh[0]
                row["class"] = result.names[cls_id]
                row["confidence"] = float(box.conf[0])
                row["x"], row["y"] = float(x), float(y)
                row["offset"] = float((x - w_img / 2) / w_img)

                frame.append(row)

                if box.conf[0] >= self.confidence_threshold:
                    print(f"{cls} at ({x}, {y}), with confidence {box.conf[0]}")

        df = pd.DataFrame(frame, columns=["class", "confidence", "x", "y", "offset"])

        return df


if __name__ == "__main__":
    img = cv2.imread("test.jpg")

    v = Visual_processing("yolo26n.pt")

    df = v.perceive(img)

    print(df)
