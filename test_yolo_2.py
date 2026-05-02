from camera import Camera
from visual_processing import Visual_processing

c = Camera()

vp = Visual_processing("yolo26n.pt")

frame = c.capture()

df = vp.perceive(frame)

print(df)
