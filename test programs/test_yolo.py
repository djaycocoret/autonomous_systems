import cv2
from ultralytics import YOLO

print("starting")

model = YOLO("yolo26n.pt")

img = cv2.imread("./files/cat.jpg")
h, w, _ = img.shape


results = model.predict("./files/cat.jpg")

predictions = list()
for result in results:
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]

        start_point = (int(x1), int(y1))
        end_point = (int(x2), int(y2))

        conf = box.conf[0]
        cls_id = int(box.cls[0])
        cls_name = result.names[cls_id]
        print(
            f"Detected {cls_name} with confidence {conf:.2f} at ({x1}, {y1}) to ({x2}, {y2})"
        )

        cv2.rectangle(img, start_point, end_point, color=(0, 0, 0), thickness=1)
        cv2.putText(
            img,
            cls_name,
            (int(x1), int(y1) - 10),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.6,
            color=(255, 255, 255),
            thickness=2,
        )

        cv2.imwrite("example.jpg", img)
