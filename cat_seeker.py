angry_dog = Robot.from_config("gpio_settings.json")

try:
    while True:
        # the perception action loop goes here.
        frame = angry_dog.capture_image()
        offset, found = angry_dog.locate_cat(frame)
        print(offset, found)

except KeyboardInterrupt:
    angry_dog.stop(stop_cam=True)
