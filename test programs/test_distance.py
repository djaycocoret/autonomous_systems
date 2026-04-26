from time import sleep

from gpiozero import DistanceSensor

sensor = DistanceSensor(5, 6)

print(sensor.distance)
print(dir(sensor))
