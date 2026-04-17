from ultralytics import YOLO


class Visual_processing:
    """A class representing the visual processing

    Attributes
    __________
    model : ultralytics.models.yolo.model.YOLO
        The model that will classify the images.
    confidence_threshold : float [0, 1]
        The threshold that will have to for the system to act on the classification.
    """

    def __init__(self, model, confidence_threshold=0.8):
        """Initialises the visual processing class"""
        self.model = YOLO(model)
        self.confidence_threshold = confidence_threshold

    def locate_cat(self, input):
        """Locates a cat, if found, returns a scaled value how off centre the target is.

        Parameters
        __________
        input : np.array
            The captured image as a numpy array

        Returns
        _______
        offset : float [-0.5, 0.5]
            idk how to describe it yet.
            0 can be 0 offset of nothing in image
        """

        h_img, w_img, _ = input.shape

        results = self.model.predict(input)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                cls = result.names[cls_id]
                x, y, _, _ = box.xywh[0]
                print(f"{cls} at ({x}, {y}), with confidence {box.conf[0]}")
                if cls == "cat":
                    offset = float((x - w_img / 2) / w_img)
                    return offset
                else:
                    continue
        return 0
