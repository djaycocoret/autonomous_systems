from robot import *

# ugly test code
# very old and maybe not working anymore. lol sorry

forward_pin = 17
backward_pin = 27
PWM_pin = 12
right_wheel = Motor(forward_pin, backward_pin, PWM_pin)

forward_pin_2 = 23
backward_pin_2 = 24
PWM_pin_2 = 13
left_wheel = Motor(forward_pin_2, backward_pin_2, PWM_pin_2)

audio = Audio_processing(
    ["files/audio/KSHMR_Animals_12_Dog_A.wav"],
    ["files/audio/KSHMR_Animals_13_Dog_Growl.wav"],
)

visual_processing = Visual_processing("yolo26n.pt")

dis_sensor = Distance_sensor(5, 6)

c = Camera()

angry_dog = Robot(left_wheel, right_wheel, audio, visual_processing, dis_sensor, c)
