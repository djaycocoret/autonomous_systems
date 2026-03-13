from time import sleep

from gpiozero import DigitalOutputDevice

# Define pins to match your Arduino variables
forward_pin = DigitalOutputDevice(17)
backward_pin = DigitalOutputDevice(27)
forward_pin_2 = DigitalOutputDevice(23)
backward_pin_2 = DigitalOutputDevice(24)
delay_time = 2.0  # seconds

try:
    while True:
        # Stop
        forward_pin.off()
        backward_pin.off()
        forward_pin_2.off()
        backward_pin_2.off()
        print("Stop")
        sleep(delay_time)

        # Spin Forward
        forward_pin.on()
        backward_pin.off()
        forward_pin_2.on()
        backward_pin_2.off()
        print("Forward")
        sleep(delay_time)

        # Stop
        forward_pin.off()
        backward_pin.off()
        forward_pin_2.off()
        backward_pin_2.off()
        print("Stop")
        sleep(delay_time)

        # Spin Backward
        forward_pin.off()
        backward_pin.on()
        forward_pin_2.off()
        backward_pin_2.on()
        print("Backward")
        sleep(delay_time)

except KeyboardInterrupt:
    # Clean exit if you press Ctrl+C
    forward_pin.off()
    backward_pin.off()
    forward_pin_2.off()
    backward_pin_2.off()
