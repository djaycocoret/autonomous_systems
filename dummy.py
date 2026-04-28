from brain import Brain

simulated_distance = 0.1
use_webcam = False
dummy_image = "files/test images/cat.jpg"
yolo_model = "yolo26n.pt"

brain = Brain.dummy_config(
    webcam=use_webcam,
    dummy_img=dummy_image,
    yolo="yolo26n.pt",
    distance=simulated_distance,
)

if __name__ == "__main__":
    try:
        while True:
            brain.update(verbose=True)

    except KeyboardInterrupt:
        brain.stop()
