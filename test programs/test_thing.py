import cv2
from ultralytics import YOLO


class Visual_processing:
    """A class representing the visual processing

    Attributes
    __________
    model : ultralytics.models.yolo.model.YOLO
        The model that will classify the images.
    """

    def __init__(self, model):
        """Initialises the visual processing class"""
        self.model = YOLO(model)
        print(type(self.model))

    def locate_cat(self, input):
        """Locates a cat, if found,

        Parameters
        __________
        input : np.array
            The captured image as a numpy array

        Returns
        _______
        offset : float [-1, 1] or None
            KKKKKKK
        """

        h_img, w_img, _ = input.shape

        results = self.model.predict(input)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                cls = result.names[cls_id]
                x, y, _, _ = box.xywh[0]
                print(f"{cls} at ({x}, {y})")
                if cls == "cat":
                    offset = float((x - w_img / 2) / w_img)
                    return offset
                else:
                    continue
        return None


vs = Visual_processing("yolo26n.pt")

img = cv2.imread("files/cat.jpg")
print(vs.locate_cat(img))
